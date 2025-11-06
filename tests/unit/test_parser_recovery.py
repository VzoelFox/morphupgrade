# tests/unit/test_parser_recovery.py
# -*- coding: utf-8 -*-

# PATCH-TEST-003: Menambahkan test suite untuk pemulihan kesalahan parser.
# TODO: Tambahkan lebih banyak skenario pemulihan kesalahan yang kompleks.

import pytest
from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai, PenguraiKesalahan

def test_parser_error_recovery(capsys):
    """
    Memastikan bahwa parser dapat pulih dari kesalahan sintaks
    dan melaporkan beberapa kesalahan dalam satu kali jalan.
    """
    code_with_errors = """
    biar x = 5 + "teks";  # Kesalahan 1: Token tidak valid (;)
    biar y = "string tidak ditutup

    jika x > maka         # Kesalahan 2: Ekspresi tidak lengkap
        tulis(x)
    akhir

    fungsi salah() maka   # Sintaks benar sebagai titik sinkronisasi
        tulis("lanjut")
    akhir
    """

    lexer = Leksikal(code_with_errors)
    tokens = lexer.buat_token()
    parser = Pengurai(tokens)

    with pytest.raises(PenguraiKesalahan) as exc_info:
        parser.urai()

    # Verifikasi bahwa beberapa pesan kesalahan yang berbeda dilaporkan
    # Pesan yang tepat mungkin perlu disesuaikan berdasarkan implementasi parser.
    # Untuk saat ini, kita akan memeriksa substring kunci.

    # Verifikasi bahwa pesan-pesan kesalahan kunci ada di dalam output gabungan.
    output = str(exc_info.value)

    # 1. Pesan rekapitulasi puitis
    assert "Dalam kidung kodemu, beberapa nada sumbang terdengar" in output, \
        "Pesan rekapitulasi puitis tidak ditemukan."
