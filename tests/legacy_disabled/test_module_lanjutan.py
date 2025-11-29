# tests/fitur_baru/test_module_lanjutan.py
import pytest
import os
from tests.conftest import run_morph_program
from tests.stdlib.test_berkas import safe_path
from tests.fixtures import _test_internal

def test_deep_import_chain(run_morph_program):
    """
    Memverifikasi bahwa simbol dari modul yang diimpor secara transitif (A -> B -> C)
    tersedia di modul tingkat atas (A).
    """
    # Path ke file a.fox yang akan menjadi entry point
    a_path = safe_path(os.path.abspath("tests/fixtures/module_tests/deep_chain/a.fox"))

    # Kode sumber a.fox
    a_code = f'''
    ambil_semua "./b.fox"
    tulis(NILAI_C)
    '''

    # Tulis kode ke file a.fox
    with open(a_path, "w") as f:
        f.write(a_code)

    # Jalankan a.fox
    output, errors = run_morph_program(f'ambil_semua "{a_path}"')

    assert not errors, f"Terjadi error saat menjalankan deep import chain: {errors}"
    assert "INI DARI C" in output

def test_diamond_dependency_executes_once(run_morph_program):
    """
    Memverifikasi bahwa dalam dependensi berlian (A -> B -> D, A -> C -> D),
    modul D hanya dieksekusi sekali.
    """
    _test_internal.reset_globals()

    # Path ke file a.fox yang akan menjadi entry point
    a_path = safe_path(os.path.abspath("tests/fixtures/module_tests/diamond/a.fox"))

    # Kode sumber a.fox
    a_code = f'''
    ambil_semua "./b.fox"
    ambil_semua "./c.fox"

    tulis(NILAI_D)
    '''

    with open(a_path, "w") as f:
        f.write(a_code)

    # Jalankan a.fox
    output, errors = run_morph_program(f'ambil_semua "{a_path}"')

    assert not errors, f"Terjadi error saat menjalankan diamond dependency: {errors}"
    assert "INI DARI D" in output

    # Verifikasi bahwa counter hanya dinaikkan sekali
    counter = _test_internal.get_global("diamond_counter")
    assert counter == 1, f"Modul D dieksekusi {counter} kali, seharusnya hanya sekali."
