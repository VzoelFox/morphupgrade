# tests/test_closures.py
import pytest

def test_simple_closure(run_morph_program):
    program = """
    biar a = 1
    fungsi hitung() maka
        tulis(a)
        tulis("\n") // Tambahkan baris baru secara manual
        ubah a = 2
    akhir
    hitung()
    tulis(a)
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    assert output.strip().replace('"', '') == "1\n2"

def test_lexical_scoping(run_morph_program):
    program = """
    biar a = "global"
    fungsi tunjukkan_a() maka
        tulis(a)
    akhir

    fungsi scope_baru() maka
        biar a = "lokal"
        tunjukkan_a()
    akhir

    scope_baru()
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    assert output.strip().replace('"', '') == "global"

def test_nested_closures(run_morph_program):
    program = """
    fungsi buat_penghitung() maka
        biar i = 0
        fungsi penghitung() maka
            ubah i = i + 1
            kembalikan i
        akhir
        kembalikan penghitung
    akhir

    biar hitung = buat_penghitung()
    hitung()
    hitung()
    tulis(hitung())
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    assert output.strip() == "3"
