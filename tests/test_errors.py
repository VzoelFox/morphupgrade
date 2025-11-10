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

def test_recursion_depth_error(run_morph_program):
    """Memverifikasi bahwa interpreter berhenti saat batas rekursi terlampaui."""
    kode = """
    fungsi panggil_diri(n) maka
        jika n == 0 maka
            kembalikan 0
        akhir
        kembalikan panggil_diri(n - 1)
    akhir

    panggil_diri(801) // Melebihi batas default (800)
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0
    error_msg = errors[0]
    assert "Waduh, programnya crash di baris 7" in error_msg # Lokasi pemanggilan rekursif
    assert "[KesalahanRuntime]" in error_msg
    assert "wah ternyata batas kedalaman sudah tercapai,dan saya cuma bisa menggapainya sampai disini. coba anda gali lebih dalam dan saya akan menyelam kembali" in error_msg

def test_recursion_depth_env_variable(run_morph_program, monkeypatch):
    """Memverifikasi bahwa batas rekursi dapat diubah melalui environment variable."""
    monkeypatch.setenv("MORPH_RECURSION_LIMIT", "100")

    kode = """
    fungsi hitung_mundur(n) maka
        jika n > 0 maka
            hitung_mundur(n - 1)
        akhir
    akhir

    hitung_mundur(101) // Melebihi batas baru (100)
    """
    _, errors = run_morph_program(kode)
    assert len(errors) > 0, "Seharusnya ada error karena batas 100 terlampaui"
    assert "wah ternyata batas kedalaman sudah tercapai" in errors[0]

    # Tes kedua: memastikan program SUKSES jika di bawah batas baru
    kode_sukses = """
    fungsi hitung_mundur(n) maka
        jika n > 0 maka
            hitung_mundur(n - 1)
        akhir
    akhir

    hitung_mundur(99) // Di bawah batas baru (100)
    """
    _, errors_sukses = run_morph_program(kode_sukses)
    assert len(errors_sukses) == 0, "Seharusnya tidak ada error karena masih di bawah batas"
