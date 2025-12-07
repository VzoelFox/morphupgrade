# run_ivm_tests.py
import os
import sys
import traceback
from typing import List, Dict, Any

from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM
from transisi.crusher import Pengurai
from transisi.lx import Leksikal

# --- FFI untuk Assertion ---

# Variabel global untuk melacak status tes saat ini
_current_test_failures = []
_current_test_name = ""

def assert_sama(a, b):
    if a != b:
        msg = f"Assert Sama Gagal: '{a}' != '{b}'"
        _current_test_failures.append(msg)
    return None

def assert_benar(x):
    if not x:
        msg = f"Assert Benar Gagal: nilai adalah '{x}'"
        _current_test_failures.append(msg)
    return None

def assert_gagal(pesan: str):
    _current_test_failures.append(f"Gagal sengaja: {pesan}")
    return None

ASSERT_FFI = {
    "assert_sama": assert_sama,
    "assert_benar": assert_benar,
    "assert_gagal": assert_gagal,
}

# --- Test Runner ---

def temukan_file_tes(direktori_awal: str) -> List[str]:
    """Menemukan semua file .fox di dalam direktori 'tests/'."""
    file_tes = []
    for root, _, files in os.walk(direktori_awal):
        for file in files:
            if file.endswith(".fox"):
                file_tes.append(os.path.join(root, file))
    return file_tes

def jalankan_tes(path_file: str) -> List[str]:
    """Meng-compile dan menjalankan satu file tes, mengembalikan daftar kegagalan."""
    global _current_test_failures, _current_test_name
    _current_test_failures = []
    _current_test_name = path_file

    try:
        with open(path_file, "r", encoding="utf-8") as f:
            sumber = f.read()

        # Compile
        lexer = Leksikal(sumber, nama_file=path_file)
        tokens, errors = lexer.buat_token()
        if errors:
            return [f"Kesalahan Lexer: {err}" for err in errors]

        parser = Pengurai(tokens)
        ast = parser.urai()
        if not ast:
            return [f"Kesalahan Parser: {err}" for err in parser.daftar_kesalahan]

        compiler = Compiler()
        code_obj = compiler.compile(ast, filename=path_file, is_main_script=True)

        # Jalankan
        vm = StandardVM()
        # Suntikkan FFI assertion ke dalam globals VM
        vm.globals.update(ASSERT_FFI)
        vm.load(code_obj)
        vm.run()

        return _current_test_failures

    except Exception:
        return [f"Kesalahan Kritis: {traceback.format_exc()}"]

def main():
    # Daftar direktori tes yang akan dijalankan
    daftar_dir = ["tests/fitur_dasar", "greenfield/examples"]

    daftar_file_tes = []
    for d in daftar_dir:
        files = temukan_file_tes(d)
        # Filter file tes di greenfield/examples agar hanya menjalankan file berawalan 'test_' atau 'uji_'
        if "greenfield" in d:
             files = [f for f in files if "test_" in os.path.basename(f) or "uji_" in os.path.basename(f)]
        daftar_file_tes.extend(files)

    print(f"--- Menjalankan Tes IVM ({len(daftar_file_tes)} file) ---")

    if not daftar_file_tes:
        print("Tidak ada file tes .fox yang ditemukan.")
        sys.exit(0)

    total_gagal = 0
    total_tes = len(daftar_file_tes)

    for path_file in daftar_file_tes:
        print(f" menjalankan: {path_file} ...", end="")
        kegagalan = jalankan_tes(path_file)
        if not kegagalan:
            print(" LULUS")
        else:
            print(" GAGAL")
            total_gagal += 1
            for i, pesan in enumerate(kegagalan):
                print(f"    {i+1}. {pesan}")

    print("\n--- Ringkasan Tes IVM ---")
    print(f"Total Tes Dijalankan: {total_tes}")
    print(f"Lulus: {total_tes - total_gagal}")
    print(f"Gagal: {total_gagal}")

    if total_gagal > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
