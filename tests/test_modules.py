# tests/test_modules.py
import pytest
import os

def test_import_all_simple(capture_output):
    """Menguji 'ambil_semua' untuk mengimpor semua simbol dari sebuah modul."""
    program = """
    ambil_semua "tests/fixtures/matematika.fox"

    tulis(PI)
    biar hasil = kuadrat(5)
    tulis(hasil)
    """
    output = capture_output(program)
    assert output.strip() == "3.14159\n25"

def test_import_with_alias(capture_output):
    """Menguji 'ambil_semua ... sebagai' untuk mengimpor modul ke dalam namespace."""
    program = """
    ambil_semua "tests/fixtures/matematika.fox" sebagai mat

    tulis(mat["PI"])
    biar hasil = mat["tambah"](10, 20)
    tulis(hasil)
    """
    output = capture_output(program)
    assert output.strip() == "3.14159\n30"

def test_import_partial(capture_output):
    """Menguji 'ambil_sebagian ... dari' untuk mengimpor item spesifik."""
    program = """
    ambil_sebagian PI, kuadrat dari "tests/fixtures/matematika.fox"

    tulis(PI)
    tulis(kuadrat(10))

    # Memastikan 'tambah' tidak diimpor
    biar _ = tambah
    """
    # Mengharapkan KesalahanRuntime karena 'tambah' tidak terdefinisi
    output = capture_output(program)
    assert "Variabel 'tambah' tidak didefinisikan" in output

# TODO: Tambahkan kembali pengujian impor sirkular setelah masalah timeout diinvestigasi.
# def test_circular_import_detection(capture_output):
#     """Memastikan interpreter mendeteksi dan mencegah impor sirkular."""
#     ...
