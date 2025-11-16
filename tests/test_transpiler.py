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
