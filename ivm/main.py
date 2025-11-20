# ivm/main.py
import sys
import argparse
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM

def main():
    parser = argparse.ArgumentParser(description="Fox VM Runner")
    parser.add_argument("file", help="Path to the .fox file to execute")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    lexer = Leksikal(source)
    tokens, errors = lexer.buat_token()
    if errors:
        print("Lexer Errors:")
        for err in errors:
            print(err)
        sys.exit(1)

    parser = Pengurai(tokens)
    ast = parser.urai()
    if not ast:
        print("Parser Failed. Errors:")
        for err in parser.daftar_kesalahan:
            print(err)
        sys.exit(1)

    compiler = Compiler()
    instructions = compiler.compile(ast)

    vm = FoxVM()
    vm.run(instructions)

if __name__ == "__main__":
    main()
