
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))

from ivm.vms.standard_vm import StandardVM

def test_lexer():
    print("--- Testing Greenfield Lexer (Bootstrap) ---")
    vm = StandardVM()

    # Create a test wrapper script in Morph to load and run the Lexer
    # This script mimics how another Morph module would use lx_morph
    test_script = """
ambil_semua "greenfield/lx_morph.fox" sebagai LX
ambil_sebagian TipeToken dari "greenfield/morph_t.fox"

fungsi main() maka
    biar source = "biar x = 10"
    biar lexer = LX.Leksikal(source, "test_input.fox")

    # Debugging: Cek apakah lexer berhasil dibuat
    tulis("Lexer created:", lexer)

    biar hasil = lexer.buat_token()
    biar tokens = hasil[0]
    biar errors = hasil[1]

    tulis("Tokens count:", panjang(tokens))

    # Print first few tokens types
    jika panjang(tokens) > 0 maka
        tulis("First token type:", tokens[0].tipe)
    akhir
akhir

main()
"""
    # Write this temporary test script
    with open("greenfield/test_lexer_wrapper.fox", "w") as f:
        f.write(test_script)

    try:
        vm.load_module("greenfield/test_lexer_wrapper.fox")
        print("Test Finished Successfully")
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lexer()
