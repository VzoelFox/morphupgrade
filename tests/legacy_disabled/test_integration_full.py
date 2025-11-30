# tests/test_integration_full.py
import pytest

def test_full_python_pipeline_integration(capture_output_from_file):
    """
    Tes integrasi ini memvalidasi pipeline penuh menggunakan parser Python.
    Ini memastikan bahwa beberapa fitur kunci bekerja sama dengan baik:
    - Definisi Tipe Varian
    - Pattern Matching (jodohkan)
    - Panggilan modul Standard Library (`teks`)
    - Panggilan FFI ke modul helper Python
    """
    # Jalankan program MORPH yang kompleks
    output = capture_output_from_file("tests/samples/integration_test.morph")

    # Verifikasi output yang diharapkan
    # Panggilan pertama: proses_status(Sukses(...))
    #   - ganti(...) -> "ini adalah data bersih"
    #   - ffi(...) -> 50.0
    #   - tulis(huruf_besar(...), 50.0) -> "INI ADALAH DATA BERSIH" 50.0
    # Panggilan kedua: proses_status(Gagal(...))
    #   - tulis(...) -> "Terjadi kegagalan:" "database tidak terhubung"
    # Fixture capture_output akan menggabungkan ini
    expected_output = '"INI ADALAH DATA BERSIH" 50.0"Terjadi kegagalan:" "database tidak terhubung"'
    assert output == expected_output
