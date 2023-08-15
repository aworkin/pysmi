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
                      OBJECT-GROUP
                        FROM SNMPv2-CONF;
                
                    testObjectGroup OBJECT-GROUP
                        OBJECTS         {
                                            testStorageType,
                                            testRowStatus
                                        }
                        STATUS          current
                        DESCRIPTION
                            "A collection of test objects."
                     ::= { 1 3 }
                
                    END
                    """
        ),
    ),
    indirect=True,
)
class TestObjectGroup:
    def test_object_group_symbol(self, pysnmp_classes):
        assert "testObjectGroup" in pysnmp_classes, "symbol not present"

    def test_object_group_name(self, pysnmp_classes):
        assert pysnmp_classes["testObjectGroup"].getName() == (1, 3), "bad name"

    def test_object_group_description(self, pysnmp_classes):
        assert (
            pysnmp_classes["testObjectGroup"].getDescription() == "A collection of test objects.\n"
        ), "bad DESCRIPTION"

    def test_object_group_objects(self, pysnmp_classes):
        assert pysnmp_classes["testObjectGroup"].getObjects() == (
            ("TEST-MIB", "testStorageType"),
            ("TEST-MIB", "testRowStatus"),
        ), "bad OBJECTS"

    def test_object_group_class(self, pysnmp_classes):
        assert pysnmp_classes["testObjectGroup"].__class__.__name__ == "ObjectGroup", "bad SYNTAX class"


if __name__ == "__main__":
    pytest.main()
