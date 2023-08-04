#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import os
import struct
import time

try:
    import importlib

    try:
        PY_MAGIC_NUMBER = importlib.util.MAGIC_NUMBER
        SOURCE_SUFFIXES = importlib.machinery.SOURCE_SUFFIXES
        BYTECODE_SUFFIXES = importlib.machinery.BYTECODE_SUFFIXES

    except Exception as err:
        raise ImportError() from err

except ImportError:
    import imp

    PY_MAGIC_NUMBER = imp.get_magic()
    SOURCE_SUFFIXES = [s[0] for s in imp.get_suffixes() if s[2] == imp.PY_SOURCE]
    BYTECODE_SUFFIXES = [s[0] for s in imp.get_suffixes() if s[2] == imp.PY_COMPILED]

from pysmi import debug
from pysmi import error
from pysmi.compat import decode
from pysmi.searcher.base import AbstractSearcher


class PyFileSearcher(AbstractSearcher):
    """Figures out if given Python file (source or bytecode) exists at given
    location.
    """

    def __init__(self, path):
        """Create an instance of *PyFileSearcher* bound to specific directory.

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
        pyfile = os.path.join(self._path, mibname)

        for pySfx in BYTECODE_SUFFIXES:
            f = pyfile + pySfx

            if not os.path.exists(f) or not os.path.isfile(f):
                if debug.logger & debug.flagSearcher:
                    debug.logger("%s not present or not a file" % f)
                continue

            try:
                with open(f, "rb") as fp:
                    pyData = fp.read(8)

            except OSError as err:
                msg = f"failure opening compiled file {f}: {err}"
                raise error.PySmiSearcherError(
                    msg,
                    searcher=self,
                ) from err
            if pyData[:4] == PY_MAGIC_NUMBER:
                pyData = pyData[4:]
                pyTime = struct.unpack("<L", pyData[:4])[0]
                if debug.logger & debug.flagSearcher:
                    debug.logger(
                        "found {}, mtime {}".format(
                            f,
                            time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime)),
                        )
                    )
                if pyTime >= mtime:
                    raise error.PySmiFileNotModifiedError()

                else:
                    msg = f"older file {mibname} exists"
                    raise error.PySmiFileNotFoundError(msg, searcher=self)

            else:
                if debug.logger & debug.flagSearcher:
                    debug.logger("bad magic in %s" % f)
                continue

        for pySfx in SOURCE_SUFFIXES:
            f = pyfile + pySfx

            if not os.path.exists(f) or not os.path.isfile(f):
                if debug.logger & debug.flagSearcher:
                    debug.logger("%s not present or not a file" % f)
                continue

            try:
                pyTime = os.stat(f)[8]

            except OSError as err:
                msg = f"failure opening compiled file {f}: {err}"
                raise error.PySmiSearcherError(
                    msg,
                    searcher=self,
                ) from err

            if debug.logger & debug.flagSearcher:
                debug.logger(
                    "found {}, mtime {}".format(
                        f,
                        time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime)),
                    )
                )

            if pyTime >= mtime:
                raise error.PySmiFileNotModifiedError()

        msg = f"no compiled file {mibname} found"
        raise error.PySmiFileNotFoundError(msg, searcher=self)
