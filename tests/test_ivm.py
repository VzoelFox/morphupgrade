# tests/test_ivm.py
import pytest
from io import StringIO
import sys

# Komponen dari arsitektur lama (parser)
from transisi.lx import Leksikal
from transisi.crusher import Pengurai

# Komponen dari arsitektur baru (compiler & vm)
from ivm import hir
from ivm.frontend import HIRConverter
from ivm.compiler import Compiler
from ivm.vm import VirtualMachine

def test_full_compilation_pipeline(capsys):
    """
    Tes integrasi end-to-end untuk alur kerja penuh:
    String Kode -> Lexer -> Parser -> AST -> HIR -> Compiler -> Bytecode -> VM -> Output
    """
    kode_sumber = "tulis(1 + 2);"

    # 1. Parsing (AST Generation)
    lexer = Leksikal(kode_sumber, "<test>")
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_tree = parser.urai()
    assert ast_tree is not None

    # 2. Konversi AST ke HIR
    hir_converter = HIRConverter()
    hir_tree = hir_converter.convert(ast_tree)

    # (Opsional) Verifikasi struktur HIR
    assert isinstance(hir_tree.body[0].expression.args[0], hir.BinaryOperation)

    # 3. Kompilasi HIR ke Bytecode
    compiler = Compiler()
    code_obj = compiler.compile(hir_tree)

    # 4. Eksekusi Bytecode di VM
    vm = VirtualMachine()
    vm.run(code_obj)

    # 5. Verifikasi Output
    captured = capsys.readouterr()
    assert captured.out.strip() == "3"
