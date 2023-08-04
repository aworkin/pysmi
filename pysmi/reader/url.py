#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
from urllib import parse as urlparse
from urllib.request import url2pathname

from pysmi import error
from pysmi.reader.ftpclient import FtpReader
from pysmi.reader.httpclient import HttpReader
from pysmi.reader.localfile import FileReader
from pysmi.reader.zipreader import ZipReader


def getReadersFromUrls(*sourceUrls, **options):
    readers = []
    for sourceUrl in sourceUrls:
        mibSource = urlparse.urlparse(sourceUrl)

        if mibSource.scheme in ("", "file", "zip"):
            scheme = mibSource.scheme
            filePath = url2pathname(mibSource.path)
            scheme = "zip" if scheme != "file" and (filePath.endswith(".zip") or filePath.endswith(".ZIP")) else "file"

            if scheme == "file":
                readers.append(FileReader(filePath).setOptions(**options))
            else:
                readers.append(ZipReader(filePath).setOptions(**options))

        elif mibSource.scheme in ("http", "https"):
            readers.append(
                HttpReader(
                    mibSource.hostname or mibSource.netloc,
                    mibSource.port or 80,
                    mibSource.path,
                    ssl=mibSource.scheme == "https",
                ).setOptions(**options)
            )

        elif mibSource.scheme in ("ftp", "sftp"):
            readers.append(
                FtpReader(
                    mibSource.hostname or mibSource.netloc,
                    mibSource.path,
                    ssl=mibSource.scheme == "sftp",
                    port=mibSource.port or 21,
                    user=mibSource.username or "anonymous",
                    password=mibSource.password or "anonymous@",
                ).setOptions(**options)
            )

        else:
            msg = f"Unsupported URL scheme {sourceUrl}"
            raise error.PySmiError(msg)

    return readers
