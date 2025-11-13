# tests/stdlib/test_teks.py
import pytest

# Semua tes akan menggunakan fixture 'capture_output' dari conftest.py

def test_pisah(capture_output):
    """Tes fungsi teks.pisah()."""
    code = """
    ambil_sebagian pisah dari "transisi/stdlib/wajib/teks.fox"
    biar hasil = pisah("satu,dua,tiga", ",")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '["satu", "dua", "tiga"]'

def test_gabung(capture_output):
    """Tes fungsi teks.gabung()."""
    code = """
    ambil_sebagian gabung dari "transisi/stdlib/wajib/teks.fox"
    biar data = ["apel", "jeruk", "mangga"]
    biar hasil = gabung(data, " & ")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '"apel & jeruk & mangga"'

def test_potong_spasi(capture_output):
    """Tes fungsi teks.potong_spasi()."""
    code = """
    ambil_sebagian potong_spasi dari "transisi/stdlib/wajib/teks.fox"
    biar hasil = potong_spasi("   halo dunia   ")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '"halo dunia"'

def test_huruf_besar(capture_output):
    """Tes fungsi teks.huruf_besar()."""
    code = """
    ambil_sebagian huruf_besar dari "transisi/stdlib/wajib/teks.fox"
    biar hasil = huruf_besar("ini teks kecil")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '"INI TEKS KECIL"'

def test_huruf_kecil(capture_output):
    """Tes fungsi teks.huruf_kecil()."""
    code = """
    ambil_sebagian huruf_kecil dari "transisi/stdlib/wajib/teks.fox"
    biar hasil = huruf_kecil("INI TEKS BESAR")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '"ini teks besar"'

def test_ganti(capture_output):
    """Tes fungsi teks.ganti()."""
    code = """
    ambil_sebagian ganti dari "transisi/stdlib/wajib/teks.fox"
    biar hasil = ganti("halo dunia, dunia indah", "dunia", "morph")
    tulis(hasil)
    """
    output = capture_output(code)
    assert output == '"halo morph, morph indah"'

def test_mulai_dengan(capture_output):
    """Tes fungsi teks.mulai_dengan()."""
    code = """
    ambil_sebagian mulai_dengan dari "transisi/stdlib/wajib/teks.fox"
    biar hasil1 = mulai_dengan("morph lang", "morph")
    biar hasil2 = mulai_dengan("morph lang", "python")
    tulis(hasil1, hasil2)
    """
    output = capture_output(code)
    assert output == 'benar salah'

def test_berakhir_dengan(capture_output):
    """Tes fungsi teks.berakhir_dengan()."""
    code = """
    ambil_sebagian berakhir_dengan dari "transisi/stdlib/wajib/teks.fox"
    biar hasil1 = berakhir_dengan("file.fox", ".fox")
    biar hasil2 = berakhir_dengan("file.py", ".fox")
    tulis(hasil1, hasil2)
    """
    output = capture_output(code)
    assert output == 'benar salah'
