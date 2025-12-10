# tests/compiler/unit/test_codegen_errors.py

import pytest
from llvmlite import ir
from morphupgrade.morph_engine_py.leksikal import Leksikal
from morphupgrade.morph_engine_py.pengurai import Pengurai
from compiler.codegen_llvm import LLVMCodeGenerator

@pytest.mark.compiler
@pytest.mark.unit
class TestCodegenValidation:
    """Tes untuk validasi dan penanganan error di code generator."""

    def test_if_condition_not_boolean_raises_type_error(self):
        """
        Memastikan TypeError dilemparkan jika kondisi 'jika' bukan boolean.
        Contoh: 'jika 10 maka ...'
        """
        code = """
        jika 10 maka
            tulis(1)
        akhir
        """
        tokens = Leksikal(code).buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()

        codegen = LLVMCodeGenerator()

        # Replikasi setup minimal dari generate_code untuk memungkinkan visit() berjalan
        func_type = ir.FunctionType(ir.IntType(32), [])
        main_func = ir.Function(codegen.module, func_type, name="main")
        block = main_func.append_basic_block("entry")
        codegen.builder = ir.IRBuilder(block)

        with pytest.raises(TypeError) as excinfo:
            # Panggil visit() secara langsung untuk melewati try-except di generate_code
            codegen.visit(ast)

        assert "Kondisi 'jika' harus berupa ekspresi boolean" in str(excinfo.value)
        assert "bukan tipe i32" in str(excinfo.value)
        assert "pada baris 2" in str(excinfo.value)

    def test_codegen_graceful_recovery_on_error(self, capsys):
        """
        Memastikan compiler tidak crash dan mengembalikan modul yang valid
        saat terjadi error tak terduga.
        """
        code = """
        # Kode ini akan menyebabkan error karena 'variabel_tidak_ada'
        # tidak dideklarasikan, memicu NameError.
        tulis(variabel_tidak_ada)
        """
        tokens = Leksikal(code).buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()

        codegen = LLVMCodeGenerator()

        # Panggil generate_code, yang seharusnya menangani error
        ir_module = codegen.generate_code(ast)
        ir_output = str(ir_module)

        # 1. Verifikasi pesan error di stderr
        captured = capsys.readouterr()
        assert "; MORPH Compilation Error:" in captured.err
        assert "Variabel 'variabel_tidak_ada' belum dideklarasikan." in captured.err
        assert "; Compilation aborted due to fatal error." in captured.err

        # 2. Verifikasi modul yang dikembalikan adalah modul error yang valid
        assert 'ModuleID = "morph_program_error"' in ir_output
        assert 'define i32 @"main"()' in ir_output
        assert 'ret i32 1' in ir_output # Exit code 1
