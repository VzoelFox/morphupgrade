import sys
import os

# Add repository root to sys.path
sys.path.append(os.getcwd())

from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM

def test_jodohkan():
    # Use explicit newlines to avoid indentation confusion
    code = """biar x = 10
jodohkan x dengan
| 1 maka
    tulis("Satu")
| 10 maka
    tulis("Sepuluh")
| _ maka
    tulis("Lainnya")
akhir

jodohkan 5 dengan
| 1 maka
    tulis("Satu")
| 5 maka
    tulis("Lima")
akhir

jodohkan 99 dengan
| 1 maka
    tulis("1")
| _ maka
    tulis("Wildcard worked")
akhir
"""

    print("--- Parsing ---")
    lexer = Leksikal(code)
    tokens, errors = lexer.buat_token()
    if errors:
        print("Lexer Errors:", errors)
        return

    parser = Pengurai(tokens)
    ast = parser.urai()
    if not ast:
        print("Parser failed. Errors:")
        for err in parser.daftar_kesalahan:
            print(err)
        return

    print("--- Compiling ---")
    compiler = Compiler()
    instructions = compiler.compile(ast)

    print("\n--- Bytecode ---")
    for i, instr in enumerate(instructions):
        print(f"{i}: {instr}")

    print("\n--- Running Standard VM ---")
    vm = FoxVM()
    vm.run(instructions)

if __name__ == "__main__":
    test_jodohkan()
