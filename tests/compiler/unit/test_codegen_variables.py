# tests/compiler/unit/test_codegen_variables.py

import pytest
from llvmlite import ir
from compiler.codegen_llvm import LLVMCodeGenerator
from morph_engine.node_ast import NodeDeklarasiVariabel, NodePengenal, NodeAngka
from morph_engine.token_morph import Token, TipeToken

def setup_codegen_with_builder():
    """Helper untuk setup codegen dengan builder aktif."""
    codegen = LLVMCodeGenerator()
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)
    return codegen

def test_visit_node_deklarasi_variabel():
    """Tes visitor untuk NodeDeklarasiVariabel."""
    codegen = setup_codegen_with_builder()

    # Node untuk 'biar x = 10'
    node_angka = NodeAngka(Token(TipeToken.ANGKA, 10))
    node_nama = Token(TipeToken.PENGENAL, "x")
    jenis_decl = Token(TipeToken.BIAR, "biar")
    node_decl = NodeDeklarasiVariabel(jenis_decl, node_nama, node_angka)

    codegen.visit_NodeDeklarasiVariabel(node_decl)

    # Verifikasi
    assert "x" in codegen.symbol_table
    var_ptr = codegen.symbol_table["x"]
    assert isinstance(var_ptr, ir.AllocaInstr)
    assert var_ptr.type == ir.PointerType(ir.IntType(32))

    # Periksa instruksi yang dihasilkan
    ir_output = str(codegen.builder.block)
    assert '%"x" = alloca i32' in ir_output
    assert 'store i32 10, i32* %"x"' in ir_output

def test_visit_node_pengenal():
    """Tes visitor untuk NodePengenal (akses variabel)."""
    codegen = setup_codegen_with_builder()

    # Setup variabel 'y' di symbol table
    var_ptr = codegen.builder.alloca(ir.IntType(32), name="y")
    codegen.builder.store(ir.Constant(ir.IntType(32), 99), var_ptr)
    codegen.symbol_table["y"] = var_ptr

    # Node untuk 'y'
    node_pengenal = NodePengenal(Token(TipeToken.PENGENAL, "y"))

    result = codegen.visit_NodePengenal(node_pengenal)

    assert isinstance(result, ir.LoadInstr)

    # Periksa instruksi load yang dihasilkan
    ir_output = str(codegen.builder.block)
    # Cukup periksa apakah ada operasi load dari pointer %y
    assert 'load i32, i32* %"y"' in ir_output

def test_visit_node_pengenal_not_found():
    """Tes error ketika mengakses variabel yang tidak ada."""
    codegen = setup_codegen_with_builder()
    node_pengenal = NodePengenal(Token(TipeToken.PENGENAL, "z"))

    with pytest.raises(NameError, match="Variabel 'z' belum dideklarasikan."):
        codegen.visit_NodePengenal(node_pengenal)
