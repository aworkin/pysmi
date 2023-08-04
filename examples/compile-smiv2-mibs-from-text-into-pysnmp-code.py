"""
Compile SMIv2 MIBs
++++++++++++++++++

Invoke user callback function to provide MIB text,
compile given text string into pysnmp MIB form and pass
results to another user callback function for storing.

Here we expect to deal only with SMIv2-valid MIBs.

We use noDeps flag to prevent MIB compiler from attempting
to compile IMPORT'ed MIBs as well.
"""  #
import sys
from pathlib import Path

from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler
from pysmi.parser import SmiV2Parser
from pysmi.reader import CallbackReader
from pysmi.searcher import StubSearcher
from pysmi.writer import CallbackWriter

inputMibs = ["IF-MIB", "IP-MIB"]
srcDir = "/usr/share/snmp/mibs/"  # we will read MIBs from here

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    SmiV2Parser(),
    PySnmpCodeGen(),
    # our own callback function stores results in its own way
    CallbackWriter(lambda m, d, c: sys.stdout.write(d)),
)

# our own callback function serves as a MIB source here
mibCompiler.addSources(CallbackReader(lambda m, c: (Path(srcDir) / f"{m}.txt").read_text()))

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*PySnmpCodeGen.baseMibs))

# run non-recursive MIB compilation
results = mibCompiler.compile(*inputMibs, **{"noDeps": True})

result_message = ", ".join([f"{k}:{results[v]}" for k, v in results.items()])
print(f"Results: {result_message}")
