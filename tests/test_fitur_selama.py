# tests/test_fitur_selama.py

import pytest

def test_selama_sederhana(capture_output):
    kode = """
    biar a = 0;
    selama a < 5 maka
        tulis(a);
        a = a + 1;
    akhir
    """
    output = capture_output(kode)
    hasil_bersih = " ".join(output.strip().split())
    assert hasil_bersih == "0 1 2 3 4"

def test_selama_dengan_scope(capture_output):
    kode = """
    biar a = 3;
    biar b = 0;
    selama a > 0 maka
        biar b = a;
        tulis(b);
        a = a - 1;
    akhir
    tulis(b); # Harus 0, karena 'b' di dalam loop punya scope sendiri
    """
    output = capture_output(kode)
    hasil_bersih = " ".join(output.strip().split())
    assert hasil_bersih == "3 2 1 0"
