"""
Compile MIBs into JSON
++++++++++++++++++++++

Look up specific ASN.1 MIBs at configured Web and FTP sites,
compile them into JSON documents and print them out to stdout.

Try to support both SMIv1 and SMIv2 flavors of SMI as well as
popular deviations from official syntax found in the wild.
"""#
from pysmi.reader import FileReader, HttpReader
from pysmi.searcher import StubSearcher
from pysmi.writer import CallbackWriter
from pysmi.parser import SmiStarParser
from pysmi.codegen import JsonCodeGen
from pysmi.compiler import MibCompiler
# from pysmi import debug

# debug.setLogger(debug.Debug('reader', 'compiler'))

inputMibs = ['IF-MIB', 'IP-MIB']
srcDirectories = ['/usr/share/snmp/mibs']
httpSources = [
    ('mibs.snmplabs.com', 80, '/asn1/@mib@')
]


def printOut(mibName, jsonDoc, cbCtx):
    print(f'\n\n# MIB module {mibName}')
    print(jsonDoc)

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    SmiStarParser(), JsonCodeGen(), CallbackWriter(printOut)
)

# search for source MIBs here
mibCompiler.addSources(*[FileReader(x) for x in srcDirectories])

# search for source MIBs at Web sites
mibCompiler.addSources(*[HttpReader(*x) for x in httpSources])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*JsonCodeGen.baseMibs))

# run recursive MIB compilation
results = mibCompiler.compile(*inputMibs)

result_message = ', '.join([f'{k}:{results[v]}' for k, v in results.items()])
print(f'\n# Results: {result_message}')
