"""Input: abstract syntax tree -- Output: (transformed) abstract syntax tree.

The transform step is essential for the processing of the manuscript.  For exmaple,
references and citations are resolved during this time.

The transform step is also responsible for 'fixing up' some syntactic sugar afforded by
RSM markup to yield a sound manuscript.  For exmaple, for mathematical proofs, it is
possible to have a sequence of ``:step:`` tags inside a parent ``:step:``.  However, in
the final manuscript, those sub-steps will be wrapped by a :class:`rsm.nodes.SubProof`
node, without the user having to manually create a ``:p:`` tag.  This wrapper node is
created during the transform step.

After the transform step, static analysis tools such as the linter may run over the
manuscript.

The convention is that the manuscript will not be modified for any reason after the
transform step is done.  **This is currently not enforced**, but merely a convention,
though it must at all times be followed.

The transform step is carried out by :class:`Transformer`, which simply executes in
sequence a number of routines that are all independent from each other.  Since the task
of each such routine is to modify the manuscript tree, the order in which they take
place is of utmost importance.

"""

import logging
from collections import defaultdict
from itertools import count
from string import ascii_uppercase
from typing import Generator, Optional, Type

from icecream import ic

from . import nodes

logger = logging.getLogger("RSM").getChild("tform")


class RSMTransformerError(Exception):
    pass


