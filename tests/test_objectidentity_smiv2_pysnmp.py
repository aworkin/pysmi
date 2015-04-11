try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysnmp.smi.builder import MibBuilder

class ObjectIdentityTestCase(unittest.TestCase):
    """
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

    def setUp(self):
        self.otherMibs, pycode = SmiV2Parser().parse(self.__class__.__doc__)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testObjectIdentitySymbol(self):
        self.assertTrue(
            'testObject' in self.ctx,
            'symbol not present'
        )

    def testObjectIdentityName(self):
        self.assertEqual(
            self.ctx['testObject'].getName(),
            (1, 3),
            'bad name'
        )

    def testObjectIdentityDescription(self):
        self.assertEqual(
            self.ctx['testObject'].getDescription(),
            'This is the MIB module for the SNMP',
            'bad DESCRIPTION'
        )

    def testObjectIdentityReference(self):
        self.assertEqual(
            self.ctx['testObject'].getReference(),
            'ABC',
            'bad REFERENCE'
        )

    def testObjectIdentityClass(self):
        self.assertEqual(
            self.ctx['testObject'].__class__.__name__,
            'ObjectIdentity',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()