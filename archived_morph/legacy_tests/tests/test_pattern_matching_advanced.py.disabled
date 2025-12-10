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

def test_match_literal():
    code = """
    biar x = 10
    biar res = ""
    jodohkan x dengan
    | 10 maka
        ubah res = "sepuluh"
    | _ maka
        ubah res = "lainnya"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "sepuluh"

def test_match_list_exact():
    code = """
    biar data = [1, 2]
    biar res = ""
    jodohkan data dengan
    | [1, 2] maka
        ubah res = "cocok"
    | _ maka
        ubah res = "gagal"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "cocok"

def test_match_list_binding():
    code = """
    biar data = [10, 20]
    biar a = 0
    biar b = 0
    jodohkan data dengan
    | [x, y] maka
        ubah a = x
        ubah b = y
    | _ maka
        ubah a = -1
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['a'] == 10
    assert vm.globals['b'] == 20

def test_match_list_rest():
    """Test [x, ...sisa] - Saat ini diimplementasikan sebagai min_len check tanpa binding sisa"""
    code = """
    biar data = [1, 2, 3, 4]
    biar head = 0
    jodohkan data dengan
    | [h, ...sisa] maka
        ubah head = h
    | _ maka
        ubah head = -1
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['head'] == 1

def test_match_list_fail_len():
    code = """
    biar data = [1]
    biar res = ""
    jodohkan data dengan
    | [a, b] maka
        tulis("Masuk Case 1")
        ubah res = "salah"
    | _ maka
        tulis("Masuk Case 2")
        ubah res = "benar"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "benar"

def test_match_nested_simple():
    """Test nested literal match inside list"""
    code = """
    biar data = [1, "ok"]
    biar res = ""
    jodohkan data dengan
    | [1, "ok"] maka
        ubah res = "cocok"
    | _ maka
        ubah res = "gagal"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "cocok"
