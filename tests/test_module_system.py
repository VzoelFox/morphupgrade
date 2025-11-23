import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM
import os

def run_morph_code(code):
    lexer = Leksikal(code)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()

    if ast_node is None:
        msg = "\n".join([e[1] for e in parser.daftar_kesalahan])
        raise RuntimeError(f"Parser Failed: {msg}")

    compiler = Compiler()
    bytecode = compiler.compile(ast_node)
    vm = StandardVM()
    vm.load(bytecode)
    vm.run()
    return vm

def test_import_real_module():
    # Pastikan file sample ada
    assert os.path.exists("tests/samples/hello.fox")

    code = """
    ambil_semua "tests.samples.hello" sebagai h

    biar pesan = h.pesan
    biar angka = h.angka
    biar sapaan = h.sapa("Budi")
    """

    vm = run_morph_code(code)

    # Verifikasi hasil import
    # h adalah dictionary (module object)
    h = vm.globals.get('h')
    assert isinstance(h, dict)
    assert h['pesan'] == "Halo dari File!"
    assert h['angka'] == 123

    # Verifikasi binding variabel lokal
    assert vm.globals['pesan'] == "Halo dari File!"
    assert vm.globals['angka'] == 123

    # Verifikasi pemanggilan fungsi dari modul
    assert vm.globals['sapaan'] == "Halo Budi"
