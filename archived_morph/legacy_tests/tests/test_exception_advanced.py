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
        # Print error parser untuk debug
        error_msg = "\n".join([f"{e[1]} (Baris {e[0].baris})" for e in parser.daftar_kesalahan])
        raise RuntimeError(f"Parser failed:\n{error_msg}")

    compiler = Compiler()
    bytecode = compiler.compile(ast_node)
    vm = StandardVM()
    vm.load(bytecode)
    vm.run()
    return vm

def test_manual_throw_simple():
    code = """
    coba
        lemparkan "Ups!"
    tangkap e
        biar res = e.pesan
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['res'] == "Ups!"

def test_manual_throw_with_type():
    code = """
    coba
        lemparkan "File Hilang" jenis "ErrorIO"
    tangkap e
        biar msg = e.pesan
        biar type = e.jenis
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['msg'] == "File Hilang"
    assert vm.globals['type'] == "ErrorIO"

def test_stack_trace_capture():
    code = """
    fungsi rusak() maka
        lemparkan "Rusak"
    akhir

    fungsi panggil() maka
        rusak()
    akhir

    coba
        panggil()
    tangkap e
        biar trace = e.jejak
    akhir
    """
    vm = run_morph_code(code)
    trace = vm.globals['trace']
    assert isinstance(trace, list)
    names = [t.split(" ")[0] for t in trace]
    assert "rusak" in names
    assert "panggil" in names
    assert "<module>" in names

def test_multiple_catch_with_guard():
    code = """
    biar status = ""

    fungsi lempar_io() maka
        lemparkan "IO Error" jenis "ErrorIO"
    akhir

    coba
        lempar_io()
    tangkap e jika e.jenis == "ErrorTeks"
        ubah status = "Menangkap Teks"
    tangkap e jika e.jenis == "ErrorIO"
        ubah status = "Menangkap IO"
    tangkap e
        ubah status = "Catch All"
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['status'] == "Menangkap IO"

def test_finally_block():
    code = """
    biar clean = 0
    coba
        lemparkan "Error"
    tangkap e
        // handle
    akhirnya
        ubah clean = 1
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['clean'] == 1

def test_finally_block_success_path():
    code = """
    biar clean = 0
    coba
        biar x = 1
    akhirnya
        ubah clean = 1
    akhir
    """
    vm = run_morph_code(code)
    assert vm.globals['clean'] == 1
