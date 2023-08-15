#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
from textwrap import dedent

import pytest


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
             MODULE-IDENTITY, OBJECT-TYPE, Unsigned32, mib-2
                FROM SNMPv2-SMI
             SnmpAdminString
                FROM SNMP-FRAMEWORK-MIB;
                
            END
            """
        ),
    ),
    indirect=True,
)
class TestImportClause:
    def test_module_imports_required_mibs(self, pysnmp_mib_info):
        assert pysnmp_mib_info.imported == (
            "SNMP-FRAMEWORK-MIB",
            "SNMPv2-CONF",
            "SNMPv2-SMI",
            "SNMPv2-TC",
        ), "imported MIBs not reported"

    def test_module_check_imported_symbol(self, pysnmp_classes):
        assert "SnmpAdminString" in pysnmp_classes, "imported symbol not present"


if __name__ == "__main__":
    pytest.main()
