import typing as t

import pytest
from pysnmp.smi.builder import MibBuilder

from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysmi.parser.smi import parserFactory

if t.TYPE_CHECKING:
    from pysmi.mibinfo import MibInfo


@pytest.fixture(scope="session")
def parser():
    return parserFactory()()


@pytest.fixture(scope="session")
def symtable_generator():
    return SymtableCodeGen()


@pytest.fixture(scope="session")
def pysnmp_generator():
    return PySnmpCodeGen()


@pytest.fixture()
def mib_document(request):
    return getattr(request, "param", "")


@pytest.fixture()
def ast(parser, mib_document):
    return parser.parse(mib_document)[0]


@pytest.fixture()
def symtable(ast, symtable_generator) -> dict[str, list]:
    return symtable_generator.genCode(ast, {}, genTexts=True)[1]


@pytest.fixture()
def symtable_mib_info(ast, symtable_generator) -> "MibInfo":
    return symtable_generator.genCode(ast, {}, genTexts=True)[0]


@pytest.fixture()
def pysnmp_code_str(ast, pysnmp_generator, symtable_mib_info, symtable) -> str:
    return pysnmp_generator.genCode(ast, {symtable_mib_info.name: symtable}, genTexts=True)[1]


@pytest.fixture()
def pysnmp_mib_info(ast, pysnmp_generator, symtable_mib_info, symtable) -> "MibInfo":
    return pysnmp_generator.genCode(ast, {symtable_mib_info.name: symtable}, genTexts=True)[0]


@pytest.fixture()
def pysnmp_code(pysnmp_code_str):
    return compile(pysnmp_code_str, "test", "exec")


@pytest.fixture()
def mib_builder():
    mib_builder = MibBuilder()
    mib_builder.loadTexts = True
    return mib_builder


@pytest.fixture()
def pysnmp_classes(pysnmp_code, mib_builder):
    ctx = {"mibBuilder": mib_builder}
    exec(pysnmp_code, ctx, ctx)
    del ctx["mibBuilder"]
    return ctx
