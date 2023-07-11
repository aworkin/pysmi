#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import sys
import unittest

from pysnmp.smi.builder import MibBuilder

from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.parser.smi import parserFactory


class TypeDeclarationTestCase(unittest.TestCase):
    """
    TEST-MIB DEFINITIONS ::= BEGIN
    IMPORTS

      NetworkAddress,
      IpAddress,
      Counter,
      Gauge,
      TimeTicks,
      Opaque
        FROM RFC1155-SMI;

    -- simple types
    TestTypeInteger ::= INTEGER
    TestTypeOctetString ::= OCTET STRING
    TestTypeObjectIdentifier ::= OBJECT IDENTIFIER

    -- application types
    TestTypeNetworkAddress::= NetworkAddress
    TestTypeIpAddress ::= IpAddress
    TestTypeCounter ::= Counter
    TestTypeGauge ::= Gauge
    TestTypeTimeTicks ::= TimeTicks
    TestTypeOpaque ::= Opaque

    END
    """

    def setUp(self):
        ast = parserFactory(**smiV1Relaxed)().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(
            ast, {mibInfo.name: symtable}, genTexts=True
        )
        codeobj = compile(pycode, "test", "exec")

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = {"mibBuilder": mibBuilder}

        exec(codeobj, self.ctx, self.ctx)

    def protoTestSymbol(self, symbol, klass):
        self.assertTrue(symbol in self.ctx, f"symbol {symbol} not present")

    def protoTestClass(self, symbol, klass):
        self.assertEqual(
            self.ctx[symbol].__bases__[0].__name__,
            klass,
            f"expected class {klass}, got {self.ctx[symbol].__bases__[0].__name__} at {symbol}",
        )


# populate test case class with per-type methods

typesMap = (
    ("TestTypeInteger", "Integer32"),
    ("TestTypeOctetString", "OctetString"),
    ("TestTypeObjectIdentifier", "ObjectIdentifier"),
    ("TestTypeNetworkAddress", "IpAddress"),
    ("TestTypeIpAddress", "IpAddress"),
    ("TestTypeCounter", "Counter32"),
    ("TestTypeGauge", "Gauge32"),
    ("TestTypeTimeTicks", "TimeTicks"),
    ("TestTypeOpaque", "Opaque"),
)


def decor(func, symbol, klass):
    def inner(self):
        func(self, symbol, klass)

    return inner


for s, k in typesMap:
    setattr(
        TypeDeclarationTestCase,
        "testTypeDeclaration" + k + "SymbolTestCase",
        decor(TypeDeclarationTestCase.protoTestSymbol, s, k),
    )
    setattr(
        TypeDeclarationTestCase,
        "testTypeDeclaration" + k + "ClassTestCase",
        decor(TypeDeclarationTestCase.protoTestClass, s, k),
    )

# XXX constraints flavor not checked

suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
