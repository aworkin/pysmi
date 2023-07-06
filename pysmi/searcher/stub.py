#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
from pysmi.searcher.base import AbstractSearcher
from pysmi import debug
from pysmi import error


class StubSearcher(AbstractSearcher):
    """Figures out if given MIB module is present in a fixed list of modules.
    """

    def __init__(self, *mibnames):
        """Create an instance of *StubSearcher* initialized with a fixed list
           or MIB modules names.

           Args:
               mibnames (str): blacklisted MIB names
        """
        self._mibnames = mibnames

    def __str__(self):
        return f'{self.__class__.__name__}'

    def fileExists(self, mibname, mtime, rebuild=False):
        if mibname in self._mibnames:
            if debug.logger & debug.flagSearcher:
                debug.logger('pretend compiled %s exists and is very new' % mibname)
            raise error.PySmiFileNotModifiedError(f'compiled file {mibname} is among {", ".join(self._mibnames)}',
                                                  searcher=self)

        raise error.PySmiFileNotFoundError(f'no compiled file {mibname} found among {", ".join(self._mibnames)}',
                                           searcher=self)
