# tests/test_integration.py
import pytest

def test_complex_program_with_functions(run_morph_program):
    program = """
    biar x = 10
    fungsi tambah(a, b) maka
        kembalikan a + b
    akhir
    fungsi kali(a, b) maka
        kembalikan a * b
    akhir
    biar hasil = kali(tambah(x, 3), 10)
    tulis(hasil)
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output == "130"

def test_while_loop_integration(run_morph_program):
    program = """
    biar i = 0
    selama i < 5 maka
        tulis(i)
        tulis("\n")
        ubah i = i + 1
    akhir
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip().replace('"', '') == "0\n1\n2\n3\n4\n"

def test_dictionary_integration(run_morph_program):
    program = """
    biar data = {"nama": "Vzoel", "skor": 150}
    tulis(data["nama"])
    tulis(data["skor"])
    tulis(data["alamat"]) // Harusnya nil
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip() == '"Vzoel"150nil'

def test_if_statement_integration(run_morph_program):
    program = """
    biar angka = 10
    jika angka == 10 maka
        tulis("sepuluh")
    akhir
    jika angka > 5 dan angka < 15 maka
        tulis(benar)
    akhir
    biar teks = "halo"
    jika teks == "dunia" atau angka < 0 maka
        tulis("salah")
    lain
        tulis("negatif")
    akhir
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip() == '"sepuluh"benar"negatif"'

def test_pilih_statement_integration(run_morph_program):
    program = """
    fungsi cek_nilai(n) maka
        pilih n
        ketika 1 maka
            tulis("Satu")
        ketika 2 maka
            tulis("Dua")
        ketika 3 maka
            tulis("Tiga")
        lainnya maka
            tulis("Lainnya")
        akhir
    akhir
    cek_nilai(2)
    cek_nilai(99)
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip() == '"Dua""Lainnya"'
