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
        raise RuntimeError("Parser gagal mengurai kode tes.")

    compiler = Compiler()
    bytecode = compiler.compile(ast_node)
    vm = StandardVM()
    vm.load(bytecode)
    vm.run()
    return vm

def test_stdlib_teks_extended():
    code = """
    ambil_semua "transisi.stdlib.wajib.teks" sebagai internal

    fungsi huruf_besar(teks) maka
        kembali internal.huruf_besar(teks)
    akhir
    fungsi huruf_kecil(teks) maka
        kembali internal.huruf_kecil(teks)
    akhir
    fungsi pisah(teks, pembatas) maka
        kembali internal.pisah(teks, pembatas)
    akhir
    fungsi panjang(teks) maka
        kembali internal.panjang(teks)
    akhir

    biar kalimat = "Halo Dunia"
    biar besar = huruf_besar(kalimat)
    biar kecil = huruf_kecil(kalimat)
    biar split = pisah(kalimat, " ")
    biar len = panjang(kalimat)
    """
    vm = run_morph_code(code)

    assert vm.globals['besar']['data'] == "HALO DUNIA"
    assert vm.globals['kecil']['data'] == "halo dunia"
    assert vm.globals['split']['data'] == ["Halo", "Dunia"]
    assert vm.globals['len']['data'] == 10

def test_stdlib_koleksi_basic():
    code = """
    ambil_semua "transisi.stdlib.wajib.koleksi" sebagai internal

    fungsi urutkan(daftar) maka
        kembali internal.urutkan(daftar)
    akhir
    fungsi panjang(daftar) maka
        kembali internal.panjang(daftar)
    akhir
    fungsi cari(daftar, item) maka
        kembali internal.cari(daftar, item)
    akhir

    biar nums = [3, 1, 2]
    biar sorted = urutkan(nums)
    biar len = panjang(nums)
    biar found = cari(nums, 1)
    biar not_found = cari(nums, 99)
    """
    vm = run_morph_code(code)

    assert vm.globals['sorted']['data'] == [1, 2, 3]
    assert vm.globals['len']['data'] == 3
    assert vm.globals['found']['data'] == 1 # index of 1 is 1
    assert vm.globals['not_found']['data'] == -1

def test_stdlib_koleksi_hof():
    """Test Higher Order Functions: petakan & saring"""
    # Menggunakan formatting yang lebih eksplisit dengan newline untuk parser
    code = """
    ambil_semua "transisi.stdlib.wajib.koleksi" sebagai internal

    fungsi panjang(daftar) maka
        kembali internal.panjang(daftar)
    akhir

    fungsi tambah(daftar, item) maka
        kembali internal.tambah(daftar, item)
    akhir

    fungsi petakan(daftar, fungsi_pemeta) maka
        biar hasil = []
        biar i = 0
        biar p = panjang(daftar)

        jika p.sukses maka
            ubah p = p.data
        akhir

        selama i < p maka
            biar item = daftar[i]
            tambah(hasil, fungsi_pemeta(item))
            ubah i = i + 1
        akhir
        kembali hasil
    akhir

    fungsi saring(daftar, fungsi_predikat) maka
        biar hasil = []
        biar i = 0
        biar p = panjang(daftar)

        jika p.sukses maka
            ubah p = p.data
        akhir

        selama i < p maka
            biar item = daftar[i]
            jika fungsi_predikat(item) maka
                tambah(hasil, item)
            akhir
            ubah i = i + 1
        akhir
        kembali hasil
    akhir

    fungsi kuadrat(x) maka
        kembali x * x
    akhir

    fungsi is_genap(x) maka
        kembali (x % 2) == 0
    akhir

    biar data = [1, 2, 3, 4]
    biar hasil_map = petakan(data, kuadrat)
    biar hasil_filter = saring(data, is_genap)
    """
    vm = run_morph_code(code)

    # Hasil petakan/saring adalah list mentah (karena logic di Morph), bukan Result wrapper
    res_map = vm.globals['hasil_map']
    assert res_map == [1, 4, 9, 16]

    res_filter = vm.globals['hasil_filter']
    assert res_filter == [2, 4]
