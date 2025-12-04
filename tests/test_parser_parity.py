import os
import sys
import subprocess
import glob
import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai, PenguraiKesalahan

# Konfigurasi Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXAMPLES_DIR = os.path.join(PROJECT_ROOT, "greenfield", "examples")
COTC_DIR = os.path.join(PROJECT_ROOT, "greenfield", "cotc")

def run_bootstrap_parser(filepath):
    """
    Menjalankan parser Bootstrap (Python) pada file.
    Mengembalikan True jika sukses, False jika gagal.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Lexing
        lexer = Leksikal(content, filepath)
        tokens, errors = lexer.buat_token()
        if errors:
            return False, f"Lexer errors: {errors}"

        # 2. Parsing
        parser = Pengurai(tokens)
        ast = parser.urai()

        if parser.daftar_kesalahan:
            return False, f"Parser errors: {parser.daftar_kesalahan}"

        return True, "Success"
    except Exception as e:
        return False, f"Exception: {e}"

def run_greenfield_parser(filepath):
    """
    Menjalankan parser Greenfield (Morph) via VM pada file.
    Mengembalikan True jika sukses, False jika gagal.
    """
    cmd = [
        sys.executable, "-m", "ivm.main",
        os.path.join(PROJECT_ROOT, "greenfield", "verifikasi.fox"),
        filepath
    ]

    try:
        # Run process
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        # Cek output standar verifikasi.fox
        if "Verifikasi sintaks berhasil" in result.stdout:
            return True, "Success"
        else:
            return False, result.stdout + "\n" + result.stderr

    except Exception as e:
        return False, f"Subprocess failed: {e}"

def get_test_files():
    """Mengambil daftar file .fox untuk dites."""
    files = []
    # Examples
    files.extend(glob.glob(os.path.join(EXAMPLES_DIR, "*.fox")))
    # COTC (Struktur, Stdlib, etc)
    files.extend(glob.glob(os.path.join(COTC_DIR, "**", "*.fox"), recursive=True))
    return sorted(files)

@pytest.mark.parametrize("filepath", get_test_files())
def test_parser_parity(filepath):
    """
    Memastikan Bootstrap Parser dan Greenfield Parser memiliki kesepakatan
    tentang validitas sintaks setiap file.
    """
    print(f"Testing parity for: {filepath}")

    boot_success, boot_msg = run_bootstrap_parser(filepath)
    green_success, green_msg = run_greenfield_parser(filepath)

    # Assert bahwa status sukses/gagal sama
    if boot_success != green_success:
        pytest.fail(
            f"Parser Discrepancy in {os.path.basename(filepath)}!\n"
            f"Bootstrap Success: {boot_success}\n"
            f"Greenfield Success: {green_success}\n"
            f"--- Bootstrap Msg ---\n{boot_msg}\n"
            f"--- Greenfield Msg ---\n{green_msg}"
        )

    # Opsional: Jika keduanya gagal, pastikan keduanya gagal karena alasan parsing,
    # bukan karena crash VM atau file not found (tapi ini agak susah dideteksi generik)

if __name__ == "__main__":
    # Mode manual run tanpa pytest
    files = get_test_files()
    failures = 0
    print(f"Running parity check on {len(files)} files...")

    for f in files:
        b_ok, b_msg = run_bootstrap_parser(f)
        g_ok, g_msg = run_greenfield_parser(f)

        if b_ok != g_ok:
            print(f"[FAIL] {f}")
            print(f"  Bootstrap: {b_ok}")
            print(f"  Greenfield: {g_ok}")
            failures += 1
        else:
            print(f"[OK] {f}")

    if failures > 0:
        sys.exit(1)
    else:
        print("All checks passed.")
