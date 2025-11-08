# tests/test_closures.py
import pytest

def test_simple_closure(capture_output):
    """Menguji closure sederhana di mana fungsi dalam mengakses variabel dari fungsi luar."""
    program = """
    fungsi buatPenghitung() maka
        biar x = 0
        fungsi penghitung() maka
            ubah x = x + 1
            kembalikan x
        akhir
        kembalikan penghitung
    akhir

    biar p = buatPenghitung()
    tulis(p()) # 1
    tulis(p()) # 2
    """
    output = capture_output(program)
    assert output.strip() == "1\n2"

def test_lexical_scoping(capture_output):
    """Memastikan variabel diselesaikan berdasarkan di mana fungsi didefinisikan, bukan di mana ia dipanggil."""
    program = """
    biar a = "global"
    fungsi tampil() maka
        tulis(a)
    akhir

    fungsi lingkupLokal() maka
        biar a = "lokal"
        tampil()
    akhir

    lingkupLokal()
    """
    output = capture_output(program)
    assert output == '"global"'

def test_nested_closures(capture_output):
    """Menguji beberapa tingkat closure."""
    program = """
    fungsi luar() maka
        biar a = 1
        fungsi tengah() maka
            biar b = 2
            fungsi dalam() maka
                tulis(a + b)
            akhir
            dalam()
        akhir
        tengah()
    akhir
    luar()
    """
    output = capture_output(program)
    assert output == "3"
