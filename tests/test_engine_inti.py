# tests/test_engine_inti.py
import pytest

# PATCH-020A: Nonaktifkan sementara tes yang gagal karena fitur-fitur
#             (jika, selama) belum diimplementasikan di engine baru.
# TODO: Aktifkan kembali dan perbarui tes-tes ini saat parser
#       dan interpreter baru sudah mendukung kontrol alur.

def test_ekspresi_aritmetika(capture_output):
    """Memvalidasi bahwa ekspresi aritmetika dasar dievaluasi dengan benar."""
    # Interpreter baru mengharapkan titik koma atau baris baru
    kode = "tulis(5 * (3 + 2) - 10 / 2)"
    hasil = capture_output(kode)
    assert hasil == "20"

def test_error_variabel_tidak_terdefinisi(capture_output):
    """Memastikan interpreter menangkap dan melaporkan kesalahan untuk variabel yang tidak terdefinisi."""
    kode = "tulis(variabel_tidak_ada);"
    hasil = capture_output(kode)
    assert "Waduh, programnya crash" in hasil
    assert "[KesalahanNama]" in hasil
    assert "Variabel 'variabel_tidak_ada' belum didefinisikan." in hasil

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
    assert hasil == '"Benar"'

def test_scoping_jika_tidak_bocor(capture_output):
    """Memastikan variabel yang dideklarasikan di dalam blok 'jika' tidak bocor ke scope luar."""
    kode = """
    jika benar maka
        biar x = 10
    akhir
    tulis(x)
    """
    hasil = capture_output(kode)
    assert "Waduh, programnya crash" in hasil
    assert "[KesalahanNama]" in hasil
    assert "Variabel 'x' belum didefinisikan." in hasil

def test_scoping_selama_akses_luar(capture_output):
    """Memastikan blok 'selama' dapat mengakses dan mengubah variabel dari scope luar."""
    kode = """
    biar x = 1
    biar hasil = 0
    selama x < 4 maka
        ubah hasil = hasil + x
        ubah x = x + 1
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
    assert hasil == '"B"'

def test_selama_loop_sederhana(capture_output):
    """Memvalidasi fungsionalitas dasar dari perulangan 'selama'."""
    kode = """
    biar i = 0
    selama i < 3 maka
        tulis(i)
        ubah i = i + 1
    akhir
    """
    hasil = capture_output(kode)
    assert hasil.strip() == "0\n1\n2"

def test_error_runtime_pembagian_nol(capture_output):
    """Memastikan interpreter menangani kesalahan pembagian dengan nol."""
    kode = "tulis(10 / 0);"
    hasil = capture_output(kode)
    assert "Waduh, programnya crash" in hasil
    assert "[KesalahanPembagianNol]" in hasil
    assert "Tidak bisa membagi dengan nol." in hasil
