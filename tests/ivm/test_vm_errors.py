import pytest
from ivm.vm import VirtualMachine
from ivm.compiler import Compiler
from ivm.frontend import HIRConverter
from ivm.kesalahan import KesalahanJodoh
from transisi.lx import Leksikal
from transisi.crusher import Pengurai

def run_vm_on_code(code: str):
    """Helper untuk menjalankan kode dari source hingga eksekusi VM."""
    lexer = Leksikal(code)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_tree = parser.urai()
    assert ast_tree is not None, "Gagal mem-parse AST"

    hir_converter = HIRConverter()
    hir_tree = hir_converter.convert(ast_tree)

    compiler = Compiler()
    code_obj = compiler.compile(hir_tree)

    vm = VirtualMachine()
    return vm.run(code_obj)

def test_jodohkan_non_exhaustive_raises_kesalahan_jodoh():
    """
    Memverifikasi bahwa VM melempar KesalahanJodoh ketika pernyataan
    'jodohkan' tidak memiliki kasus yang cocok.
    """
    code = """
    jodohkan 100 maka
        dengan 1 maka
            tulis(1)
        dengan 2 maka
            tulis(2)
    akhir
    """
    with pytest.raises(KesalahanJodoh) as excinfo:
        run_vm_on_code(code)

    assert "Tidak ada pola `jodohkan` yang cocok" in str(excinfo.value)
