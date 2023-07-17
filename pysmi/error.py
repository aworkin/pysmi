#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
# Package exception model:
# Here we subclass base Python exception overriding its constructor to
# accommodate error message string as its first parameter and an open
# set of keyword arguments that become exception object attributes.
# While exception object is bubbling up the call stack, intermediate
# exception handlers may insert their own attributes into exception
# object.
#


class PySmiError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.msg = args[0] if args else ""
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __repr__(self):
        attrs = ", ".join([f"{k}={getattr(self, k)!r}" for k in dir(self) if k[0] != "_" and k != "args"])
        return f"{self.__class__.__name__}({attrs})"

    def __str__(self):
        return self.msg


class PySmiLexerError(PySmiError):
    lineno = "?"

    def __str__(self):
        return self.msg + f", line {self.lineno}"


class PySmiParserError(PySmiLexerError):
    pass


class PySmiSyntaxError(PySmiParserError):
    pass


class PySmiSearcherError(PySmiError):
    pass


class PySmiFileNotModifiedError(PySmiSearcherError):
    pass


class PySmiFileNotFoundError(PySmiSearcherError):
    pass


class PySmiReaderError(PySmiError):
    pass


class PySmiReaderFileNotModifiedError(PySmiReaderError):
    pass


class PySmiReaderFileNotFoundError(PySmiReaderError):
    pass


class PySmiCodegenError(PySmiError):
    pass


class PySmiSemanticError(PySmiCodegenError):
    pass


class PySmiWriterError(PySmiError):
    pass
