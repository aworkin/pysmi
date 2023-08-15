#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import unittest
from textwrap import dedent

import pytest
from pyasn1.compat.octets import str2octs
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
        
            testObjectType OBJECT-TYPE
                SYNTAX          Integer32
                UNITS           "seconds"
                MAX-ACCESS      accessible-for-notify
                STATUS          current
                DESCRIPTION     "Test object"
                REFERENCE       "ABC"
             ::= { 1 3 }
        
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeBasic:
    def test_object_type_symbol(self, pysnmp_classes):
        assert "testObjectType" in pysnmp_classes, "symbol not present"

    def test_object_type_name(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getName() == (1, 3), "bad name"

    def test_object_type_description(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getDescription() == "Test object\n", "bad DESCRIPTION"

    def test_object_type_status(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getStatus() == "current", "bad STATUS"

    # TODO:revisit
    #    def testObjectTypeReference(self):
    #        self.assertEqual(
    #            pysnmp_classes['testObjectType'].getReference(), str2octs('ABC'),
    #            'bad REFERENCE'
    #        )

    def test_object_type_max_access(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getMaxAccess() == "accessible-for-notify", "bad MAX-ACCESS"

    def test_object_type_units(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getUnits() == "seconds", "bad UNITS"

    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax().clone(123) == 123, "bad SYNTAX"

    def test_object_type_class(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].__class__.__name__ == "MibScalar", "bad SYNTAX"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE,
              Integer32
                FROM SNMPv2-SMI;
        
            testObjectType OBJECT-TYPE
                SYNTAX          Integer32
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
                DEFVAL          { 123456 }
             ::= { 1 3 }
        
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeIntegerDefault:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax() == 123456, "bad DEFVAL"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          INTEGER  {
                                    enable(1),
                                    disable(2)
                                }
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
                DEFVAL          { enable }
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeEnumDefault:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax() == 1, "bad DEFVAL"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          OCTET STRING
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
                DEFVAL          { "test value" }
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeStringDefault:
    # TODO: pyasn1 does not like OctetString.defaultValue
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax() == str2octs("test value"), "bad DEFVAL"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE,
              Unsigned32
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          Unsigned32 (0..4294967295)
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
                DEFVAL          { 0 }
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeWithIntegerConstraint:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax().clone(123) == 123, "bad integer range constrained SYNTAX"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE,
              Unsigned32
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          Unsigned32 (0|2|44)
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeWithIntegerSetConstraint:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax().clone(44) == 44, "bad multiple integer constrained SYNTAX"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE,
              Unsigned32
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          OCTET STRING (SIZE (0..512))
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeWithStringSizeConstraint:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax().clone("") == str2octs(""), "bad size constrained SYNTAX"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE,
              Unsigned32
                FROM SNMPv2-SMI;
            
            testObjectType OBJECT-TYPE
                SYNTAX          BITS { notification(0), set(1) }
                MAX-ACCESS      read-only
                STATUS          current
                DESCRIPTION     "Test object"
             ::= { 1 3 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeBits:
    def test_object_type_syntax(self, pysnmp_classes):
        assert pysnmp_classes["testObjectType"].getSyntax().clone(("set",)) == str2octs("@"), "bad BITS SYNTAX"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
              testTable OBJECT-TYPE
                SYNTAX          SEQUENCE OF TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test table"
              ::= { 1 3 }
            
              testEntry OBJECT-TYPE
                SYNTAX          TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test row"
                INDEX           { testIndex }
              ::= { testTable 1 }
            
              TestEntry ::= SEQUENCE {
                    testIndex   INTEGER,
                    testValue   OCTET STRING
              }
            
              testIndex OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 1 }
            
              testValue OBJECT-TYPE
                SYNTAX          OCTET STRING
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 2 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeMibTable:
    def test_object_type_table_class(self, pysnmp_classes):
        assert pysnmp_classes["testTable"].__class__.__name__ == "MibTable", "bad table class"

    def test_object_type_table_row_class(self, pysnmp_classes):
        assert pysnmp_classes["testEntry"].__class__.__name__ == "MibTableRow", "bad table row class"

    def test_object_type_table_column_class(self, pysnmp_classes):
        assert pysnmp_classes["testIndex"].__class__.__name__ == "MibTableColumn", "bad table column class"

    def test_object_type_table_row_index(self, pysnmp_classes):
        assert pysnmp_classes["testEntry"].getIndexNames() == ((0, "TEST-MIB", "testIndex"),), "bad table index"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
              testTable OBJECT-TYPE
                SYNTAX          SEQUENCE OF TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test table"
              ::= { 1 3 }
            
              testEntry OBJECT-TYPE
                SYNTAX          TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test row"
                INDEX           { IMPLIED testIndex }
              ::= { testTable 3 }
            
              TestEntry ::= SEQUENCE {
                    testIndex   INTEGER
              }
            
              testIndex OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 1 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeMibTableImpliedIndex:
    def test_object_type_table_row_index(self, pysnmp_classes):
        assert pysnmp_classes["testEntry"].getIndexNames() == ((1, "TEST-MIB", "testIndex"),), "bad IMPLIED table index"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
              testTable OBJECT-TYPE
                SYNTAX          SEQUENCE OF TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test table"
              ::= { 1 3 }
            
              testEntry OBJECT-TYPE
                SYNTAX          TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test row"
                INDEX           { testIndex, testValue }
              ::= { testTable 3 }
            
              TestEntry ::= SEQUENCE {
                    testIndex   INTEGER,
                    testValue   OCTET STRING
              }
            
              testIndex OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 1 }
            
              testValue OBJECT-TYPE
                SYNTAX          OCTET STRING
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 2 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeMibTableMultipleIndices:
    def test_object_type_table_row_index(self, pysnmp_classes):
        assert pysnmp_classes["testEntry"].getIndexNames() == (
            (0, "TEST-MIB", "testIndex"),
            (0, "TEST-MIB", "testValue"),
        ), "bad multiple table indices"


@pytest.mark.parametrize(
    "mib_document",
    (
        dedent(
            """\
            TEST-MIB DEFINITIONS ::= BEGIN
            IMPORTS
              OBJECT-TYPE
                FROM SNMPv2-SMI;
            
              testTable OBJECT-TYPE
                SYNTAX          SEQUENCE OF TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test table"
              ::= { 1 3 }
            
              testEntry OBJECT-TYPE
                SYNTAX          TestEntry
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test row"
                INDEX           { testIndex }
              ::= { testTable 3 }
            
              TestEntry ::= SEQUENCE {
                    testIndex   INTEGER
              }
            
              testIndex OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntry 1 }
            
              testTableExt OBJECT-TYPE
                SYNTAX          SEQUENCE OF TestEntryExt
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test table"
              ::= { 1 4 }
            
              testEntryExt OBJECT-TYPE
                SYNTAX          TestEntryExt
                MAX-ACCESS      not-accessible
                STATUS          current
                DESCRIPTION     "Test row"
                AUGMENTS        { testEntry }
              ::= { testTableExt 3 }
            
              TestEntryExt ::= SEQUENCE {
                    testIndexExt   INTEGER
              }
            
              testIndexExt OBJECT-TYPE
                SYNTAX          INTEGER
                MAX-ACCESS      read-create
                STATUS          current
                DESCRIPTION     "Test column"
              ::= { testEntryExt 1 }
            
            END
            """
        ),
    ),
    indirect=True,
)
class TestObjectTypeAurmentingMibTable:
    def test_object_type_table_row_augmention(self, pysnmp_classes):
        # TODO: provide getAugmentation() method
        try:
            augmentingRows = pysnmp_classes["testEntry"].augmentingRows

        except AttributeError:
            augmentingRows = pysnmp_classes["testEntry"]._augmentingRows

        assert next(iter(augmentingRows)) == ("TEST-MIB", "testEntryExt"), "bad AUGMENTS table clause"


if __name__ == "__main__":
    pytest.main()
