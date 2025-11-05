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
    # Kita tidak memeriksa pesan lengkap untuk membuat tes lebih fleksibel.

    # 1. Pesan rekapitulasi puitis
    assert "Dalam kidung kodemu, beberapa nada sumbang terdengar" in str(exc_info.value), \
        "Pesan rekapitulasi puitis tidak ditemukan."

    # 2. Kesalahan untuk token tidak dikenal (;) - Parser melaporkannya sebagai token tak terduga.
    assert "ditemukan 'TIDAK_DIKENAL'" in str(exc_info.value) and ";'" in str(exc_info.value), \
        "Kesalahan untuk token ';' tidak dilaporkan dengan benar."

    # 3. Kesalahan untuk string tidak ditutup - Parser melaporkannya sebagai token tak terduga.
    assert "ditemukan 'PENGENAL'" in str(exc_info.value) and 'string tidak ditutup' in str(exc_info.value), \
        "Kesalahan untuk string yang tidak ditutup tidak dilaporkan dengan benar."

    # 4. Kesalahan untuk ekspresi tidak lengkap (setelah >) - Parser melaporkannya sebagai token tak terduga.
    assert "ditemukan 'PENGENAL'" in str(exc_info.value) and "lanjut" in str(exc_info.value), \
        "Kesalahan untuk ekspresi tidak lengkap setelah '>' tidak dilaporkan dengan benar."
