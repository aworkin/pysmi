#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import re

from ply import lex
from ply.lex import TOKEN

from pysmi import debug
from pysmi import error
from pysmi.lexer.base import AbstractLexer

UNSIGNED32_MAX = 4294967295
UNSIGNED64_MAX = 18446744073709551615
LEX_VERSION = [int(x) for x in lex.__version__.split(".")]


# Do not overload single lexer methods - overload all or none of them!
class SmiV2Lexer(AbstractLexer):
    reserved_words = [
        "ACCESS",
        "AGENT-CAPABILITIES",
        "APPLICATION",
        "AUGMENTS",
        "BEGIN",
        "BITS",
        "CONTACT-INFO",
        "CREATION-REQUIRES",
        "Counter",
        "Counter32",
        "Counter64",
        "DEFINITIONS",
        "DEFVAL",
        "DESCRIPTION",
        "DISPLAY-HINT",
        "END",
        "ENTERPRISE",
        "EXTENDS",
        "FROM",
        "GROUP",
        "Gauge",
        "Gauge32",
        "IDENTIFIER",
        "IMPLICIT",
        "IMPLIED",
        "IMPORTS",
        "INCLUDES",
        "INDEX",
        "INSTALL-ERRORS",
        "INTEGER",
        "Integer32",
        "IpAddress",
        "LAST-UPDATED",
        "MANDATORY-GROUPS",
        "MAX-ACCESS",
        "MIN-ACCESS",
        "MODULE",
        "MODULE-COMPLIANCE",
        "MODULE-IDENTITY",
        "NOTIFICATION-GROUP",
        "NOTIFICATION-TYPE",
        "NOTIFICATIONS",
        "OBJECT",
        "OBJECT-GROUP",
        "OBJECT-IDENTITY",
        "OBJECT-TYPE",
        "OBJECTS",
        "OCTET",
        "OF",
        "ORGANIZATION",
        "Opaque",
        "PIB-ACCESS",
        "PIB-DEFINITIONS",
        "PIB-INDEX",
        "PIB-MIN-ACCESS",
        "PIB-REFERENCES",
        "PIB-TAG",
        "POLICY-ACCESS",
        "PRODUCT-RELEASE",
        "REFERENCE",
        "REVISION",
        "SEQUENCE",
        "SIZE",
        "STATUS",
        "STRING",
        "SUBJECT-CATEGORIES",
        "SUPPORTS",
        "SYNTAX",
        "TEXTUAL-CONVENTION",
        "TimeTicks",
        "TRAP-TYPE",
        "UNIQUENESS",
        "UNITS",
        "UNIVERSAL",
        "Unsigned32",
        "VALUE",
        "VARIABLES",
        "VARIATION",
        "WRITE-SYNTAX",
    ]

    reserved = {}
    for w in reserved_words:
        reserved[w] = w.replace("-", "_").upper()
        # hack to support SMIv1
        if w == "Counter":
            reserved[w] = "COUNTER32"
        elif w == "Gauge":
            reserved[w] = "GAUGE32"

    forbidden_words = [
        "ABSENT",
        "ANY",
        "BIT",
        "BOOLEAN",
        "BY",
        "COMPONENT",
        "COMPONENTS",
        "DEFAULT",
        "DEFINED",
        "ENUMERATED",
        "EXPLICIT",
        "EXTERNAL",
        "FALSE",
        "MAX",
        "MIN",
        "MINUS-INFINITY",
        "NULL",
        "OPTIONAL",
        "PLUS-INFINITY",
        "PRESENT",
        "PRIVATE",
        "REAL",
        "SET",
        "TAGS",
        "TRUE",
        "WITH",
    ]

    # Token names required!
    tokens = list(
        set(
            [
                "BIN_STRING",
                "CHOICE",
                "COLON_COLON_EQUAL",
                "DOT_DOT",
                "EXPORTS",
                "HEX_STRING",
                "LOWERCASE_IDENTIFIER",
                "MACRO",
                "NEGATIVENUMBER",
                "NEGATIVENUMBER64",
                "NUMBER",
                "NUMBER64",
                "QUOTED_STRING",
                "UPPERCASE_IDENTIFIER",
            ]
            + list(reserved.values())
        )
    )

    states = (
        ("macro", "exclusive"),
        ("choice", "exclusive"),
        ("exports", "exclusive"),
        ("comment", "exclusive"),
    )

    literals = "[]{}():;,-.|"

    t_DOT_DOT = r"\.\."
    t_COLON_COLON_EQUAL = r"::="

    t_ignore = " \t"

    def __init__(self, tempdir=""):
        self._tempdir = tempdir
        self.lexer = None
        self.reset()

    def reset(self):
        if LEX_VERSION < [3, 0]:  # noqa: SIM300
            self.lexer = lex.lex(module=self, reflags=re.DOTALL, outputdir=self._tempdir, debug=False)
        else:
            logger = debug.logger.getCurrentLogger() if debug.logger & debug.flagLexer else lex.NullLogger()

            debuglogger = debug.logger.getCurrentLogger() if debug.logger & debug.flagGrammar else None

            self.lexer = lex.lex(
                module=self,
                reflags=re.DOTALL,
                outputdir=self._tempdir,
                debuglog=debuglogger,
                errorlog=logger,
            )

    @TOKEN(r"\r\n|\n|\r")
    def t_newline(self, t):
        t.lexer.lineno += 1

    # Skipping MACRO
    @TOKEN(r"MACRO")
    def t_MACRO(self, t):
        t.lexer.begin("macro")
        return t

    @TOKEN(r"\r\n|\n|\r")
    def t_macro_newline(self, t):
        t.lexer.lineno += 1

    @TOKEN(r"END")
    def t_macro_END(self, t):
        t.lexer.begin("INITIAL")
        return t

    @TOKEN(r".+?(?=END)")
    def t_macro_body(self, t):
        pass

    # Skipping EXPORTS
    @TOKEN(r"EXPORTS")
    def t_EXPORTS(self, t):
        t.lexer.begin("exports")
        return t

    @TOKEN(r"\r\n|\n|\r")
    def t_exports_newline(self, t):
        t.lexer.lineno += 1

    @TOKEN(r";")
    def t_exports_end(self, t):
        t.lexer.begin("INITIAL")

    @TOKEN(r"[^;]+")
    def t_exports_body(self, t):
        pass

    # Skipping CHOICE
    @TOKEN(r"CHOICE")
    def t_CHOICE(self, t):
        t.lexer.begin("choice")
        return t

    @TOKEN(r"\r\n|\n|\r")
    def t_choice_newline(self, t):
        t.lexer.lineno += 1

    @TOKEN(r"\}")
    def t_choice_end(self, t):
        t.lexer.begin("INITIAL")

    @TOKEN(r"[^\}]+")
    def t_choice_body(self, t):
        pass

    # Comment handling
    @TOKEN(r"--")
    def t_begin_comment(self, t):
        t.lexer.begin("comment")

    @TOKEN(r"\r\n|\n|\r")
    def t_comment_newline(self, t):
        t.lexer.lineno += 1
        t.lexer.begin("INITIAL")

    #  def t_comment_end(self, t):
    #    r'--'
    #    t.lexer.begin('INITIAL')

    @TOKEN(r"[^\r\n]+")
    def t_comment_body(self, t):
        pass

    @TOKEN(r"[A-Z][-a-zA-z0-9]*")
    def t_UPPERCASE_IDENTIFIER(self, t):
        if t.value in self.forbidden_words:
            msg = f"{t.value} is forbidden"
            raise error.PySmiLexerError(msg, lineno=t.lineno)

        if t.value[-1] == "-":
            msg = f"Identifier should not end with '-': {t.value}"
            raise error.PySmiLexerError(msg, lineno=t.lineno)

        t.type = self.reserved.get(t.value, "UPPERCASE_IDENTIFIER")

        return t

    @TOKEN(r"[0-9]*[a-z][-a-zA-z0-9]*")
    def t_LOWERCASE_IDENTIFIER(self, t):
        if t.value[-1] == "-":
            msg = f"Identifier should not end with '-': {t.value}"
            raise error.PySmiLexerError(msg, lineno=t.lineno)
        return t

    @TOKEN(r"-?[0-9]+")
    def t_NUMBER(self, t):
        t.value = int(t.value)
        neg = 0
        if t.value < 0:
            neg = 1

        val = abs(t.value)

        if val <= UNSIGNED32_MAX:
            if neg:
                t.type = "NEGATIVENUMBER"

        elif val <= UNSIGNED64_MAX:
            if neg:
                t.type = "NEGATIVENUMBER64"
            else:
                t.type = "NUMBER64"

        else:
            msg = f"Number {t.value} is too big"
            raise error.PySmiLexerError(msg, lineno=t.lineno)

        return t

    @TOKEN(r"\'[01]*\'[bB]")
    def t_BIN_STRING(self, t):
        value = t.value[1:-2]
        while value and value[0] == "0" and len(value) % 8:
            value = value[1:]
        # XXX raise in strict mode
        #    if len(value) % 8:
        #      raise error.PySmiLexerError("Number of 0s and 1s have to divide by 8 in binary string %s" % t.value, lineno=t.lineno)
        return t

    @TOKEN(r"\'[0-9a-fA-F]*\'[hH]")
    def t_HEX_STRING(self, t):
        value = t.value[1:-2]
        while value and value[0] == "0" and len(value) % 2:
            value = value[1:]
        # XXX raise in strict mode
        #    if len(value) % 2:
        #      raise error.PySmiLexerError("Number of symbols have to be even in hex string %s" % t.value, lineno=t.lineno)
        return t

    @TOKEN(r"\"[^\"]*\"")
    def t_QUOTED_STRING(self, t):
        t.lexer.lineno += len(re.findall(r"\r\n|\n|\r", t.value))
        return t

    def t_error(self, t):
        msg = f"Illegal character '{t.value[0]}', {len(t.value) - 1} characters left unparsed at this stage"
        raise error.PySmiLexerError(
            msg,
            lineno=t.lineno,
        )
        # t.lexer.skip(1)


