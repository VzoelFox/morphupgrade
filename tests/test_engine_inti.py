# tests/test_engine_inti.py
import pytest

def test_ekspresi_aritmetika(capture_output):
    """Memvalidasi bahwa ekspresi aritmetika dasar dievaluasi dengan benar."""
    kode = """
    tulis(5 * (3 + 2) - 10 / 2)
    """
    hasil = capture_output(kode)
    assert hasil == "20.0"

def test_ekspresi_boolean(capture_output):
    """Memvalidasi bahwa ekspresi boolean dan logika dievaluasi dengan benar."""
    kode = """
    jika benar dan (5 > 2) maka
        tulis("Benar")
    lain
        tulis("Salah")
    akhir
    """
    hasil = capture_output(kode)
    assert hasil == "Benar"

def test_scoping_jika_tidak_bocor(capture_output):
    """Memastikan variabel yang dideklarasikan di dalam blok 'jika' tidak bocor ke scope luar."""
    kode = """
    jika benar maka
        biar x = 10
    akhir
    tulis(x)
    """
    hasil = capture_output(kode)
    assert "Kesalahan di baris 5" in hasil
    assert "Penyair mencari makna 'x'" in hasil

def test_scoping_selama_akses_luar(capture_output):
    """Memastikan blok 'selama' dapat mengakses dan mengubah variabel dari scope luar."""
    kode = """
    biar x = 1
    biar hasil = 0
    selama x < 4 maka
        hasil = hasil + x
        x = x + 1
    akhir
    tulis(hasil)
    """
    hasil = capture_output(kode)
    assert hasil == "6"

def test_jika_lain_jika_lain(capture_output):
    """Menguji fungsionalitas penuh dari pernyataan jika-lain jika-lain."""
    kode = """
    biar nilai = 75
    jika nilai > 90 maka
        tulis("A")
    lain jika nilai > 70 maka
        tulis("B")
    lain
        tulis("C")
    akhir
    """
    hasil = capture_output(kode)
    assert hasil == "B"

def test_selama_loop_sederhana(capture_output):
    """Memvalidasi fungsionalitas dasar dari perulangan 'selama'."""
    kode = """
    biar i = 0
    selama i < 3 maka
        tulis(i)
        i = i + 1
    akhir
    """
    hasil = capture_output(kode)
    assert hasil == "0\n1\n2"

def test_error_variabel_tidak_terdefinisi(capture_output):
    """Memastikan interpreter menangkap dan melaporkan kesalahan untuk variabel yang tidak terdefinisi."""
    kode = "tulis(variabel_tidak_ada)"
    hasil = capture_output(kode)
    assert "Kesalahan di baris 1" in hasil
    assert "Penyair mencari makna 'variabel_tidak_ada'" in hasil

def test_error_runtime_pembagian_nol(capture_output):
    """Memastikan interpreter menangani kesalahan pembagian dengan nol."""
    kode = "tulis(10 / 0)"
    hasil = capture_output(kode)
    assert "Kesalahan di baris 1" in hasil
    assert "Semesta tak terhingga saat dibagi dengan kehampaan (nol)." in hasil
