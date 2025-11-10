# tests/test_errors.py
import pytest

def test_lexer_error_format(run_morph_program):
    """Memverifikasi format output untuk kesalahan dari Lexer."""
    # Kode sengaja dibuat dengan indentasi untuk menguji kalkulasi pointer
    kode = """
    fungsi utama() maka
        biar b = @ # karakter tidak valid
    akhir
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]

    # Verifikasi format baru
    expected_header = "Duh, ada typo nih di baris 3, kolom 19!"
    expected_context = "> biar b = @ # karakter tidak valid"
    expected_pointer_line_regex = r"\s*\^" # Regex untuk spasi diikuti caret
    expected_message = "! Karakter '@' tidak dikenal"

    assert expected_header in error_msg
    assert expected_context in error_msg
    assert expected_message in error_msg

    import re
    # Cari baris yang hanya berisi spasi dan pointer
    pointer_line_found = any(re.match(expected_pointer_line_regex, line) and line.strip() == '^' for line in error_msg.split('\n'))
    assert pointer_line_found, "Baris pointer '^' tidak ditemukan atau formatnya salah."

def test_parser_error_format_at_eof(run_morph_program):
    """Memverifikasi format output untuk kesalahan Parser di akhir file."""
    kode = "biar a = "
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]

    # Verifikasi format baru untuk error di akhir file (tanpa pointer)
    expected_lines = [
        "Hmm, kayaknya ada yang aneh di baris 1...",
        "> biar a =",
        "! Ekspresi tidak terduga. (di akhir file)"
    ]

    actual_lines = [line.strip() for line in error_msg.split('\n')]
    for expected in expected_lines:
        assert expected in actual_lines

    # Pastikan tidak ada pointer
    assert not any(line.strip().startswith('^') for line in actual_lines)

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
        kembali 1 / 0
    akhir

    fungsi luar() maka
        kembali dalam()
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

def test_recursion_depth_error(run_morph_program, monkeypatch):
    """
    Memverifikasi bahwa interpreter berhenti saat batas rekursi terlampaui.
    CATATAN: Batas diatur rendah untuk menghindari RecursionError dari Python.
    """
    # Batas diatur ke 100, yang terbukti lebih rendah dari batas internal Python
    # dalam lingkungan pengujian ini.
    monkeypatch.setenv("MORPH_RECURSION_LIMIT", "100")
    kode = """
    fungsi panggil_diri(n) maka
        jika n == 0 maka
            kembali 0
        akhir
        kembali panggil_diri(n - 1)
    akhir

    panggil_diri(101) // Melebihi batas yang diatur (100)
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "Waduh, programnya crash di baris 6" in error_msg
    assert "[KesalahanRuntime]" in error_msg
    assert "wah ternyata batas kedalaman sudah tercapai" in error_msg

def test_recursion_depth_env_variable(run_morph_program, monkeypatch):
    """Memverifikasi bahwa batas rekursi dapat diubah melalui environment variable."""
    monkeypatch.setenv("MORPH_RECURSION_LIMIT", "50")

    kode = """
    fungsi hitung_mundur(n) maka
        jika n > 0 maka
            hitung_mundur(n - 1)
        akhir
    akhir

    hitung_mundur(51) // Melebihi batas baru (50)
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0, "Seharusnya ada error karena batas 50 terlampaui"
    assert "wah ternyata batas kedalaman sudah tercapai" in errors[0]

    # Tes kedua: memastikan program SUKSES jika di bawah batas baru
    kode_sukses = """
    fungsi hitung_mundur(n) maka
        jika n > 0 maka
            hitung_mundur(n - 1)
        akhir
    akhir

    hitung_mundur(49) // Di bawah batas baru (50)
    """
    _, errors_sukses = run_morph_program(kode_sukses)
    assert len(errors_sukses) == 0, "Seharusnya tidak ada error karena masih di bawah batas"
