# tests/compiler/unit/test_codegen_scope.py

import pytest
from llvmlite import ir
from compiler.codegen_llvm import LLVMCodeGenerator
from morph_engine.node_ast import NodeDeklarasiVariabel, NodeNama, NodeKonstanta
from morph_engine.token_morph import Token, TipeToken

def setup_codegen_with_builder():
    """Helper untuk setup codegen dengan builder aktif."""
    codegen = LLVMCodeGenerator()
    func_type = ir.FunctionType(ir.VoidType(), [])
    func = ir.Function(codegen.module, func_type, name="test_func")
    block = func.append_basic_block("entry")
    codegen.builder = ir.IRBuilder(block)
    return codegen

def test_variable_shadowing():
    """
    Tes bahwa variabel di scope dalam (inner) menutupi (shadows)
    variabel dengan nama yang sama di scope luar (outer).
    """
    codegen = setup_codegen_with_builder()

    # 1. Deklarasi 'x' di scope global
    token_angka_global = Token(TipeToken.ANGKA, 10)
    node_angka_global = NodeKonstanta(token_angka_global, token_angka_global.nilai)
    node_nama_global = NodeNama(Token(TipeToken.PENGENAL, "x"))
    node_decl_global = NodeDeklarasiVariabel(Token(TipeToken.BIAR, "biar"), node_nama_global, node_angka_global)
    codegen.visit_NodeDeklarasiVariabel(node_decl_global)

    # Simpan pointer global
    global_x_ptr = codegen.lookup_variable("x")
    assert global_x_ptr is not None

    # 2. Masuk ke scope baru dan deklarasikan 'x' lagi
    codegen.enter_scope()
    token_angka_local = Token(TipeToken.ANGKA, 20)
    node_angka_local = NodeKonstanta(token_angka_local, token_angka_local.nilai)
    node_nama_local = NodeNama(Token(TipeToken.PENGENAL, "x"))
    node_decl_local = NodeDeklarasiVariabel(Token(TipeToken.BIAR, "biar"), node_nama_local, node_angka_local)
    codegen.visit_NodeDeklarasiVariabel(node_decl_local)

    # Simpan pointer local dan verifikasi berbeda
    local_x_ptr = codegen.lookup_variable("x")
    assert local_x_ptr is not None
    assert local_x_ptr != global_x_ptr

    # Verifikasi bahwa 'x' sekarang merujuk ke versi lokal
    node_nama_local_ref = NodeNama(Token(TipeToken.PENGENAL, "x"))
    val_local_load_instr = codegen.visit_NodeNama(node_nama_local_ref)
    assert val_local_load_instr.operands[0] == local_x_ptr

    # 3. Keluar dari scope
    codegen.exit_scope()

    # Verifikasi bahwa 'x' sekarang merujuk kembali ke versi global
    final_x_ptr = codegen.lookup_variable("x")
    assert final_x_ptr == global_x_ptr

def test_scope_isolation():
    """
    Tes bahwa variabel yang dideklarasikan di scope dalam tidak
    bisa diakses dari scope luar.
    """
    codegen = setup_codegen_with_builder()

    codegen.enter_scope()
    # Deklarasi 'y' di scope lokal
    token_angka = Token(TipeToken.ANGKA, 30)
    node_angka = NodeKonstanta(token_angka, token_angka.nilai)
    node_nama = NodeNama(Token(TipeToken.PENGENAL, "y"))
    node_decl = NodeDeklarasiVariabel(Token(TipeToken.BIAR, "biar"), node_nama, node_angka)
    codegen.visit_NodeDeklarasiVariabel(node_decl)
    codegen.exit_scope()

    # Coba akses 'y' dari scope global (seharusnya gagal)
    node_nama_ref = NodeNama(Token(TipeToken.PENGENAL, "y"))
    with pytest.raises(NameError, match="Variabel 'y' belum dideklarasikan."):
        codegen.visit_NodeNama(node_nama_ref)

def test_nested_scope_access():
    """
    Tes bahwa scope dalam bisa mengakses variabel dari scope luar
    jika tidak di-shadow.
    """
    codegen = setup_codegen_with_builder()

    # Deklarasi 'z' di scope global
    token_angka = Token(TipeToken.ANGKA, 40)
    node_angka = NodeKonstanta(token_angka, token_angka.nilai)
    node_nama = NodeNama(Token(TipeToken.PENGENAL, "z"))
    node_decl = NodeDeklarasiVariabel(Token(TipeToken.BIAR, "biar"), node_nama, node_angka)
    codegen.visit_NodeDeklarasiVariabel(node_decl)

    # Masuk ke scope baru
    codegen.enter_scope()

    # Akses 'z' dari scope dalam
    node_nama_ref = NodeNama(Token(TipeToken.PENGENAL, "z"))
    val_nested = codegen.visit_NodeNama(node_nama_ref)
    assert val_nested.operands[0] == codegen.lookup_variable("z")

    # Keluar dari scope
    codegen.exit_scope()
