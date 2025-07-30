"""Applications that execute the steps of the RSM file processing pipeline.

Classes in this module use the steps implemented elsewhere (:mod:`rsm.reader`,
:mod:`rsm.tsparser`, etc) and actually execute those steps, feeding the output of one
step into the next.  The base class for all of these is :class:`RSMApp`, which stores
the sequence of steps and executes them all via a ``run()`` method.

The three main applications provided currently are :func:`make`, :func:`render`, and
:func:`lint`.  These simply instantiate an object of class :class:`FullBuildApp`,
:class:`LinterApp`, :class:`ProcessorApp`, respectively, and call their ``run()``
method.

The functions :func:`make`, :func:`render`, and :func:`lint` can be called directly via
``rsm.make()``, ``rsm.render()``, and ``rsm.lint()``.  They each receive RSM source
(either a string or a path to a file), run the application, and return the result.  For
more control over the execution, or post-execution inspection, instantiate the
appropriate class manually.  For example:

.. code-block:: python

   This
   >>> src = ":rsm: Hello, RSM! ::"
   >>> html = rsm.make(source=src)

   Is essentially equivalent to the following.

   >>> app = FullBuildApp(plain=src)
   >>> html = app.run()

   Except that now, ``app`` can be inspected.

   >>> print(app.parser.ast.sexp())
   (Manuscript
     (Paragraph
       (Text)))

The module :mod:`rsm.cli` exposes these apps as command line utilities.

The RSM library code (i.e. all of the previous modules) does not itself set up any
logging facilities.  This is at `recommendation
<https://docs.python.org/3/howto/logging-cookbook.html#adding-handlers-other-than-nullhandler-to-a-logger-in-a-library>`_
of the Python standard library.  Instead, this module uses the functions in
:mod:`rsm.rsmlogger` before executing an application.  In other words, manually handling
RSM source with classes such as :class:`rsm.tsparser.TSParser` or
:class:`rsm.transformer.Transformer` will not issue any logging messages, while calling
the ``run()`` method on an :class:`RSMApp` instance will.

"""

import logging
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional, Union

from icecream import ic

from rsm import (
    builder,
    linter,
    reader,
    rsmlogger,
    transformer,
    translator,
    tsparser,
    writer,
)
from rsm.tsparser import RSMParserError


from .rsmlogger import GatherHandler

logger = logging.getLogger("RSM")


class RSMApplicationError(Exception):
    pass


class Task(NamedTuple):
    """A step in a :class:`Pipeline`."""

    name: str
    obj: Any
    run: Callable


class Pipeline:
    """A sequence of :class:`Task` instances executed one after the other."""

    def __init__(self, tasks: list[Task]):
        self.tasks: list[Task] = []
        for t in tasks:
            self.add_task(t)

    def add_task(self, task: Task) -> None:
        """Add a task at the end of the current pipeline."""
        self.tasks.append(task)
        setattr(self, task.name, task.obj)

    def pop_task(self) -> Task:
        """Remove and return the last task."""
        task = self.tasks.pop()
        delattr(self, task.name)
        return task

    def run(self, initial_args: Any = None) -> Any:
        """Execute every task in the pipeline serially."""
        res = initial_args
        for _, _, call in self.tasks:
            if isinstance(res, dict):
                res = call(**res)
            elif isinstance(res, (list, tuple)):
                res = call(*res)
            elif res is None:
                res = call()
            else:
                res = call(res)
        return res


class RSMApp(Pipeline):
    default_log_level = logging.WARNING

    def __init__(
        self,
        tasks: Optional[list[Task]] = None,
        loglevel: int = default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ):
        rsmlogger.config_rsm_logger(loglevel, log_format, log_time, log_lineno)
        logger.info("Application started")
        logger.info("Configuring...")
        # self.config = self.config.configure()
        super().__init__(tasks or [])

    def run(self, initial_args: Any = None) -> Optional[str]:
        try:
            result = super().run(initial_args)
            logger.info("Done.")
        except RSMParserError as e:
            logger.error(f"There was an error: {e}")
            result = ""
        return result

    def _setup_handler(self) -> None:
        target = logging.StreamHandler()
        target.setLevel(logging.WARNING)
        handler = GatherHandler([logging.WARNING], target)
        logger.addHandler(handler)

    @property
    def logs(self) -> list:
        return []


class ParserApp(RSMApp):
    def __init__(
        self,
        srcpath: Optional[Path] = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ):
        self._validate_srcpath_and_plain(srcpath, plain)

        tasks = []
        if not plain:
            tasks.append(Task("reader", r := reader.Reader(), lambda: r.read(srcpath)))
        else:
            tasks.append(Task("dummy", None, lambda: plain))

        tasks += [
            Task("parser", p := tsparser.TSParser(), p.parse),
            Task("transformer", t := transformer.Transformer(), t.transform),
        ]
        super().__init__(tasks, loglevel, log_format, log_time, log_lineno)

    @staticmethod
    def _validate_srcpath_and_plain(
        srcpath: Union[Path, str, None], plain: str
    ) -> None:
        if (not srcpath and not plain) or (srcpath and plain):
            raise RSMApplicationError("Must specify exactly one of srcpath, plain")


class LinterApp(ParserApp):
    def __init__(
        self,
        srcpath: Optional[Path] = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ):
        super().__init__(
            srcpath, plain, linter.Linter.LINT_LVL, log_format, log_time, log_lineno
        )
        mylinter = linter.Linter()
        self.add_task(Task("linter", mylinter, mylinter.lint))


class ProcessorApp(ParserApp):
    def __init__(
        self,
        srcpath: Optional[Path] = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        handrails: bool = False,
        add_source: bool = True,
        run_linter: bool = False,
    ):
        super().__init__(srcpath, plain, loglevel, log_format, log_time, log_lineno)
        if run_linter:
            self.add_task(Task("linter", l := linter.Linter(), l.lint))

        if not handrails:
            tr = translator.Translator()
        else:
            tr = translator.HandrailsTranslator(
                add_source=add_source,
            )
        self.add_task(Task("translator", tr, tr.translate))


class FullBuildApp(ProcessorApp):
    def __init__(
        self,
        srcpath: Optional[Path] = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        handrails: bool = True,
        run_linter: bool = False,
    ):
        super().__init__(
            srcpath, plain, loglevel, log_format, log_time, handrails, run_linter
        )
        self.add_task(Task("builder", b := builder.FullBuilder(), b.build))
        self.add_task(Task("writer", w := writer.Writer(), w.write))


def render(
    source: str = "",
    path: str = "",
    handrails: bool = False,
    add_source: bool = False,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
) -> str:
    return ProcessorApp(
        srcpath=path,
        plain=source,
        handrails=handrails,
        add_source=add_source,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
    ).run()


def lint(
    source: str = "",
    path: str = "",
    handrails: bool = False,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
):
    return LinterApp(
        srcpath=path,
        plain=source,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
    ).run()


def make(
    source: str = "",
    path: str = "",
    handrails: bool = True,
    lint: bool = True,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
) -> str:
    return FullBuildApp(
        srcpath=path,
        plain=source,
        run_linter=lint,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
    ).run()
