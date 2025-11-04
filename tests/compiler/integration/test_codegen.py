# tests/compiler/integration/test_codegen.py

import pytest
from llvmlite import ir

# Impor komponen dari compiler dan interpreter
from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from compiler.codegen_llvm import LLVMCodeGenerator

def test_codegen_integration_basic():
    """
    Tes integrasi end-to-end untuk kompilasi program sederhana.
    Memverifikasi deklarasi variabel, akses, dan pemanggilan fungsi 'tulis'.
    """
    code = "biar x = 42\ntulis(x)"

    # 1. Parsing
    tokens = Leksikal(code).buat_token()
    ast = Pengurai(tokens).urai()
    assert ast is not None, "Gagal mengurai kode sumber."

    # 2. Code Generation
    codegen = LLVMCodeGenerator()
    ir_module = codegen.generate_code(ast)
    ir_output = str(ir_module)

    # 3. Validasi Output IR
    # Pastikan fungsi main didefinisikan
    assert 'define i32 @"main"()' in ir_output

    # Pastikan ada alokasi memori untuk variabel 'x'
    assert '%"x" = alloca i32' in ir_output

    # Pastikan nilai 42 disimpan ke 'x'
    assert 'store i32 42, i32* %"x"' in ir_output

    # Pastikan nilai 'x' dimuat kembali untuk digunakan
    assert 'load i32, i32* %"x"' in ir_output

    # Pastikan fungsi printf dipanggil
    assert 'call i32 (i8*, ...) @"printf"' in ir_output

    # Pastikan format string untuk integer didefinisikan
    assert '@"format_int" = internal constant [4 x i8] c"%d\\0a\\00"' in ir_output

    # Pastikan fungsi 'main' mengembalikan 0
    assert 'ret i32 0' in ir_output

def test_codegen_arithmetic_integration():
    """
    Tes integrasi untuk kompilasi ekspresi aritmatika.
    """
    code = "tulis(10 + 2 * 3)" # Hasilnya harus 16

    # 1. Parsing
    tokens = Leksikal(code).buat_token()
    ast = Pengurai(tokens).urai()
    assert ast is not None

    # 2. Code Generation
    codegen = LLVMCodeGenerator()
    ir_module = codegen.generate_code(ast)
    ir_output = str(ir_module)

    # 3. Validasi
    # Periksa urutan operasi: perkalian dulu, baru penjumlahan
    assert '%"multmp" = mul i32 2, 3' in ir_output
    assert '%"addtmp" = add i32 10, %"multmp"' in ir_output
    assert 'call i32 (i8*, ...) @"printf"' in ir_output