class Transformer:
    """Apply transformations to the abstract syntax tree.

    A transformation is any operation on the manuscript tree that modifies its
    structure.  This class keeps a register of transformations and applies them in
    sequence.  Order of application is of the utmost importance since each transform
    modifies the tree in some way.

    Notes
    -----
    If an operation is being carried out not to transform the tree, but merely to check
    it in some way, consider implementing it as a linter operation instead.

    Examples
    --------
    Consider the following manuscript.

    >>> src = \"\"\"
    ... :rsm:
    ... Here comes a :span:{:label:lbl} word :: with a label,
    ... and a reference to the :ref:lbl,word::.
    ... ::
    ... \"\"\"

    The transform step comes after the parsing step.  After parsing, the manuscript
    looks as follows.

    >>> parser = rsm.tsparser.TSParser()
    >>> sans_transform = parser.parse(src)
    >>> print(sans_transform.sexp())
    (Manuscript
      (Paragraph
        (Text)
        (Span
          (Text))
        (Text)
        (PendingReference)
        (Text)))

    The :class:`rsm.nodes.PendingReference` node is created as a placeholder.  One can
    inspect its desired target.

    >>> sans_transform.children[0].children[3].target
    'lbl'

    The target is the string ``'lbl'``.  Note this is the label of the target node.

    After the transform step, the tree is modified and the reference is resolved.

    >>> tform = rsm.transformer.Transformer()
    >>> with_transform = tform.transform(sans_transform)
    >>> print(with_transform.sexp())
    (Manuscript
      (Paragraph
        (Text)
        (Span
          (Text))
        (Text)
        (Reference)
        (Text)))

    Accordingly, its target is now no longer a string, but the actual node.

    >>> with_transform.children[0].children[3].target
    Span(label=lbl, parent=Paragraph, [Text])

    """

    def __init__(self) -> None:
        self.tree: Optional[nodes.Manuscript] = None
        self.labels_to_nodes: dict[str, nodes.Node] = {}

    def transform(self, tree: nodes.Manuscript) -> nodes.Manuscript:
        """Transform a manuscript tree.

        For examples see class docstring.

        Parameters
        ----------
        tree
            Manuscript tree to be transformed.

        Returns
        -------
        tree
            The transformed tree.  All transformations occur in place.

        Notes
        -----
        *tree* is stored as ``self.tree``.

        """
        logger.info("Transforming...")
        self.tree = tree

        self.collect_labels()
        self.resolve_pending_references()
        self.add_necessary_subproofs()
        self.autonumber_nodes()
        self.make_toc()
        self.add_keywords_to_constructs()
        self.add_handrail_depth()
        self.assign_node_ids()
        return tree

    def collect_labels(self) -> None:
        """Find all nodes with labels.

        Find all nodes with a non-empty *label* attribute and build a label-to-node
        mapping.  This mapping is later used by other transforms.

        Warnings
        --------
        If two nodes with the same label are found, only the first node is assigned the
        label and the second (and later, if any) nodes' labels are erased and ignored.

        Notes
        -----
        This transform does not actually modify the tree, but is necessary for the
        execution of other transforms that may modify it.  Therefore, this must be
        executed before all other ones.

        """
        for node in self.tree.traverse(condition=lambda n: n.label):
            if node.label in self.labels_to_nodes:
                logger.warning(f"Duplicate label {node.label}, using first encountered")
                node.label = ""
                continue
            self.labels_to_nodes[node.label] = node

    def _label_to_node(self, label: str, default=nodes.Error) -> nodes.Node:
        try:
            return self.labels_to_nodes[label]
        except KeyError as e:
            logger.warning(f'Reference to nonexistent label "{label}"')
            return default(f'[unknown label "{label}"]')

    def resolve_pending_references(self) -> None:
        classes = [
            nodes.PendingReference,
            nodes.PendingCite,
            nodes.PendingPrev,
        ]

        counter = count()
        for pending in self.tree.traverse(condition=lambda n: type(n) in classes):
            if isinstance(pending, nodes.PendingReference):
                target = self._label_to_node(pending.target)
                if isinstance(target, nodes.Error):
                    pending.replace_self(target)
                else:
                    pending.replace_self(
                        nodes.Reference(
                            target=target,
                            overwrite_reftext=pending.overwrite_reftext,
                        )
                    )
            elif isinstance(pending, nodes.PendingCite):
                targets = [
                    self._label_to_node(label, nodes.UnknownBibitem)
                    for label in pending.targetlabels
                ]
                cite = nodes.Cite(targets=targets)
                cite.label = f"cite-{next(counter)}"
                pending.replace_self(cite)
                for tgt in targets:
                    tgt.backlinks.append(cite.label)
            elif isinstance(pending, nodes.PendingPrev):
                try:
                    step = pending.first_ancestor_of_type(nodes.Step)
                except AttributeError:
                    step = None
                if step is None:
                    raise RSMTransformerError("Found :prev: tag outside proof step")

                target = step
                for _ in range(int(str(pending.target))):
                    target = target.prev_sibling(nodes.Step)
                    if target is None:
                        raise RSMTransformerError(
                            f"Did not find previous {pending.target} step(s)"
                        )

                if target.label is None or not target.label.strip():
                    logger.warning(
                        ":prev: references un-labeled step, link will not work"
                    )
                pending.replace_self(
                    nodes.Reference(
                        target=target, overwrite_reftext=pending.overwrite_reftext
                    )
                )

        for pending in self.tree.traverse(condition=lambda n: type(n) in classes):
            raise RSMTransformerError("Found unresolved pending reference")

    def add_necessary_subproofs(self) -> None:
        for step in self.tree.traverse(nodeclass=nodes.Step):
            if not step.children:
                continue

            _, split_at_idx = step.first_of_type(
                (nodes.Step, nodes.Subproof), return_idx=True
            )
            if split_at_idx is None:
                split_at_idx = len(step.children)

            children = step.children[::]
            step.clear()

            statement = nodes.Statement()
            statement.append(children[:split_at_idx])
            statement.handrail_depth += 1

            if split_at_idx == len(children):
                step.append(statement)
                continue

            if isinstance(children[split_at_idx], nodes.Step):
                subproof = nodes.Subproof()
                subproof.append(children[split_at_idx:])
            elif isinstance(children[split_at_idx], nodes.Subproof):
                assert split_at_idx == len(children) - 1
                subproof = children[split_at_idx]
            else:
                raise RSMTransformerError("How did we get here?")
            step.append([statement, subproof])

    def autonumber_nodes(self) -> None:
        counts: dict[Type[nodes.Node], dict[Type[nodes.Node], Generator]] = defaultdict(
            lambda: defaultdict(lambda: count(start=1))
        )
        within_appendix = False
        for node in self.tree.traverse():
            if isinstance(node, nodes.Appendix):
                counts[nodes.Manuscript] = defaultdict(lambda: iter(ascii_uppercase))
                within_appendix = True
                continue
            if isinstance(node, (nodes.Proof, nodes.Subproof)):
                self._autonumber_steps(node)
                continue
            if isinstance(node, nodes.Step):
                continue

            if node.autonumber and not node.nonum:
                counts[type(node)] = defaultdict(lambda: count(start=1))
                num = next(counts[node.number_within][node.number_as])
                node.number = num
                if within_appendix and isinstance(node, nodes.Section):
                    node.reftext_template = node.reftext_template.replace(
                        "{nodeclass}", "Appendix"
                    )

    def _autonumber_steps(self, proof: nodes.Proof) -> None:
        step_gen = (s for s in proof.children if isinstance(s, nodes.Step))
        for idx, step in enumerate(step_gen, start=1):
            step.number = idx

    def make_toc(self) -> None:
        toc = None
        for node in self.tree.traverse(nodeclass=nodes.Contents):
            if toc is None:
                toc = node
            else:
                logger.warning("Multiple Tables of Content found, using only first one")
                node.remove_self()
        if toc is None:
            return

        current_parent = toc
        for sec in self.tree.traverse(nodeclass=nodes.Section):
            item = nodes.Item()
            reftext = f"{sec.title}" if sec.nonum else f"{sec.full_number}. {sec.title}"
            item.append(nodes.Reference(target=sec, overwrite_reftext=reftext))

            # The order of the `if isinstance(...)` statements here matters because all
            # Subsections are also Sections so isinstance(sec, nodes.Section) evaluates
            # to True even when sec is a Subsection.  Thus, we have to go from smallest
            # (Subsubsection) to largest (Section).
            if isinstance(sec, nodes.Subsubsection):
                current_parent.append(item)
                if sec.parent.last_of_type(nodes.Subsubsection) is sec:
                    current_parent = current_parent.parent.parent
            elif isinstance(sec, nodes.Subsection):
                current_parent.append(item)
                if sec.first_of_type(nodes.Subsubsection):
                    itemize = nodes.Itemize()
                    item.append(itemize)
                    current_parent = itemize
                elif sec.parent.last_of_type(nodes.Subsection) is sec:
                    current_parent = current_parent.parent.parent
            elif isinstance(sec, nodes.Section):
                toc.append(item)
                if sec.first_of_type(nodes.Subsection):
                    itemize = nodes.Itemize()
                    item.append(itemize)
                    current_parent = itemize
            else:
                raise RSMTransformerError("How did we get here?")

    def add_keywords_to_constructs(self) -> None:
        for construct in self.tree.traverse(nodeclass=nodes.Construct):
            kind = construct.kind
            assert kind
            construct.types.append(kind)
            if kind not in {"then", "suffices", "claim", "claimblock", "qed", "prove"}:
                construct.types.append("assumption")

    def add_handrail_depth(self) -> None:
        for nc in nodes.all_node_subtypes():
            if nc.has_handrail:
                self._add_handrail_depth_for_class(nc)

    def _add_handrail_depth_for_class(self, nodeclass) -> None:
        for node in self.tree.traverse(nodeclass=nodeclass):
            for desc in node.traverse():
                if desc == node:
                    continue
                desc.handrail_depth += 1

    def assign_node_ids(self) -> None:
        nodeid = 0
        for node in self.tree.traverse():
            node.nodeid = nodeid
            nodeid += 1
