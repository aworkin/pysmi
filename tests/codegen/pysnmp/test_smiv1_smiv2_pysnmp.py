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
                    Counter, IpAddress, TimeTicks
                        FROM RFC1155-SMI
                    DisplayString, mib-2
                        FROM RFC1213-MIB
                    OBJECT-TYPE
                        FROM RFC-1212
                
                    NOTIFICATION-GROUP
                        FROM SNMPv2-CONF;
                
                testSmiV1 NOTIFICATION-GROUP
                   NOTIFICATIONS    {
                                        testStatusChangeNotify,
                                        testClassEventNotify,
                                        testThresholdBelowNotify
                                    }
                    STATUS          current
                    DESCRIPTION
                        "A collection of test notifications."
                 ::= { 1 3 }
                
                END
                """
        ),
    ),
    indirect=True,
)
class TestSmiV1:
    def test_smi_v1_symbol(self, pysnmp_classes):
        assert "testSmiV1" in pysnmp_classes, "symbol not present"

    def test_smi_v1_name(self, pysnmp_classes):
        assert pysnmp_classes["testSmiV1"].getName() == (1, 3), "bad name"

    def test_smi_v1_description(self, pysnmp_classes):
        assert (
            pysnmp_classes["testSmiV1"].getDescription() == "A collection of test notifications.\n"
        ), "bad DESCRIPTION"

    def test_smi_v1_class(self, pysnmp_classes):
        assert pysnmp_classes["testSmiV1"].__class__.__name__ == "NotificationGroup", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
