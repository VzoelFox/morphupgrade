
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))

from ivm.vms.standard_vm import StandardVM

def verify_error_reporting():
    print("--- Verifying Error Reporting (Self-Hosted) ---")
    vm = StandardVM()

    # Create a wrapper script that imports greenfield/morph.fox and calls jalankan_sumber with ERROR CODE
    wrapper_script = """
ambil_semua "greenfield/morph.fox" sebagai M

fungsi main() maka
    biar compiler = M.MorphMain()

    # Test Source Code: Contains Syntax Error (Missing 'maka' after 'jika')
    biar source_code = "fungsi halo() maka \\n jika benar \\n tulis('Salah') \\n akhir \\n akhir"

    tulis("=== Input Source Code (Dengan Error) ===")
    tulis(source_code)
    tulis("=========================================")

    compiler.jalankan_sumber(source_code, "error_test.fox")
akhir

main()
"""
    with open("verify_error_reporting.fox", "w") as f:
        f.write(wrapper_script)

    try:
        vm.load_module("verify_error_reporting.fox")
        print("Verification Script Finished")
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists("verify_error_reporting.fox"):
            os.remove("verify_error_reporting.fox")

if __name__ == "__main__":
    verify_error_reporting()
