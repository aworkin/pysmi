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
              TRAP-TYPE
                FROM RFC-1215
            
              OBJECT-TYPE
                FROM RFC1155-SMI;
            
            testId  OBJECT IDENTIFIER ::= { 1 3 }
            
            testObject OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      accessible-for-notify
                STATUS          current
                DESCRIPTION     "Test object"
             ::= { 1 3 }
            
            testTrap     TRAP-TYPE
                    ENTERPRISE  testId
                    VARIABLES { testObject }
                    DESCRIPTION
                            "Test trap"
              ::= 1
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestTrapType:
    def test_trap_type_symbol(self, pysnmp_classes):
        assert "testTrap" in pysnmp_classes, "symbol not present"

    def test_trap_type_name(self, pysnmp_classes):
        assert pysnmp_classes["testTrap"].getName() == (1, 3, 0, 1), "bad name"

    def test_trap_type_description(self, pysnmp_classes):
        assert pysnmp_classes["testTrap"].getDescription() == "Test trap\n", "bad DESCRIPTION"

    def test_trap_type_class(self, pysnmp_classes):
        assert pysnmp_classes["testTrap"].__class__.__name__ == "NotificationType", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
