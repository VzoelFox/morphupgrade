# tests/compiler/integration/test_codegen_control_flow.py

import pytest
from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from compiler.codegen_llvm import LLVMCodeGenerator

def compile_code_to_ir(source_code):
    """Helper untuk pipeline kompilasi: Teks -> Token -> AST -> LLVM IR."""
    tokens = Leksikal(source_code).buat_token()
    parser = Pengurai(tokens)
    ast = parser.urai()
    assert not parser.daftar_kesalahan, "Terjadi kesalahan saat parsing."

    codegen = LLVMCodeGenerator()
    ir_module = codegen.generate_code(ast)
    return str(ir_module)

@pytest.mark.integration
@pytest.mark.compiler
class TestCodegenControlFlow:
    """Tes integrasi untuk code generation struktur kontrol."""

    def test_simple_if_true(self):
        """Tes 'jika' dengan kondisi yang selalu benar."""
        code = """
        jika 10 > 5 maka
            tulis(1)
        akhir
        """
        ir_output = compile_code_to_ir(code)

        # Verifikasi
        assert 'define i32 @"main"()' in ir_output
        # Periksa perbandingan (icmp)
        assert 'icmp sgt i32 10, 5' in ir_output
        # Periksa conditional branch, llvmlite menambahkan quotes
        assert 'br i1 %"cmptmp", label %"maka", label %"lain"' in ir_output
        # Periksa blok 'maka' berisi pemanggilan printf
        assert '\nmaka:' in ir_output
        assert 'call i32 (i8*, ...) @"printf"' in ir_output
        # Periksa blok 'lain' kosong
        assert '\nlain:' in ir_output
        # Periksa semua cabang menuju ke merge block
        assert 'br label %"setelah_jika"' in ir_output
        assert '\nsetelah_jika:' in ir_output

    def test_if_else_false(self):
        """Tes 'jika-lain' dengan kondisi yang selalu salah."""
        code = """
        jika 2 > 100 maka
            tulis(1)
        lain
            tulis(0)
        akhir
        """
        ir_output = compile_code_to_ir(code)

        # Periksa perbandingan
        assert 'icmp sgt i32 2, 100' in ir_output
        # Periksa bahwa printf dipanggil dengan nilai 1 di blok 'maka'
        maka_block_start = ir_output.find('\nmaka:')
        assert 'call i32 (i8*, ...) @"printf"(i8* getelementptr ([4 x i8], [4 x i8]* @"format_int", i32 0, i32 0), i32 1)' in ir_output[maka_block_start:]
        # Periksa bahwa printf dipanggil dengan nilai 0 di blok 'lain'
        lain_block_start = ir_output.find('\nlain:')
        assert 'call i32 (i8*, ...) @"printf"(i8* getelementptr ([4 x i8], [4 x i8]* @"format_int", i32 0, i32 0), i32 0)' in ir_output[lain_block_start:]

    def test_if_elseif_else(self):
        """Tes rantai 'jika - lain jika - lain'."""
        code = """
        biar x = 50
        jika x > 100 maka
            tulis(1)
        lain jika x > 20 maka
            tulis(2)
        lain
            tulis(3)
        akhir
        """
        ir_output = compile_code_to_ir(code)

        # Periksa keberadaan perbandingan dengan nama variabel yang benar
        assert 'icmp sgt i32 %"x.1", 100' in ir_output
        assert 'icmp sgt i32 %"x.2", 20' in ir_output

        # Periksa keberadaan label-label penting
        assert '\nmaka:' in ir_output
        assert '\nlain:' in ir_output
        assert '\nmaka_lain_jika_0:' in ir_output
        assert '\nlain_berikutnya_0:' in ir_output

        # Periksa bahwa printf dipanggil dengan nilai yang benar di blok yang benar
        maka_lj_block_start = ir_output.find('\nmaka_lain_jika_0:')
        assert 'call i32 (i8*, ...) @"printf"(i8* getelementptr ([4 x i8], [4 x i8]* @"format_int", i32 0, i32 0), i32 2)' in ir_output[maka_lj_block_start:]

        lain_final_block_start = ir_output.find('\nlain_berikutnya_0:')
        assert 'call i32 (i8*, ...) @"printf"(i8* getelementptr ([4 x i8], [4 x i8]* @"format_int", i32 0, i32 0), i32 3)' in ir_output[lain_final_block_start:]
