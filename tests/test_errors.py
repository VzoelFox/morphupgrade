# tests/test_errors.py
import pytest

def test_lexer_error_format(run_morph_program):
    """Memverifikasi format output untuk kesalahan dari Lexer."""
    kode = """
    biar a = 1
    biar b = @ # karakter tidak valid
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "Duh, ada typo nih di baris 3" in error_msg
    assert "Karakter '@' tidak dikenal" in error_msg

def test_parser_error_format(run_morph_program):
    """Memverifikasi format output untuk kesalahan dari Parser."""
    kode = """
    biar a =
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "Hmm, kayaknya ada yang aneh di baris 2" in error_msg
    assert "Ekspresi tidak terduga." in error_msg

def test_runtime_error_format(run_morph_program):
    """Memverifikasi format output untuk kesalahan dari Interpreter (Runtime)."""
    kode = """
    biar a = 10
    biar b = a + "teks" # kesalahan tipe
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "Waduh, programnya crash di baris 3" in error_msg
    assert "[KesalahanTipe]" in error_msg
    assert "Operan harus dua angka atau dua teks." in error_msg

def test_stack_trace_format(run_morph_program):
    """Memverifikasi format stack trace untuk kesalahan runtime di dalam fungsi."""
    kode = """
    fungsi dalam() maka
        kembalikan 1 / 0
    akhir

    fungsi luar() maka
        kembalikan dalam()
    akhir

    luar()
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "[KesalahanPembagianNol]" in error_msg
    assert "Jejak Panggilan" in error_msg
    assert "fungsi 'dalam' dipanggil dari baris 7" in error_msg
    assert "fungsi 'luar' dipanggil dari baris 10" in error_msg
