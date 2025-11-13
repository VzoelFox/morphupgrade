import pytest
import subprocess
import os
import sys
from transisi.Morph import Morph
from transisi.error_utils import FormatterKesalahan

# Pastikan kita berada di root direktori proyek untuk path yang konsisten
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="module")
def compiled_error_fixture():
    """
    Fixture untuk mengkompilasi file MORPH yang mengandung error runtime
    dan mengembalikan path ke JSON serta sumber kode aslinya.
    """
    morph_source_code = """
biar x = 10 / 0 // Error akan terjadi di sini
tulis(x)
"""
    source_path = "universal/test_error_lokasi.morph"
    json_path = "universal/test_error_lokasi.json"
    compiler_path = "universal/_build/default/main.exe"

    with open(source_path, "w", encoding="utf-8") as f:
        f.write(morph_source_code)

    if not os.path.exists(compiler_path):
        pytest.fail(f"Compiler OCaml tidak ditemukan di {compiler_path}. Jalankan 'dune build' di 'universal/'.")

    result = subprocess.run(
        [compiler_path, source_path, json_path],
        capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        pytest.fail(f"Kompilasi OCaml gagal: {result.stderr}")

    yield json_path, morph_source_code

    os.remove(source_path)
    os.remove(json_path)


def test_runtime_error_uses_ast_node_location(compiled_error_fixture):
    """
    Tes integrasi end-to-end untuk memverifikasi bahwa runtime error
    menggunakan informasi lokasi dari node AST untuk pelaporan error.
    """
    json_path, source_code = compiled_error_fixture

    morph_app = Morph()

    # Karena jalankan_dari_ocaml_ast mencetak ke stderr dan sys.exit, kita perlu
    # menjalankannya di subprocess untuk menangkap output dan mencegah exit.
    # Kita juga perlu mengatur PYTHONPATH agar modul transisi ditemukan.
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    process = subprocess.run(
        [sys.executable, "-m", "transisi.Morph", "--use-ocaml-loader", json_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env,
        check=False # Jangan raise exception jika return code non-zero
    )

    # Verifikasi bahwa pesan error diformat dengan benar dan ada di stderr
    error_message = process.stderr
    assert error_message, "Seharusnya ada output di stderr"

    # Ini adalah ASERSI KUNCI
    # Kita mengharapkan baris 2, kolom 13 (lokasi dari operator '/')
    expected_location_string = "[baris 2:kolom 13]"
    assert expected_location_string in error_message, \
        f"Pesan error tidak mengandung informasi lokasi yang benar. Diharapkan '{expected_location_string}' dalam stderr."

    assert "Tidak bisa membagi dengan nol" in error_message, "Pesan error tidak mengandung detail yang benar."

    print(f"\nStderr yang Ditangkap:\n{error_message}")
