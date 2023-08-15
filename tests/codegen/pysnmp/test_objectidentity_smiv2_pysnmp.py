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
                OBJECT-IDENTITY
            FROM SNMPv2-SMI;
        
            testObject OBJECT-IDENTITY
                STATUS          current
                DESCRIPTION     "Initial version"
                REFERENCE       "ABC"
        
             ::= { 1 3 }
        
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectIdentity:
    def test_object_identity_symbol(self, pysnmp_classes):
        assert "testObject" in pysnmp_classes, "symbol not present"

    def test_object_identity_name(self, pysnmp_classes):
        assert pysnmp_classes["testObject"].getName() == (1, 3), "bad name"

    def test_object_identity_description(self, pysnmp_classes):
        assert pysnmp_classes["testObject"].getDescription() == "Initial version\n", "bad DESCRIPTION"

    def test_object_identity_reference(self, pysnmp_classes):
        assert pysnmp_classes["testObject"].getReference() == "ABC\n", "bad REFERENCE"

    def test_object_identity_class(self, pysnmp_classes):
        assert pysnmp_classes["testObject"].__class__.__name__ == "ObjectIdentity", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
