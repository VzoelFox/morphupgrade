# tests/test_arrays.py
import pytest

def test_array_literal_and_access(capture_output):
    """Menguji pembuatan array (daftar) dan akses elemen."""
    program = """
    biar a = [10, "dua", benar, 30 + 10]
    tulis(a[0])
    tulis(a[1])
    tulis(a[3])
    """
    output = capture_output(program)
    assert output.strip() == '10\n"dua"\n40'

def test_nested_array(capture_output):
    """Menguji array yang berisi array lain."""
    program = """
    biar a = [[1, 2], [3, 4]]
    tulis(a[0][1]) # Harusnya 2
    """
    output = capture_output(program)
    assert output == "2"

def test_array_assignment(capture_output):
    """Menguji pengubahan nilai elemen dalam array."""
    program = """
    biar a = [1, 2, 3]
    ubah a[1] = 99
    tulis(a[1])
    """
    output = capture_output(program)
    assert output == "99"

def test_index_out_of_bounds(capture_output):
    """Memastikan akses indeks di luar jangkauan menghasilkan kesalahan."""
    program = """
    biar a = [1, 2]
    tulis(a[5])
    """
    output = capture_output(program)
    assert "[KesalahanIndeks]" in output
    assert "Indeks di luar jangkauan" in output
