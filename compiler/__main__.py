# compiler/__main__.py
import sys
from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from .codegen_llvm import LLVMCodeGenerator

def main():
    if len(sys.argv) != 2:
        print("Penggunaan: python -m compiler <file.fox>")
        return 1

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Kesalahan: File tidak ditemukan di '{filepath}'")
        return 1

    try:
        # Gunakan lexer/parser yang sudah ada dari interpreter
        tokens = Leksikal(code).buat_token()
        ast = Pengurai(tokens).urai()

        if ast is None:
            # Pengurai mungkin mengembalikan None jika ada kesalahan fatal
            print("Gagal mengurai program karena kesalahan sintaks.", file=sys.stderr)
            return 1

        # Hasilkan LLVM IR dari AST
        codegen = LLVMCodeGenerator()
        ir_module = codegen.generate_code(ast)

        print("; MORPH Compiler - LLVM IR Output")
        print(";" + "="*30)
        print(str(ir_module))
        print(";" + "="*30)

    except Exception as e:
        # Menangkap kesalahan dari lexer, parser, atau codegen
        print(f"Terjadi kesalahan saat kompilasi: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
