#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import os
import sys
import time

from pysmi import debug
from pysmi import error
from pysmi.compat import decode
from pysmi.searcher.base import AbstractSearcher


class AnyFileSearcher(AbstractSearcher):
    """Figures out if given file exists at given location."""

    exts = []

    def __init__(self, path):
        """Create an instance of *AnyFileSearcher* bound to specific directory.

        Args:
          path (str): path to local directory
        """
        self._path = os.path.normpath(decode(path))

    def __str__(self):
        return f'{self.__class__.__name__}{{"{self._path}"}}'

    def fileExists(self, mibname, mtime, rebuild=False):
        if rebuild:
            if debug.logger & debug.flagSearcher:
                debug.logger("pretend %s is very old" % mibname)
            return

        mibname = decode(mibname)
        basename = os.path.join(self._path, mibname)

        for sfx in self.exts:
            f = basename + sfx
            if not os.path.exists(f) or not os.path.isfile(f):
                if debug.logger & debug.flagSearcher:
                    debug.logger("%s not present or not a file" % f)
                continue

            try:
                fileTime = os.stat(f)[8]

            except OSError:
                msg = f"failure opening compiled file {f}: {sys.exc_info()[1]}"
                raise error.PySmiSearcherError(
                    msg,
                    searcher=self,
                )

            if debug.logger & debug.flagSearcher:
                debug.logger(
                    "found {}, mtime {}".format(
                        f,
                        time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(fileTime)),
                    )
                )

            if fileTime >= mtime:
                raise error.PySmiFileNotModifiedError()

        msg = f"no compiled file {mibname} found"
        raise error.PySmiFileNotFoundError(msg, searcher=self)
