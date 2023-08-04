#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import datetime
import os
import sys
import time
import zipfile

from pysmi import debug
from pysmi import error
from pysmi.compat import decode
from pysmi.mibinfo import MibInfo
from pysmi.reader.base import AbstractReader


class FileLike:
    """Stripped down, binary file mock to work with ZipFile"""

    def __init__(self, buf, name):
        self.name = name
        self.buf = buf
        self.null = buf[:0]
        self.len = len(buf)
        self.buflist = []
        self.pos = 0
        self.closed = False
        self.softspace = 0

    def close(self):
        if not self.closed:
            self.closed = True
            self.buf = self.null
            self.pos = 0

    def seek(self, pos, mode=0):
        if self.buflist:
            self.buf += self.null.join(self.buflist)
            self.buflist = []

        if mode == 1:
            pos += self.pos

        elif mode == 2:
            pos += self.len

        self.pos = max(0, pos)

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if self.buflist:
            self.buf += self.null.join(self.buflist)
            self.buflist = []

        if n < 0:
            newpos = self.len
        else:
            newpos = min(self.pos + n, self.len)

        r = self.buf[self.pos : newpos]

        self.pos = newpos

        return r


class ZipReader(AbstractReader):
    """Fetch ASN.1 MIB text by name from a ZIP archive.

    *ZipReader* class instance tries to locate ASN.1 MIB files
    by name, fetch and return their contents to caller.
    """

    useIndexFile = False

    def __init__(self, path, ignoreErrors=True):
        """Create an instance of *ZipReader* serving a ZIP archive.

        Args:
            path (str): path to ZIP archive containing MIB files

        Keyword Args:
            ignoreErrors (bool): ignore ZIP archive access errors
        """
        self._name = path
        self._members = {}
        self._pendingError = None

        try:
            self._members = self._readZipDirectory(fileObj=open(path, "rb"))

        except Exception:
            if debug.logger & debug.flagReader:
                debug.logger(f"ZIP file {self._name} open failure: {sys.exc_info()[1]}")

            if not ignoreErrors:
                self._pendingError = error.PySmiError(f"file {self._name} access error: {sys.exc_info()[1]}")

    def _readZipDirectory(self, fileObj):
        archive = zipfile.ZipFile(fileObj)

        if isinstance(fileObj, FileLike):
            fileObj = None

        members = {}

        for member in archive.infolist():
            filename = os.path.basename(member.filename)
            if not filename:
                continue

            if member.filename.endswith(".zip") or member.filename.endswith(".ZIP"):
                innerZipBlob = archive.read(member.filename)

                innerMembers = self._readZipDirectory(FileLike(innerZipBlob, member.filename))

                for innerFilename, ref in innerMembers.items():
                    while innerFilename in members:
                        innerFilename += "+"

                    members[innerFilename] = [[fileObj, member.filename, None]]
                    members[innerFilename].extend(ref)

            else:
                mtime = time.mktime(datetime.datetime(*member.date_time[:6]).timetuple())

                members[filename] = [[fileObj, member.filename, mtime]]

        return members

    def _readZipFile(self, refs):
        for fileObj, filename, mtime in refs:
            if not fileObj:
                fileObj = FileLike(dataObj, name=self._name)

            archive = zipfile.ZipFile(fileObj)

            try:
                dataObj = archive.read(filename)

            except Exception:
                if debug.logger & debug.flagReader:
                    debug.logger(f"ZIP read component {fileObj.name} read error: {sys.exc_info()[1]}")
                return "", 0

        return dataObj, mtime

    def __str__(self):
        return f'{self.__class__.__name__}{{"{self._name}"}}'

    def getData(self, mibname, **options):
        if debug.logger & debug.flagReader:
            debug.logger(f"looking for MIB {mibname} at {self._name}")

        if self._pendingError:
            raise self._pendingError

        if not self._members:
            msg = f"source MIB {mibname} not found"
            raise error.PySmiReaderFileNotFoundError(msg, reader=self)

        for mibalias, mibfile in self.getMibVariants(mibname, **options):
            if debug.logger & debug.flagReader:
                debug.logger("trying MIB %s" % mibfile)

            try:
                refs = self._members[mibfile]

            except KeyError:
                continue

            mibData, mtime = self._readZipFile(refs)

            if not mibData:
                continue

            if debug.logger & debug.flagReader:
                debug.logger(
                    "source MIB {}, mtime {}, read from {}/{}".format(
                        mibfile,
                        time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime)),
                        self._name,
                        mibfile,
                    )
                )

            if len(mibData) == self.maxMibSize:
                msg = f"MIB {self._name}/{mibfile} too large"
                raise OSError(msg)

            return MibInfo(
                path=f"zip://{self._name}/{mibfile}",
                file=mibfile,
                name=mibalias,
                mtime=mtime,
            ), decode(mibData)

        msg = f"source MIB {mibname} not found"
        raise error.PySmiReaderFileNotFoundError(msg, reader=self)
