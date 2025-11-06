# tests/test_penerjemah_bawaan.py
# Changelog:
# - PATCH-020D: Membuat suite tes baru untuk fungsi bawaan, dimulai dengan `ambil()`.

import pytest
from unittest.mock import patch

from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.penerjemah import Penerjemah, KesalahanRuntime

def jalankan_kode(kode, mock_input_side_effect=None):
    """
    Utilitas untuk menjalankan kode Morph dari string.
    Menerima side_effect untuk mock input, bisa berupa list atau Exception.
    """
    leksikal = Leksikal(kode)
    daftar_token = leksikal.buat_token()
    pengurai = Pengurai(daftar_token)
    ast = pengurai.urai()
    if pengurai.daftar_kesalahan:
        raise pengurai.daftar_kesalahan[0]

    penerjemah = Penerjemah(ast)

    # Gunakan side_effect yang diberikan, default ke list kosong jika None
    side_effect = mock_input_side_effect if mock_input_side_effect is not None else []

    with patch('builtins.input', side_effect=side_effect) as mock_input:
        penerjemah.interpretasi()
        return penerjemah.lingkungan, mock_input

# === Tes untuk fungsi ambil() ===

def test_ambil_dengan_prompt():
    """Memverifikasi `ambil()` dengan prompt teks."""
    kode = 'biar nama = ambil("Masukkan nama: ")'
    input_pengguna = "Jules"

    lingkungan, mock_input = jalankan_kode(kode, mock_input_side_effect=[input_pengguna])

    # Periksa apakah prompt yang benar digunakan
    mock_input.assert_called_once_with("Masukkan nama: ")

    # Periksa apakah variabel 'nama' menerima nilai yang benar
    simbol = lingkungan.dapatkan("nama")
    assert simbol is not None
    assert simbol.nilai == input_pengguna

def test_ambil_tanpa_prompt():
    """Memverifikasi `ambil()` tanpa prompt."""
    kode = 'biar data = ambil()'
    input_pengguna = "rahasia123"

    lingkungan, mock_input = jalankan_kode(kode, mock_input_side_effect=[input_pengguna])

    # Periksa apakah input dipanggil tanpa argumen (prompt kosong)
    mock_input.assert_called_once_with("")

    # Periksa nilai variabel
    simbol = lingkungan.dapatkan("data")
    assert simbol is not None
    assert simbol.nilai == input_pengguna

def test_ambil_handle_eof():
    """Memverifikasi `ambil()` mengembalikan string kosong saat EOF."""
    kode = 'biar data_eof = ambil("Prompt:")'

    # Simulasikan EOFError
    lingkungan, mock_input = jalankan_kode(kode, mock_input_side_effect=EOFError)

    # Periksa apakah prompt tetap dipanggil
    mock_input.assert_called_once_with("Prompt:")

    # Periksa apakah variabel diset ke string kosong
    simbol = lingkungan.dapatkan("data_eof")
    assert simbol is not None
    assert simbol.nilai == ""

def test_ambil_dalam_ekspresi_dan_tulis(capsys):
    """Memverifikasi `ambil()` bekerja saat digabungkan dengan fungsi lain."""
    kode = 'tulis("Halo, " + ambil("Nama: "))'
    input_pengguna = "Dunia"

    # Tidak perlu memeriksa lingkungan, hanya output
    _, mock_input = jalankan_kode(kode, mock_input_side_effect=[input_pengguna])

    # Periksa prompt
    mock_input.assert_called_once_with("Nama: ")

    # Periksa output yang dicetak
    captured = capsys.readouterr()
    assert captured.out.strip() == "Halo, Dunia"

def test_ambil_prompt_dari_variabel():
    """Memverifikasi prompt `ambil()` dapat berupa nilai dari variabel."""
    kode = """
    biar pesan_prompt = "Siapakah Anda? "
    biar pengguna = ambil(pesan_prompt)
    """
    input_pengguna = "Pengelana"

    lingkungan, mock_input = jalankan_kode(kode, mock_input_side_effect=[input_pengguna])

    mock_input.assert_called_once_with("Siapakah Anda? ")
    simbol = lingkungan.dapatkan("pengguna")
    assert simbol is not None
    assert simbol.nilai == input_pengguna

def test_ambil_dengan_argumen_bukan_teks_gagal():
    """Memverifikasi `ambil()` melempar kesalahan jika prompt bukan teks."""
    kode = 'ambil(123)'

    with pytest.raises(KesalahanRuntime) as excinfo:
        jalankan_kode(kode)

    # Periksa pesan kesalahan yang spesifik
    assert "Bisikan untuk 'ambil' haruslah berupa 'teks'" in str(excinfo.value)
