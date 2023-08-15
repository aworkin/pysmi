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
                 MODULE-IDENTITY
                    FROM SNMPv2-SMI;
            
                testModule MODULE-IDENTITY
                 LAST-UPDATED "200001100000Z" -- Midnight 10 January 2000
                 ORGANIZATION "AgentX Working Group"
                 CONTACT-INFO "WG-email:   agentx@dorothy.bmc.com"
                 DESCRIPTION  "This is the MIB module for the SNMP"
                 REVISION     "200001100000Z" -- Midnight 10 January 2000
                 DESCRIPTION  "Initial version published as RFC 2742."
                 ::= { 1 3 }
            
                END
                """
        ),
    ),
    indirect=True,
)
class TestModuleIdentity:
    def test_module_identity_symbol(self, pysnmp_classes):
        assert "testModule" in pysnmp_classes, "symbol not present"

    def test_module_identity_name(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].getName() == (1, 3), "bad name"

    def test_module_identity_last_updated(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].getLastUpdated() == "200001100000Z", "bad LAST-UPDATED"

    def test_module_identity_organization(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].getOrganization() == "AgentX Working Group\n", "bad ORGANIZATION"

    def test_module_identity_revisions(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].getRevisions() == ("2000-01-10 00:00",), "bad REVISIONS"

    # TODO: pysnmp does not implement .getRevisionsDescriptions()
    #        self.assertEqual(
    #            pysnmp_classes['testModule'].getRevisionsDescriptions(),
    #            ('Initial version published as RFC 2742.',),
    #            'bad REVISIONS'
    #        )

    def test_module_identity_contact_info(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].getContactInfo() == "WG-email: agentx@dorothy.bmc.com\n", "bad CONTACT-INFO"

    def test_module_identity_description(self, pysnmp_classes):
        assert (
            pysnmp_classes["testModule"].getDescription() == "This is the MIB module for the SNMP\n"
        ), "bad DESCRIPTION"

    def test_module_identity_class(self, pysnmp_classes):
        assert pysnmp_classes["testModule"].__class__.__name__ == "ModuleIdentity", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
