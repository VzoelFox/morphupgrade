# tests/test_modules.py
import pytest
import os

def test_import_all_simple(run_morph_program):
    """Menguji 'ambil_semua' untuk mengimpor semua simbol dari sebuah modul."""
    module_code = """
tetap PI = 3.14
fungsi kuadrat(n) maka
    kembalikan n * n
akhir
biar _rahasia = 42
"""
    with open("modul_tes_1.fox", "w") as f:
        f.write(module_code)

    program = """
    ambil_semua "modul_tes_1.fox"
    tulis(PI)
    tulis(kuadrat(5))
    """
    output, errors = run_morph_program(program, "tes_utama_1.fox")
    os.remove("modul_tes_1.fox")

    assert not errors, f"Expected no errors, but got: {errors}"
    assert "3.14" in output
    assert "25" in output

def test_import_with_alias(run_morph_program):
    """Menguji 'ambil_semua ... sebagai' untuk mengimpor modul ke dalam namespace."""
    module_code = """
tetap PI = 3.14159
fungsi tambah(a, b) maka
    kembalikan a + b
akhir
"""
    with open("modul_tes_2.fox", "w") as f:
        f.write(module_code)

    program = """
    ambil_semua "modul_tes_2.fox" sebagai mat
    tulis(mat["PI"])
    biar hasil = mat["tambah"](10, 20)
    tulis(hasil)
    """
    output, errors = run_morph_program(program, "tes_utama_2.fox")
    os.remove("modul_tes_2.fox")

    assert not errors, f"Expected no errors, but got: {errors}"
    assert "3.14159" in output
    assert "30" in output

def test_import_partial(run_morph_program):
    """Menguji 'ambil_sebagian ... dari' untuk mengimpor item spesifik."""
    module_code = """
tetap PI = 3.14
fungsi kuadrat(n) maka
    kembalikan n * n
akhir
fungsi tambah(a, b) maka
    kembalikan a + b
akhir
"""
    with open("modul_tes_3.fox", "w") as f:
        f.write(module_code)

    program = """
    ambil_sebagian PI, kuadrat dari "modul_tes_3.fox"
    tulis(PI)
    tulis(kuadrat(10))
    tambah(1, 2) # Ini seharusnya gagal
    """
    output, errors = run_morph_program(program, "tes_utama_3.fox")
    os.remove("modul_tes_3.fox")

    assert len(errors) == 1
    assert "KesalahanNama" in errors[0]
    assert "'tambah' belum didefinisikan" in errors[0]
    assert "3.14" in output
    assert "100" in output

def test_circular_import_detection(run_morph_program):
    """Memastikan interpreter mendeteksi dan mencegah impor sirkular."""
    module_a_code = 'ambil_semua "modul_b.fox"'
    module_b_code = 'ambil_semua "modul_a.fox"'

    with open("modul_a.fox", "w") as f:
        f.write(module_a_code)
    with open("modul_b.fox", "w") as f:
        f.write(module_b_code)

    program = 'ambil_semua "modul_a.fox"'
    output, errors = run_morph_program(program, "tes_utama_sirkular.fox")

    os.remove("modul_a.fox")
    os.remove("modul_b.fox")

    assert len(errors) == 1
    assert "KesalahanRuntime" in errors[0]
    assert "Import melingkar terdeteksi!" in errors[0]
    assert "modul_a.fox -> modul_b.fox -> modul_a.fox" in errors[0]

def test_module_not_found(run_morph_program):
    """Menguji error yang benar ketika modul tidak ditemukan."""
    program = 'ambil_semua "file_yang_tidak_ada.fox"'
    output, errors = run_morph_program(program, "tes_utama_tak_ada.fox")

    assert len(errors) == 1
    assert "KesalahanRuntime" in errors[0]
    assert "Modul 'file_yang_tidak_ada.fox' tidak ditemukan" in errors[0]

def test_private_symbols_not_exported(run_morph_program):
    """Memastikan simbol yang diawali '_' tidak diekspor."""
    module_code = """
biar publik = 10
biar _privat = 20
"""
    with open("modul_tes_privat.fox", "w") as f:
        f.write(module_code)

    # Tes untuk 'ambil_semua' tanpa alias
    program1 = """
    ambil_semua "modul_tes_privat.fox"
    tulis(publik)
    tulis(_privat) # Ini harus gagal
    """
    output1, errors1 = run_morph_program(program1, "tes_utama_privat1.fox")
    assert "10" in output1
    assert len(errors1) == 1
    assert "'_privat' belum didefinisikan" in errors1[0]

    # Tes untuk 'ambil_semua' dengan alias
    program2 = """
    ambil_semua "modul_tes_privat.fox" sebagai mod
    tulis(mod["publik"])
    tulis(mod["_privat"]) # Ini harus mengembalikan nil
    """
    output2, errors2 = run_morph_program(program2, "tes_utama_privat2.fox")
    assert not errors2
    assert "10" in output2
    assert "nil" in output2

    os.remove("modul_tes_privat.fox")

def test_module_syntax_error(run_morph_program):
    """Menguji bahwa error sintaks di modul dilaporkan dengan benar."""
    module_code = "biar x = 1 +" # Sintaks tidak lengkap
    with open("modul_salah.fox", "w") as f:
        f.write(module_code)

    program = 'ambil_semua "modul_salah.fox"'
    output, errors = run_morph_program(program, "tes_utama_salah.fox")
    os.remove("modul_salah.fox")

    assert len(errors) == 1
    assert "KesalahanRuntime" in errors[0]
    assert "Kesalahan sintaks di modul 'modul_salah.fox'" in errors[0]
