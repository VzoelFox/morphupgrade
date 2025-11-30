# tests/test_arrays.py
import pytest

def test_array_literal_and_access(run_morph_program):
    """Menguji pembuatan array (daftar) dan akses elemen."""
    program = """
    biar a = [10, "dua", benar, 30 + 10]
    tulis(a[0])
    tulis(a[1])
    tulis(a[3])
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    # Periksa bahwa semua output yang diharapkan ada, abaikan spasi/baris baru
    assert "10" in output
    assert '"dua"' in output
    assert "40" in output

def test_nested_array(run_morph_program):
    """Menguji array yang berisi array lain."""
    program = """
    biar a = [[1, 2], [3, 4]]
    tulis(a[0][1]) # Harusnya 2
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    assert output == "2"

def test_array_assignment(run_morph_program):
    """Menguji pengubahan nilai elemen dalam array."""
    program = """
    biar a = [1, 2, 3]
    ubah a[1] = 99
    tulis(a[1])
    """
    output, errors = run_morph_program(program)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    assert not errors
    assert output == "99"

def test_index_out_of_bounds(run_morph_program):
    """Memastikan akses indeks di luar jangkauan menghasilkan kesalahan."""
    program = """
    biar a = [1, 2]
    tulis(a[5])
    """
    output, errors = run_morph_program(program)
    assert errors
    assert "[KesalahanIndeks]" in errors[0]
    assert "Indeks di luar jangkauan" in errors[0]
