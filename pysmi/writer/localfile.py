#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import os
import tempfile
from contextlib import suppress

from pysmi import debug
from pysmi import error
from pysmi.compat import decode
from pysmi.compat import encode
from pysmi.writer.base import AbstractWriter


class FileWriter(AbstractWriter):
    """Stores transformed MIB modules in files at specified location.

    User is expected to pass *FileReader* class instance to
    *MibCompiler* on instantiation. The rest is internal to *MibCompiler*.
    """

    suffix = ""

    def __init__(self, path):
        """Creates an instance of *FileReader* class.

        Args:
            path: writable directory to store created files
        """
        self._path = decode(os.path.normpath(path))

    def __str__(self):
        return f'{self.__class__.__name__}{{"{self._path}"}}'

    def getData(self, mibname, dryRun=False):
        filename = os.path.join(self._path, decode(mibname)) + self.suffix

        f = None

        try:
            with open(filename) as f:
                data = f.read()
            return data

        except (OSError, UnicodeEncodeError):
            return ""

    def putData(self, mibname, data, comments=(), dryRun=False):
        if dryRun:
            if debug.logger & debug.flagWriter:
                debug.logger("dry run mode")
            return

        if not os.path.exists(self._path):
            try:
                os.makedirs(self._path)

            except OSError as err:
                msg = f"failure creating destination directory {self._path}: {err}"
                raise error.PySmiWriterError(
                    msg,
                    writer=self,
                ) from err

        if comments:
            comment_lines = [f"# {x}\n" for x in comments]
            data = f'#\n{"".join(comment_lines)}#\n{data}'

        filename = os.path.join(self._path, decode(mibname)) + self.suffix

        tfile = None

        try:
            fd, tfile = tempfile.mkstemp(dir=self._path)
            os.write(fd, encode(data))
            os.close(fd)
            os.rename(tfile, filename)

        except (OSError, UnicodeEncodeError) as err:
            if tfile:
                with suppress(OSError):
                    os.unlink(tfile)

            msg = f"failure writing file {filename}: {err}"
            raise error.PySmiWriterError(msg, file=filename, writer=self) from err

        if debug.logger & debug.flagWriter:
            debug.logger(f"{mibname} stored in {filename}")
