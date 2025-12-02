
import sys
import os
import glob
import re

# [ARCHIVED/LEGACY]
# Alat verifikasi ini telah digantikan oleh `greenfield/verifikasi.fox` yang berjalan di atas IVM.
# File ini disimpan sebagai referensi sejarah atau fallback darurat.
# Untuk menjalankan verifikasi, gunakan:
# python3 -m ivm.main greenfield/verifikasi.fox <target_file>

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))

from ivm.vms.standard_vm import StandardVM
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi.absolute_sntx_morph import AmbilSemua, AmbilSebagian, Pinjam

GREENFIELD_DIR = "greenfield"

def print_step(step_num, title):
    print(f"\n[{step_num}/4] {title}")
    print("=" * 40)

def step_1_verify_per_line(files):
    """
    Langkah 1: Verifikasi Per-line (Sintaksis Dasar)
    Menggunakan Parser internal untuk memastikan tidak ada Syntax Error.
    """
    print_step(1, "Verifikasi Per-line (Sintaks)")

    passed = True
    for filepath in files:
        print(f"Checking {filepath}...", end=" ")
        try:
            with open(filepath, 'r') as f:
                source = f.read()

            lexer = Leksikal(source, filepath)
            tokens, errs = lexer.buat_token()

            if errs:
                print("FAIL (Lexer)")
                for e in errs: print(f"  - {e}")
                passed = False
                continue

            parser = Pengurai(tokens)
            ast = parser.urai()

            if parser.daftar_kesalahan:
                print("FAIL (Parser)")
                for e in parser.daftar_kesalahan: print(f"  - {e}")
                passed = False
            else:
                print("OK")

        except Exception as e:
            print(f"CRASH: {e}")
            passed = False

    return passed

def step_2_verify_dependencies(files):
    """
    Langkah 2: Verifikasi Ketergantungan (File Existence)
    Mengecek apakah file yang diimport benar-benar ada.
    """
    print_step(2, "Verifikasi Ketergantungan (File Exist)")
    passed = True

    # Simple RegEx for imports to avoid full AST traversal complexity for this step
    # import_pattern = re.compile(r'(ambil_semua|dari|pinjam)\s+"([^"]+)"')

    # Better: Use the AST from Step 1 logic

    for filepath in files:
        print(f"Scanning imports in {filepath}...")
        try:
            with open(filepath, 'r') as f: source = f.read()
            lexer = Leksikal(source, filepath)
            tokens, _ = lexer.buat_token()
            parser = Pengurai(tokens)
            ast_root = parser.urai()

            if not ast_root: continue # Already failed step 1

            dir_context = os.path.dirname(filepath)

            for stmt in ast_root.daftar_pernyataan:
                target_path = None

                if isinstance(stmt, AmbilSemua):
                    target_path = stmt.path_file.nilai
                elif isinstance(stmt, AmbilSebagian):
                    target_path = stmt.path_file.nilai
                elif isinstance(stmt, Pinjam):
                    target_path = stmt.path_file.nilai

                if target_path:
                    # Resolve Path Logic (Mimic VM)
                    resolved = False

                    # 1. Direct relative
                    path_check = os.path.join(dir_context, target_path)
                    if os.path.exists(path_check): resolved = True

                    # 2. Hack for "cotc(stdlib)"
                    if not resolved and "cotc(stdlib)" in target_path:
                        # Assuming verify run from root
                        # Map "cotc(stdlib)/..." to "greenfield/cotc/stdlib/..."
                        clean_path = target_path.replace("cotc(stdlib)", "greenfield/cotc/stdlib")
                        if os.path.exists(clean_path): resolved = True

                    if not resolved:
                        print(f"  [X] Missing dependency: '{target_path}'")
                        passed = False
                    else:
                        # print(f"  [v] Found: {target_path}")
                        pass

        except Exception as e:
            print(f"  Error checking deps: {e}")
            passed = False

    if passed: print("All dependencies found.")
    return passed

def step_3_verify_compatibility(files):
    """
    Langkah 3: Verifikasi Kompatibilitas (Symbol Check)
    Mengecek apakah simbol yang diambil (ambil_sebagian) benar-benar diekspor.
    """
    print_step(3, "Verifikasi Kompatibilitas (Symbol Exports)")
    passed = True

    vm = StandardVM()

    for filepath in files:
        # We only check 'ambil_sebagian'
        try:
            with open(filepath, 'r') as f: source = f.read()
            tokens, _ = Leksikal(source, filepath).buat_token()
            ast_root = Pengurai(tokens).urai()

            if not ast_root: continue

            dir_context = os.path.dirname(filepath)

            for stmt in ast_root.daftar_pernyataan:
                if isinstance(stmt, AmbilSebagian):
                    target_path = stmt.path_file.nilai
                    symbols_needed = [t.nilai for t in stmt.daftar_simbol]

                    # print(f"Checking symbols {symbols_needed} from {target_path}...")

                    # Load Module in VM to inspect exports
                    # Note: This executes module body!
                    try:
                        # Path Hack for VM load
                        load_path = target_path
                        if "cotc(stdlib)" in target_path:
                            load_path = target_path.replace("cotc(stdlib)", "greenfield/cotc/stdlib")
                        elif not os.path.isabs(target_path):
                             # Make relative path relative to root for VM
                             load_path = os.path.join(dir_context, target_path)

                        exports = vm.load_module(load_path)

                        for sym in symbols_needed:
                            if sym not in exports:
                                print(f"  [X] ERROR in {filepath}: Symbol '{sym}' not found in '{target_path}'")
                                print(f"      Available: {list(exports.keys())}")
                                passed = False
                            # else:
                            #     print(f"      [v] {sym} OK")

                    except Exception as e:
                        print(f"  [!] Failed to load module '{target_path}' for symbol check: {e}")
                        # passed = False # Don't fail step 3 if module load fails (Step 4 catches this), just warning

        except Exception:
            pass

    if passed: print("All symbols resolved correctly.")
    return passed

def step_4_verify_ivm_execution(files):
    """
    Langkah 4: Verifikasi dengan IVM (Runtime)
    Mencoba memuat setiap file sebagai modul utama.
    """
    print_step(4, "Verifikasi Eksekusi IVM (Runtime Load)")
    passed = True
    vm = StandardVM()

    for filepath in files:
        print(f"Running {filepath}...", end=" ")
        try:
            # We verify we can LOAD the module without crashing.
            # Executing logic (like calling main) is specific to entry points.
            vm.load_module(filepath)
            print("OK")
        except Exception as e:
            print(f"FAIL: {e}")
            passed = False

    return passed

def main():
    print("=== GREENFIELD 4-STEP VERIFICATION TOOL ===")

    files = glob.glob(os.path.join(GREENFIELD_DIR, "*.fox"))
    files.sort()

    if not files:
        print(f"No .fox files found in {GREENFIELD_DIR}")
        return

    # RUN STEPS
    if not step_1_verify_per_line(files):
        print("\n[STOP] Step 1 Failed. Fix syntax errors first.")
        sys.exit(1)

    if not step_2_verify_dependencies(files):
        print("\n[STOP] Step 2 Failed. Fix missing files.")
        sys.exit(1)

    if not step_3_verify_compatibility(files):
        print("\n[STOP] Step 3 Failed. Fix missing symbols.")
        sys.exit(1)

    if not step_4_verify_ivm_execution(files):
        print("\n[STOP] Step 4 Failed. Fix runtime errors.")
        sys.exit(1)

    print("\n" + "="*40)
    print("✅ VERIFICATION SUCCESSFUL! System is Robust.")
    print("="*40)

if __name__ == "__main__":
    main()
