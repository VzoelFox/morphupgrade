# tests/test_modules.py
import pytest
import os
import asyncio

def test_import_all_simple(run_morph_program):
    """Menguji 'ambil_semua' untuk mengimpor semua simbol dari sebuah modul."""
    module_code = """
tetap PI = 3.14
fungsi kuadrat(n) maka
    kembali n * n
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
    kembali a + b
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
    kembali n * n
akhir
fungsi tambah(a, b) maka
    kembali a + b
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
    error_msg = errors[0]
    assert "KesalahanRuntime" in error_msg
    assert "Import melingkar terdeteksi!" in error_msg
    # Urutan pasti bisa bervariasi tergantung implementasi, jadi kita periksa bagian-bagiannya
    assert "tes_utama_sirkular.fox" in error_msg
    assert "modul_a.fox" in error_msg
    assert "modul_b.fox" in error_msg

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


def test_module_cache_eviction(monkeypatch):
    """Memverifikasi bahwa cache modul melakukan eviksi saat kapasitas terlampaui."""
    CACHE_SIZE = 5
    monkeypatch.setenv("MORPH_MODULE_CACHE_SIZE", str(CACHE_SIZE))

    from transisi.translator import Penerjemah
    from transisi.error_utils import FormatterKesalahan
    from transisi.lx import Leksikal
    from transisi.crusher import Pengurai
    from io import StringIO

    module_files = []
    num_modules = CACHE_SIZE + 2

    try:
        # Buat file-file modul
        for i in range(num_modules):
            filename = f"mod_cache_test_{i}.fox"
            module_files.append(filename)
            with open(filename, "w") as f:
                f.write(f"tetap ID = {i}")

        import_statements = "\n".join([f'ambil_semua "{f}" sebagai m{i}' for i, f in enumerate(module_files)])

        # 1. Siapkan komponen interpreter
        formatter = FormatterKesalahan(import_statements)
        output_stream = StringIO()

        # 2. Lakukan Lexing
        lexer = Leksikal(import_statements, "main_cache_test.fox")
        tokens, lexer_errors = lexer.buat_token()
        assert not lexer_errors, f"Terjadi kesalahan lexer yang tidak diharapkan: {lexer_errors}"

        # 3. Lakukan Parsing
        parser = Pengurai(tokens)
        program_ast = parser.urai()
        assert not parser.daftar_kesalahan, f"Terjadi kesalahan parser yang tidak diharapkan: {parser.daftar_kesalahan}"

        # 4. Inisialisasi dan jalankan interpreter
        interpreter = Penerjemah(formatter, output_stream=output_stream)

        # Jalankan coroutine terjemahan menggunakan asyncio.run
        runtime_errors = asyncio.run(interpreter.terjemahkan(program_ast, "main_cache_test.fox"))

        assert not runtime_errors, f"Tidak seharusnya ada error saat runtime: {runtime_errors}"

        # 5. Verifikasi state cache
        module_cache = interpreter.module_loader.cache
        assert len(module_cache._cache) == CACHE_SIZE, f"Ukuran cache seharusnya {CACHE_SIZE} tetapi ditemukan {len(module_cache._cache)}"

        # Modul pertama (mod_cache_test_0.fox) seharusnya sudah tereviksi
        first_module_path = os.path.abspath(module_files[0])
        assert first_module_path not in module_cache._cache, "Modul tertua seharusnya sudah dieviksi dari cache"

        # Modul terakhir (mod_cache_test_6.fox) seharusnya ada di cache
        last_module_path = os.path.abspath(module_files[-1])
        assert last_module_path in module_cache._cache, "Modul terbaru seharusnya ada di dalam cache"
        assert module_cache.get(last_module_path)["ID"] == num_modules - 1

    finally:
        # Cleanup
        for filename in module_files:
            if os.path.exists(filename):
                os.remove(filename)
