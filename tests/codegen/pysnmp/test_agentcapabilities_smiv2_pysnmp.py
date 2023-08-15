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
                    MODULE-IDENTITY
                        FROM SNMPv2-SMI
                    AGENT-CAPABILITIES
                        FROM SNMPv2-CONF;
    
                testCapability AGENT-CAPABILITIES
                    PRODUCT-RELEASE "Test produce"
                    STATUS          current
                    DESCRIPTION
                        "test capabilities"
    
                    SUPPORTS        TEST-MIB
                    INCLUDES        {
                                        testSystemGroup,
                                        testNotificationObjectGroup,
                                        testNotificationGroup
                                    }
                    VARIATION       testSysLevelType
                    ACCESS          read-only
                    DESCRIPTION
                        "Not supported."
    
                    VARIATION       testSysLevelType
                    ACCESS          read-only
                    DESCRIPTION
                        "Supported."
    
                 ::= { 1 3 }
    
                END
                """
        ),
    ),
    indirect=True,
)
class TestAgentCapabilities:
    def test_agent_capabilities_symbol(self, pysnmp_classes):
        assert "testCapability" in pysnmp_classes, "symbol not present"

    def test_agent_capabilities_name(self, pysnmp_classes):
        assert pysnmp_classes["testCapability"].getName() == (1, 3), "bad name"

    def test_agent_capabilities_description(self, pysnmp_classes):
        assert pysnmp_classes["testCapability"].getDescription() == "test capabilities\n", "bad DESCRIPTION"

    # XXX SUPPORTS/INCLUDES/VARIATION/ACCESS not supported by pysnmp

    def test_agent_capabilities_class_name(self, pysnmp_classes):
        assert pysnmp_classes["testCapability"].__class__.__name__ == "AgentCapabilities", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
