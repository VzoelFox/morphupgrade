# tests/test_engine_inti.py
import pytest

def test_ekspresi_aritmetika(run_morph_program):
    program = """
    biar hasil = (5 + 5) * (3 - 1)
    tulis(hasil)
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output == "20"

def test_error_variabel_tidak_terdefinisi(run_morph_program):
    program = "tulis(variabel_tidak_ada)"
    output, errors = run_morph_program(program)
    assert errors
    assert "[KesalahanNama]" in errors[0]

def test_ekspresi_boolean(run_morph_program):
    program = """
    biar a = benar
    biar b = salah
    biar c = (a dan tidak b) atau (5 > 10)
    tulis(c)
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip().replace('"', '') == "benar"

def test_scoping_jika_tidak_bocor(run_morph_program):
    program = """
    jika benar maka
        biar x = 10
    akhir
    tulis(x) // Ini harus error
    """
    output, errors = run_morph_program(program)
    assert errors
    assert "[KesalahanNama]" in errors[0]

def test_scoping_selama_akses_luar(run_morph_program):
    program = """
    biar x = 5
    biar y = 0
    selama x > 0 maka
        biar z = 1 // Variabel dalam scope loop
        ubah y = y + z
        ubah x = x - 1
    akhir
    tulis(y + x) // Harusnya 5 + 0 = 5. Oops, test asli salah. Seharusnya 6
    """
    # Test asli mengharapkan 6, mari kita perbaiki ekspektasinya
    # y akan menjadi 5, dan x akan menjadi 0. jadi y+x = 5
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output == "5"

def test_jika_lain_jika_lain(run_morph_program):
    program = """
    biar nilai = 15
    jika nilai < 10 maka
        tulis("A")
    lain jika nilai < 20 maka
        tulis("B")
    lain
        tulis("C")
    akhir
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip().replace('"', '') == "B"

def test_selama_loop_sederhana(run_morph_program):
    program = """
    biar i = 0
    selama i < 3 maka
        tulis(i)
        tulis("\n")
        ubah i = i + 1
    akhir
    """
    output, errors = run_morph_program(program)
    if errors: print(errors)
    assert not errors
    assert output.strip().replace('"', '') == "0\n1\n2\n"

def test_error_runtime_pembagian_nol(run_morph_program):
    program = "biar hasil = 10 / 0"
    output, errors = run_morph_program(program)
    assert errors
    assert "[KesalahanPembagianNol]" in errors[0]
