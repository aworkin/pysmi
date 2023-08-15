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
from pysmi.parser.smi import parserFactory

types_map = (
    # TODO: Integer/Integer32?
    ("TestTypeInteger", "Integer32"),
    ("TestTypeOctetString", "OctetString"),
    ("TestTypeObjectIdentifier", "ObjectIdentifier"),
    ("TestTypeIpAddress", "IpAddress"),
    ("TestTypeInteger32", "Integer32"),
    ("TestTypeCounter32", "Counter32"),
    ("TestTypeGauge32", "Gauge32"),
    ("TestTypeTimeTicks", "TimeTicks"),
    ("TestTypeOpaque", "Opaque"),
    ("TestTypeCounter64", "Counter64"),
    ("TestTypeUnsigned32", "Unsigned32"),
    ("TestTypeEnum", "Integer32"),
    ("TestTypeSizeRangeConstraint", "OctetString"),
    ("TestTypeSizeConstraint", "OctetString"),
    ("TestTypeRangeConstraint", "Integer32"),
    ("TestTypeSingleValueConstraint", "Integer32"),
)


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
            
              IpAddress,
              Counter32,
              Gauge32,
              TimeTicks,
              Opaque,
              Integer32,
              Unsigned32,
              Counter64
                FROM SNMPv2-SMI
            
              TEXTUAL-CONVENTION
                FROM SNMPv2-TC;
            
            -- simple types
            TestTypeInteger ::= INTEGER
            TestTypeOctetString ::= OCTET STRING
            TestTypeObjectIdentifier ::= OBJECT IDENTIFIER
            
            -- application types
            TestTypeIpAddress ::= IpAddress
            TestTypeInteger32 ::= Integer32
            TestTypeCounter32 ::= Counter32
            TestTypeGauge32 ::= Gauge32
            TestTypeTimeTicks ::= TimeTicks
            TestTypeOpaque ::= Opaque
            TestTypeCounter64 ::= Counter64
            TestTypeUnsigned32 ::= Unsigned32
            
            -- constrained subtypes
            
            TestTypeEnum ::= INTEGER {
                                noResponse(-1),
                                noError(0),
                                tooBig(1)
                            }
            TestTypeSizeRangeConstraint ::= OCTET STRING (SIZE (0..255))
            TestTypeSizeConstraint ::= OCTET STRING (SIZE (8 | 11))
            TestTypeRangeConstraint ::= INTEGER (0..2)
            TestTypeSingleValueConstraint ::= INTEGER (0|2|4)
            
            TestTypeBits ::= BITS {
                                sunday(0),
                                monday(1),
                                tuesday(2),
                                wednesday(3),
                                thursday(4),
                                friday(5),
                                saturday(6)
                            }
            
            
            TestTextualConvention ::= TEXTUAL-CONVENTION
                DISPLAY-HINT "1x:"
                STATUS       current
                DESCRIPTION
                        "Test TC"
                REFERENCE
                        "Test reference"
                SYNTAX       OCTET STRING
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestTypeDeclaration:
    @pytest.mark.parametrize(
        ("symbol", "klass"),
        types_map,
    )
    def test_symbol(self, pysnmp_classes, symbol, klass):
        assert symbol in pysnmp_classes, f"symbol {symbol} not present"

    @pytest.mark.parametrize(
        ("symbol", "klass"),
        types_map,
    )
    def test_class(self, pysnmp_classes, symbol, klass):
        assert (
            pysnmp_classes[symbol].__bases__[0].__name__ == klass
        ), f"expected class {klass}, got {pysnmp_classes[symbol].__bases__[0].__name__} at {symbol}"

    def test_textual_convention_symbol(self, pysnmp_classes):
        assert "TestTextualConvention" in pysnmp_classes, "symbol not present"

    def test_textual_convention_display_hint(self, pysnmp_classes):
        assert pysnmp_classes["TestTextualConvention"].getDisplayHint() == "1x:", "bad DISPLAY-HINT"

    def test_textual_convention_status(self, pysnmp_classes):
        assert pysnmp_classes["TestTextualConvention"].getStatus() == "current", "bad STATUS"

    def test_textual_convention_description(self, pysnmp_classes):
        assert pysnmp_classes["TestTextualConvention"].getDescription() == "Test TC\n", "bad DESCRIPTION"

    def test_textual_convention_reference(self, pysnmp_classes):
        assert pysnmp_classes["TestTextualConvention"].getReference() == "Test reference", "bad REFERENCE"

    def test_textual_convention_class(self, pysnmp_classes):
        assert pysnmp_classes["TestTextualConvention"].__class__.__name__ == "TextualConvention", "bad SYNTAX class"


# XXX constraints flavor not checked

if __name__ == "__main__":
    pytest.main()
