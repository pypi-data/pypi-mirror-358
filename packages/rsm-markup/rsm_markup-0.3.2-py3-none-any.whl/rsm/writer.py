"""Input: WebManuscript -- Output: None (writes to disk)."""

import logging
from pathlib import Path
from typing import Optional

from fs.copy import copy_fs

from .manuscript import WebManuscript

logger = logging.getLogger("RSM").getChild("write")


class Writer:
    """Take a WebManuscript and write to disk."""

    def __init__(self, dstpath: Optional[Path] = None) -> None:
        self.web: Optional[WebManuscript] = None
        self.dstpath = Path() if dstpath is None else dstpath

    def write(self, web: WebManuscript) -> None:
        self.web = web
        copy_fs(web, "./")
