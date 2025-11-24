
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))

from ivm.vms.standard_vm import StandardVM

def test_parser():
    print("--- Testing Greenfield Parser (Bootstrap) ---")
    vm = StandardVM()

    # Create a test wrapper script in Morph to load and run the Parser
    test_script = """
ambil_semua "greenfield/lx_morph.fox" sebagai LX
ambil_semua "greenfield/crusher.fox" sebagai CR
ambil_semua "greenfield/absolute_syntax_morph.fox" sebagai AST

fungsi main() maka
    # Test Case: Simple Assignment and Function Call
    biar source = "biar x = 10\\n tulis(x)"

    tulis("Source Code:", source)

    # 1. Lexing
    biar lexer = LX.Leksikal(source, "test_parser_input.fox")
    biar hasil_lex = lexer.buat_token()
    biar tokens = hasil_lex[0]
    biar errors_lex = hasil_lex[1]

    jika panjang(errors_lex) > 0 maka
        tulis("Lexer Error:", errors_lex)
        kembali nil
    akhir

    tulis("Lexing Success. Token Count:", panjang(tokens))

    # 2. Parsing
    biar parser = CR.Pengurai(tokens)
    biar ast_result = parser.urai()

    jika ast_result == nil maka
        tulis("Parser Error Occurred")
        tulis("Errors:", parser.daftar_kesalahan)
    lain
        tulis("Parsing Success!")
        tulis("AST Result:", ast_result)
        tulis("Number of statements:", panjang(ast_result.daftar_pernyataan))
    akhir
akhir

main()
"""
    # Write this temporary test script
    with open("greenfield/test_parser_wrapper.fox", "w") as f:
        f.write(test_script)

    try:
        vm.load_module("greenfield/test_parser_wrapper.fox")
        print("Test Finished Successfully")
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
