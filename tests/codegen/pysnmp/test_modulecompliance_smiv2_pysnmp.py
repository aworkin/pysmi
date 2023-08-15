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
                  MODULE-COMPLIANCE
                    FROM SNMPv2-CONF;
            
                testCompliance MODULE-COMPLIANCE
                 STATUS      current
                 DESCRIPTION  "This is the MIB compliance statement"
                 MODULE
                  MANDATORY-GROUPS {
                   testComplianceInfoGroup,
                   testNotificationInfoGroup
                  }
                  GROUP     testNotificationGroup
                  DESCRIPTION
                        "Support for these notifications is optional."
                  ::= { 1 3 }
            
                END
                """
        ),
    ),
    indirect=True,
)
class TestModuleCompliance:
    def test_module_compliance_symbol(self, pysnmp_classes):
        assert "testCompliance" in pysnmp_classes, "symbol not present"

    def test_module_compliance_name(self, pysnmp_classes):
        assert pysnmp_classes["testCompliance"].getName() == (1, 3), "bad name"

    def test_module_compliance_description(self, pysnmp_classes):
        assert (
            pysnmp_classes["testCompliance"].getDescription() == "This is the MIB compliance statement\n"
        ), "bad DESCRIPTION"

    def test_module_compliance_class(self, pysnmp_classes):
        assert pysnmp_classes["testCompliance"].__class__.__name__ == "ModuleCompliance", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()