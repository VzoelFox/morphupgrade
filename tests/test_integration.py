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
