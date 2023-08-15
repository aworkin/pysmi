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


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
            
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
            -- simple values
            
            testValue1  OBJECT IDENTIFIER ::= { 1 }
            testValue2  OBJECT IDENTIFIER ::= { testValue1 3 }
            testValue3  OBJECT IDENTIFIER ::= { 1 3 6 1 2 }
            
            -- testValue01  INTEGER ::= 123
            -- testValue02  INTEGER ::= -123
            -- testValue04  OCTET STRING ::= h'test string'
            -- testValue05  INTEGER ::= testValue01
            -- testValue06  OCTET STRING ::= "test string"
            -- testValue07  OCTET STRING ::= b'010101'
            
            -- application syntax
            
            -- testValue03  Integer32 ::= 123
            -- testValue03  Counter32 ::= 123
            -- testValue03  Gauge32 ::= 123
            -- testValue03  Unsigned32 ::= 123
            -- testValue03  TimeTicks ::= 123
            -- testValue03  Opaque ::= "0123"
            -- testValue03  Counter64 ::= 123456789123456789
            -- testValue03  IpAddress ::= "127.0.0.1"
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestValueDeclaration:
    def test_value_declaration_symbol(self, pysnmp_classes):
        assert (
            "testValue1" in pysnmp_classes and "testValue2" in pysnmp_classes and "testValue3" in pysnmp_classes
        ), "symbol not present"

    def test_value_declaration_name1(self, pysnmp_classes):
        assert pysnmp_classes["testValue1"].getName() == (1,), "bad value"

    def test_value_declaration_name2(self, pysnmp_classes):
        assert pysnmp_classes["testValue2"].getName() == (1, 3), "bad value"

    def test_value_declaration_name3(self, pysnmp_classes):
        assert pysnmp_classes["testValue3"].getName() == (1, 3, 6, 1, 2), "bad value"


if __name__ == "__main__":
    pytest.main()
