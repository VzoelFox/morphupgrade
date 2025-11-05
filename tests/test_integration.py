# tests/test_integration.py
# -*- coding: utf-8 -*-
"""
Integration tests yang menjalankan program .fox secara end-to-end.

Test Categories:
1. Valid Programs (verifikasi output yang benar)
2. Invalid Programs (verifikasi pesan error yang benar)
3. Complex Scenarios (kombinasi fitur)
"""
# PATCH-TEST-002: Menambahkan test case integrasi untuk program kompleks.
# TODO: Tambahkan lebih banyak skenario integrasi (misal: closures, array, I/O).

import pytest

def test_complex_program_with_functions(capture_output):
    """
    Menguji program lengkap yang menggunakan beberapa fungsi,
    termasuk rekursi dan pemanggilan bersarang, untuk memverifikasi
    integrasi fitur-fitur ini secara end-to-end.
    """
    program = """
    fungsi tambah(a, b) maka
        kembalikan a + b
    akhir

    fungsi faktorial(n) maka
        jika n <= 1 maka
            kembalikan 1
        akhir
        kembalikan n * faktorial(n - 1)
    akhir

    biar hasil = tambah(faktorial(5), 10) # faktorial(5) = 120
    tulis(hasil)
    """

    # Menjalankan program dan memverifikasi output
    # Diharapkan: 120 + 10 = 130
    output = capture_output(program)
    assert output == "130"

def test_while_loop_integration(capture_output):
    """Menguji loop 'selama' dari ujung ke ujung."""
    program = """
    biar x = 0
    selama x < 5 maka
        tulis(x)
        x = x + 1
    akhir
    """
    output = capture_output(program)
    assert output.strip() == "0\n1\n2\n3\n4"

def test_dictionary_integration(capture_output):
    """Menguji pembuatan, akses, dan assignment kamus dari ujung ke ujung."""
    program = """
    biar data = {"nama": "Vzoel", "nilai": 100}
    tulis(data["nama"])
    data["nilai"] = 150
    tulis(data["nilai"])
    tulis(data["alamat"]) # Akses kunci yang tidak ada, harapkan nil
    """
    output = capture_output(program)
    assert output.strip() == "Vzoel\n150\nnil"

def test_pilih_statement_integration(capture_output):
    """Menguji pernyataan 'pilih' sederhana dari ujung ke ujung."""
    program = """
    biar kode = 2
    pilih kode
        ketika 1 maka
            tulis("Satu")
        ketika 2 maka
            tulis("Dua")
        lainnya maka
            tulis("Lainnya")
    akhir

    pilih 99
        ketika 1 maka
            tulis("Satu")
        lainnya maka
            tulis("Lainnya")
    akhir
    """
    output = capture_output(program)
    assert output.strip() == "Dua\nLainnya"
