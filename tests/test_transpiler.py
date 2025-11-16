# tests/test_transpiler.py
import pytest
from transisi.transpiler import Transpiler
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi.absolute_sntx_morph import FungsiDeklarasi

def transpilasi_dari_sumber(sumber: str) -> str:
    """Helper untuk menjalankan pipeline penuh dari sumber ke Python."""
    leksikal = Leksikal(sumber, "<test>")
    tokens, _ = leksikal.buat_token()
    pengurai = Pengurai(tokens)
    program = pengurai.urai()

    if program is None:
        pytest.fail("Parser gagal mengurai source code, mengembalikan None.")

    # Asumsi node yang relevan adalah statement pertama
    node_untuk_ditranspilasi = program.daftar_pernyataan[0]

    transpiler = Transpiler()
    return transpiler.transpilasi(node_untuk_ditranspilasi)

def bersihkan_kode(kode: str) -> str:
    """Menghapus spasi berlebih dan baris kosong untuk perbandingan."""
    return "\n".join(line.strip() for line in kode.strip().splitlines())

def test_transpilasi_fungsi_sederhana():
    sumber_morph = """
    fungsi tambah(a, b) maka
        kembalikan a + b
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    __hasil = (a + b)
    """

    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)

def test_transpilasi_loop_selama():
    sumber_morph = """
    fungsi hitung_mundur(n) maka
        selama n > 0 maka
            ubah n = n - 1
        akhir
        kembalikan n
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    while (n > 0):
        n = (n - 1)
    __hasil = n
    """

    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)

def test_transpilasi_kondisional_jika_lain():
    sumber_morph = """
    fungsi cek_angka(x) maka
        jika x > 10 maka
            kembalikan "besar"
        lain
            kembalikan "kecil"
        akhir
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    if (x > 10):
        __hasil = "besar"
    else:
        __hasil = "kecil"
    """
    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)

def test_transpilasi_kondisional_jika_lain_jika_lain():
    sumber_morph = """
    fungsi grade(skor) maka
        jika skor >= 90 maka
            kembalikan "A"
        lain jika skor >= 80 maka
            kembalikan "B"
        lain
            kembalikan "C"
        akhir
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    if (skor >= 90):
        __hasil = "A"
    elif (skor >= 80):
        __hasil = "B"
    else:
        __hasil = "C"
    """
    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)

def test_transpilasi_fungsi_dengan_variabel():
    sumber_morph = """
    fungsi hitung(x) maka
        biar y = x * 2
        kembalikan y + 5
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    y = (x * 2)
    __hasil = (y + 5)
    """

    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)

def test_transpilasi_nested_binary_operations():
    sumber_morph = """
    fungsi kalkulasi(a, b, c) maka
        kembalikan a + b * c
    akhir
    """
    hasil_python = transpilasi_dari_sumber(sumber_morph)

    kode_yang_diharapkan = """
    __hasil = (a + (b * c))
    """

    assert bersihkan_kode(hasil_python) == bersihkan_kode(kode_yang_diharapkan)
