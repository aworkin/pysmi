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
                  NOTIFICATION-TYPE
                    FROM SNMPv2-SMI;
            
                testNotificationType NOTIFICATION-TYPE
                   OBJECTS         {
                                        testChangeConfigType,
                                        testChangeConfigValue
                                    }
                    STATUS          current
                    DESCRIPTION
                        "A collection of test notification types."
                 ::= { 1 3 }
            
                END
                """
        ),
    ),
    indirect=True,
)
class TestNotificationType:
    def test_notification_type_symbol(self, pysnmp_classes):
        assert "testNotificationType" in pysnmp_classes, "symbol not present"

    def test_notification_type_name(self, pysnmp_classes):
        assert pysnmp_classes["testNotificationType"].getName() == (1, 3), "bad name"

    def test_notification_type_description(self, pysnmp_classes):
        assert (
            pysnmp_classes["testNotificationType"].getDescription() == "A collection of test notification types.\n"
        ), "bad DESCRIPTION"

    def test_notification_type_class(self, pysnmp_classes):
        assert pysnmp_classes["testNotificationType"].__class__.__name__ == "NotificationType", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
