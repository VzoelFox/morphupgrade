import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM

def run_morph_code(code):
    """Helper untuk menjalankan kode Morph dan mengembalikan VM state."""
    lexer = Leksikal(code)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()

    if ast_node is None:
        error_msg = "\n".join([f"{e[1]} (Baris {e[0].baris})" for e in parser.daftar_kesalahan])
        raise RuntimeError(f"Parser gagal mengurai kode tes:\n{error_msg}")

    compiler = Compiler()
    bytecode = compiler.compile(ast_node)
    vm = StandardVM()
    vm.load(bytecode)
    vm.run()
    return vm

def test_stdlib_teks_extended():
    # Menggunakan module loader asli
    code = """
    ambil_semua "transisi.stdlib.wajib.teks" sebagai t

    biar kalimat = "Halo Dunia"
    biar besar = t.huruf_besar(kalimat)
    biar kecil = t.huruf_kecil(kalimat)
    biar split = t.pisah(kalimat, " ")
    biar len = t.panjang(kalimat)
    """
    vm = run_morph_code(code)

    assert vm.globals['besar']['data'] == "HALO DUNIA"
    assert vm.globals['kecil']['data'] == "halo dunia"
    assert vm.globals['split']['data'] == ["Halo", "Dunia"]
    assert vm.globals['len']['data'] == 10

def test_stdlib_koleksi_pure_morph():
    """Test fungsi Pure Morph: cari & balik"""
    code = """
    ambil_semua "transisi.stdlib.wajib.koleksi" sebagai k

    biar nums = [10, 20, 30]
    biar found = k.cari(nums, 20)
    biar not_found = k.cari(nums, 99)
    biar reversed = k.balik(nums)
    """
    vm = run_morph_code(code)

    assert vm.globals['found'] == 1
    assert vm.globals['not_found'] == -1
    assert vm.globals['reversed'] == [30, 20, 10]

def test_stdlib_koleksi_hof():
    """Test Higher Order Functions: petakan & saring"""
    code = """
    ambil_semua "transisi.stdlib.wajib.koleksi" sebagai k

    fungsi kuadrat(x) maka
        kembali x * x
    akhir

    fungsi is_genap(x) maka
        kembali (x % 2) == 0
    akhir

    biar data = [1, 2, 3, 4]
    biar hasil_map = k.petakan(data, kuadrat)
    biar hasil_filter = k.saring(data, is_genap)
    """
    vm = run_morph_code(code)

    res_map = vm.globals['hasil_map']
    assert res_map == [1, 4, 9, 16]

    res_filter = vm.globals['hasil_filter']
    assert res_filter == [2, 4]