class SupportSmiV1Keywords:
    @staticmethod
    def reserved():
        reserved_words = [
            "ACCESS",
            "AGENT-CAPABILITIES",
            "APPLICATION",
            "AUGMENTS",
            "BEGIN",
            "BITS",
            "CONTACT-INFO",
            "CREATION-REQUIRES",
            "Counter",
            "Counter32",
            "Counter64",
            "DEFINITIONS",
            "DEFVAL",
            "DESCRIPTION",
            "DISPLAY-HINT",
            "END",
            "ENTERPRISE",
            "EXTENDS",
            "FROM",
            "GROUP",
            "Gauge",
            "Gauge32",
            "IDENTIFIER",
            "IMPLICIT",
            "IMPLIED",
            "IMPORTS",
            "INCLUDES",
            "INDEX",
            "INSTALL-ERRORS",
            "INTEGER",
            "Integer32",
            "IpAddress",
            "LAST-UPDATED",
            "MANDATORY-GROUPS",
            "MAX-ACCESS",
            "MIN-ACCESS",
            "MODULE",
            "MODULE-COMPLIANCE",
            "MAX",
            "MODULE-IDENTITY",
            "NetworkAddress",
            "NOTIFICATION-GROUP",
            "NOTIFICATION-TYPE",
            "NOTIFICATIONS",
            "OBJECT",
            "OBJECT-GROUP",
            "OBJECT-IDENTITY",
            "OBJECT-TYPE",
            "OBJECTS",
            "OCTET",
            "OF",
            "ORGANIZATION",
            "Opaque",
            "PIB-ACCESS",
            "PIB-DEFINITIONS",
            "PIB-INDEX",
            "PIB-MIN-ACCESS",
            "PIB-REFERENCES",
            "PIB-TAG",
            "POLICY-ACCESS",
            "PRODUCT-RELEASE",
            "REFERENCE",
            "REVISION",
            "SEQUENCE",
            "SIZE",
            "STATUS",
            "STRING",
            "SUBJECT-CATEGORIES",
            "SUPPORTS",
            "SYNTAX",
            "TEXTUAL-CONVENTION",
            "TimeTicks",
            "TRAP-TYPE",
            "UNIQUENESS",
            "UNITS",
            "UNIVERSAL",
            "Unsigned32",
            "VALUE",
            "VARIABLES",
            "VARIATION",
            "WRITE-SYNTAX",
        ]

        reserved = {}
        for w in reserved_words:
            reserved[w] = w.replace("-", "_").upper()
            # hack to support SMIv1
            if w == "Counter":
                reserved[w] = "COUNTER32"
            elif w == "Gauge":
                reserved[w] = "GAUGE32"

        return reserved

    @staticmethod
    def forbidden_words():
        return [
            "ABSENT",
            "ANY",
            "BIT",
            "BOOLEAN",
            "BY",
            "COMPONENT",
            "COMPONENTS",
            "DEFAULT",
            "DEFINED",
            "ENUMERATED",
            "EXPLICIT",
            "EXTERNAL",
            "FALSE",
            "MIN",
            "MINUS-INFINITY",
            "NULL",
            "OPTIONAL",
            "PLUS-INFINITY",
            "PRESENT",
            "PRIVATE",
            "REAL",
            "SET",
            "TAGS",
            "TRUE",
            "WITH",
        ]

    @staticmethod
    def tokens():
        # Token names required!
        tokens = [
            "BIN_STRING",
            "CHOICE",
            "COLON_COLON_EQUAL",
            "DOT_DOT",
            "EXPORTS",
            "HEX_STRING",
            "LOWERCASE_IDENTIFIER",
            "MACRO",
            "NEGATIVENUMBER",
            "NEGATIVENUMBER64",
            "NUMBER",
            "NUMBER64",
            "QUOTED_STRING",
            "UPPERCASE_IDENTIFIER",
        ]
        tokens += list(SupportSmiV1Keywords.reserved().values())
        return list(set(tokens))


relaxedGrammar = {
    "supportSmiV1Keywords": [
        SupportSmiV1Keywords.reserved,
        SupportSmiV1Keywords.forbidden_words,
        SupportSmiV1Keywords.tokens,
    ],
    "supportIndex": [],
    "commaAtTheEndOfImport": [],
    "commaAtTheEndOfSequence": [],
    "mixOfCommasAndSpaces": [],
    "uppercaseIdentifier": [],
    "lowcaseIdentifier": [],
    "curlyBracesAroundEnterpriseInTrap": [],
    "noCells": [],
}


def lexerFactory(**grammarOptions):
    classAttr = {}

    for option in grammarOptions:
        if grammarOptions[option]:
            if option not in relaxedGrammar:
                msg = f"Unknown lexer relaxation option: {option}"
                raise error.PySmiError(msg)

            for func in relaxedGrammar[option]:
                classAttr[func.__name__] = func()

    return type("SmiLexer", (SmiV2Lexer,), classAttr)
