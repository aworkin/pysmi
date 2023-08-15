#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import unittest
from textwrap import dedent

import pytest
from pysnmp.smi.builder import MibBuilder

from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.parser.smi import parserFactory


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
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
        ),
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    ("symbol", "klass"),
    (
        ("TestTypeInteger", "Integer32"),
        ("TestTypeOctetString", "OctetString"),
        ("TestTypeObjectIdentifier", "ObjectIdentifier"),
        ("TestTypeNetworkAddress", "IpAddress"),
        ("TestTypeIpAddress", "IpAddress"),
        ("TestTypeCounter", "Counter32"),
        ("TestTypeGauge", "Gauge32"),
        ("TestTypeTimeTicks", "TimeTicks"),
        ("TestTypeOpaque", "Opaque"),
    ),
)
class TestTypeDeclaration:
    def test_symbol(self, pysnmp_classes, symbol, klass):
        assert symbol in pysnmp_classes, f"symbol {symbol} not present"

    def test_class(self, pysnmp_classes, symbol, klass):
        assert (
            pysnmp_classes[symbol].__bases__[0].__name__ == klass
        ), f"expected class {klass}, got {pysnmp_classes[symbol].__bases__[0].__name__} at {symbol}"


# XXX constraints flavor not checked

if __name__ == "__main__":
    pytest.main()
