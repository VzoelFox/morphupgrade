import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM

def run_morph_code(code):
    lexer = Leksikal(code)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()

    if ast_node is None:
        raise RuntimeError("Parser failed")

    compiler = Compiler()
    bytecode = compiler.compile(ast_node)
    vm = StandardVM()
    vm.load(bytecode)
    vm.run()
    return vm

def test_match_multi_case_unpack_fail():
    """
    Memastikan stack bersih jika failure terjadi SETELAH unpack sequence.
    Kasus 1: [1, 999] -> Unpack sukses, match elemen ke-2 gagal.
    Kasus 2: [1, 2] -> Harus sukses.
    """
    code = """
    biar data = [1, 2]
    biar res = "awal"

    jodohkan data dengan
    | [1, 999] maka
        ubah res = "salah"
    | [1, 2] maka
        ubah res = "benar"
    | _ maka
        ubah res = "default"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "benar"

def test_match_multi_case_nested_fail():
    """
    Memastikan stack bersih pada nested failure.
    Kasus 1: [1, [999]] -> Nested list match gagal.
    """
    code = """
    biar data = [1, [2]]
    biar res = "awal"

    jodohkan data dengan
    | [1, [999]] maka
        ubah res = "salah"
    | [1, [2]] maka
        ubah res = "benar"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "benar"
