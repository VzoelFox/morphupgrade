
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))

from ivm.vms.standard_vm import StandardVM

def verify_greenfield():
    print("--- Verifying Greenfield Pipeline (Self-Hosted) ---")
    vm = StandardVM()

    entry_point = "greenfield/morph.fox"

    # Create a wrapper script that imports greenfield/morph.fox and calls jalankan_sumber
    wrapper_script = """
ambil_semua "greenfield/morph.fox" sebagai M

fungsi main() maka
    biar compiler = M.MorphMain()

    # Test Source Code: A valid Morph program
    biar source_code = "fungsi halo() maka tulis('Halo Dunia') akhir \\n halo()"

    tulis("=== Input Source Code ===")
    tulis(source_code)
    tulis("=========================")

    biar ast = compiler.jalankan_sumber(source_code, "input_test.fox")

    jika ast != nil maka
        tulis("VERIFIKASI SUKSES: Compiler berhasil menghasilkan AST.")
    lain
        tulis("VERIFIKASI GAGAL: Compiler gagal.")
    akhir
akhir

main()
"""
    with open("verify_greenfield_wrapper.fox", "w") as f:
        f.write(wrapper_script)

    try:
        vm.load_module("verify_greenfield_wrapper.fox")
        print("Verification Script Finished")
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists("verify_greenfield_wrapper.fox"):
            os.remove("verify_greenfield_wrapper.fox")

if __name__ == "__main__":
    verify_greenfield()
