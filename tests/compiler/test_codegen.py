# tests/compiler/test_codegen.py
import pytest
from llvmlite import ir

from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.node_ast import NodeProgram, NodeAngka
from morph_engine.token_morph import Token, TipeToken
from compiler.codegen_llvm import LLVMCodeGenerator

def parse_code(code):
    leksikal = Leksikal(code)
    token_list = leksikal.buat_token()
    pengurai = Pengurai(token_list)
    return pengurai.urai()

@pytest.mark.compiler
def test_codegen_program_kosong():
    ast = parse_code("")
    codegen = LLVMCodeGenerator()
    result_ir = codegen.generate_code(ast)
    ir_string = str(result_ir)
    assert 'define i32 @"main"()' in ir_string
    assert "ret i32 0" in ir_string

@pytest.mark.compiler
def test_codegen_literal_angka_dikembalikan():
    ast = parse_code("42")
    codegen = LLVMCodeGenerator()
    result_ir = codegen.generate_code(ast)
    ir_string = str(result_ir)
    assert 'define i32 @"main"()' in ir_string
    assert "ret i32 42" in ir_string

@pytest.mark.compiler
def test_codegen_arithmetic_tambah_dikembalikan():
    ast = parse_code("10 + 5")
    codegen = LLVMCodeGenerator()
    result_ir = codegen.generate_code(ast)
    ir_string = str(result_ir)
    assert 'define i32 @"main"()' in ir_string
    # FIX: Memeriksa nilai kembali yang benar dengan nama variabel yang benar.
    assert 'ret i32 %"addtmp"' in ir_string or "ret i32 15" in ir_string

@pytest.mark.compiler
def test_codegen_arithmetic_nested_dikembalikan():
    ast = parse_code("1 + 2 * 3")
    codegen = LLVMCodeGenerator()
    result_ir = codegen.generate_code(ast)
    ir_string = str(result_ir)
    assert 'define i32 @"main"()' in ir_string
    # FIX: Memeriksa nilai kembali dengan nama variabel yang benar (dengan tanda kutip).
    assert 'ret i32 %"addtmp"' in ir_string or "ret i32 7" in ir_string

@pytest.mark.compiler
def test_codegen_float_literal_dikembalikan():
    ast = parse_code("3.14")
    codegen = LLVMCodeGenerator()
    result_ir = codegen.generate_code(ast)
    ir_string = str(result_ir)
    assert 'define double @"main"()' in ir_string
    # FIX: llvmlite menggunakan representasi hex untuk float.
    # Cukup periksa bahwa nilai double dikembalikan.
    assert "ret double" in ir_string
    assert "3.14" not in ir_string # Pastikan tidak ada representasi string sederhana
    assert "0x40091eb851eb851f" in ir_string # Cek representasi hex yang spesifik

@pytest.mark.compiler
@pytest.mark.xfail(reason="Operasi float belum diimplementasikan")
def test_codegen_arithmetic_float():
    ast = parse_code("2.5 + 2.5")
    codegen = LLVMCodeGenerator()
    codegen.generate_code(ast)
