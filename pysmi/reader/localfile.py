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
from pysmi.mibinfo import MibInfo
from pysmi.reader.base import AbstractReader


class FileReader(AbstractReader):
    """Fetch ASN.1 MIB text by name from local file.

    *FileReader* class instance tries to locate ASN.1 MIB files
    by name, fetch and return their contents to caller.
    """

    useIndexFile = True  # optional .index file mapping MIB to file name
    indexFile = ".index"

    def __init__(self, path, recursive=True, ignoreErrors=True):
        """Create an instance of *FileReader* serving a directory.

        Args:
            path (str): directory to search MIB files

        Keyword Args:
            recursive (bool): whether to include subdirectories
            ignoreErrors (bool): ignore filesystem access errors
        """
        self._path = os.path.normpath(path)
        self._recursive = recursive
        self._ignoreErrors = ignoreErrors
        self._indexLoaded = False
        self._mibIndex = None

    def __str__(self):
        return f'{self.__class__.__name__}{{"{self._path}"}}'

    def getSubdirs(self, path, recursive=True, ignoreErrors=True):
        if not recursive:
            return [path]

        dirs = [path]

        try:
            subdirs = os.listdir(path)

        except OSError:
            if ignoreErrors:
                return dirs

            else:
                raise error.PySmiError(
                    f"directory {path} access error: {sys.exc_info()[1]}"
                )

        for d in subdirs:
            d = os.path.join(decode(path), decode(d))
            if os.path.isdir(d):
                dirs.extend(self.getSubdirs(d, recursive))

        return dirs

    @staticmethod
    def loadIndex(indexFile):
        mibIndex = {}
        if os.path.exists(indexFile):
            try:
                f = open(indexFile)
                mibIndex = dict([x.split()[:2] for x in f.readlines()])
                f.close()
                if debug.logger & debug.flagReader:
                    debug.logger(
                        "loaded MIB index map from %s file, %s entries"
                        % (indexFile, len(mibIndex))
                    )

            except IOError:
                pass

        return mibIndex

    def getMibVariants(self, mibname, **options):
        if self.useIndexFile:
            if not self._indexLoaded:
                self._mibIndex = self.loadIndex(
                    os.path.join(self._path, self.indexFile)
                )
                self._indexLoaded = True

            if mibname in self._mibIndex:
                if debug.logger & debug.flagReader:
                    debug.logger(
                        "found %s in MIB index: %s" % (mibname, self._mibIndex[mibname])
                    )
                return [(mibname, self._mibIndex[mibname])]

        return super(FileReader, self).getMibVariants(mibname, **options)

    def getData(self, mibname, **options):
        if debug.logger & debug.flagReader:
            debug.logger(
                "%slooking for MIB %s"
                % ("recursively " if self._recursive else "", mibname)
            )

        for path in self.getSubdirs(self._path, self._recursive, self._ignoreErrors):
            for mibalias, mibfile in self.getMibVariants(mibname, **options):
                f = os.path.join(decode(path), decode(mibfile))

                if debug.logger & debug.flagReader:
                    debug.logger("trying MIB %s" % f)

                if os.path.exists(f) and os.path.isfile(f):
                    try:
                        mtime = os.stat(f)[8]

                        if debug.logger & debug.flagReader:
                            debug.logger(
                                "source MIB %s mtime is %s, fetching data..."
                                % (
                                    f,
                                    time.strftime(
                                        "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime)
                                    ),
                                )
                            )

                        fp = open(f, mode="rb")
                        mibData = fp.read(self.maxMibSize)
                        fp.close()

                        if len(mibData) == self.maxMibSize:
                            raise IOError(f"MIB {f} too large")

                        return MibInfo(
                            path=f"file://{f}", file=mibfile, name=mibalias, mtime=mtime
                        ), decode(mibData)

                    except (OSError, IOError):
                        if debug.logger & debug.flagReader:
                            debug.logger(
                                "source file %s open failure: %s"
                                % (f, sys.exc_info()[1])
                            )

                        if not self._ignoreErrors:
                            raise error.PySmiError(
                                f"file {f} access error: {sys.exc_info()[1]}"
                            )

                    raise error.PySmiReaderFileNotModifiedError(
                        f"source MIB {f} is older than needed", reader=self
                    )

        raise error.PySmiReaderFileNotFoundError(
            f"source MIB {mibname} not found", reader=self
        )
