import sys
import os

# Add repo root to path
sys.path.append(os.getcwd())

from transisi.lx import Leksikal
from transisi.crusher import Pengurai

def debug_file(filepath):
    print(f"Parsing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = Leksikal(source, filepath)
    tokens, errors = lexer.buat_token()
    if errors:
        print("Lexer Errors:")
        for e in errors:
            print(e)
        return

    parser = Pengurai(tokens)
    try:
        ast = parser.urai()
        if parser.daftar_kesalahan:
            print("Parser Errors:")
            for t, msg in parser.daftar_kesalahan:
                print(f"Line {t.baris}, Col {t.kolom}: {msg}")
        else:
            print("Parsing SUCCESS!")
    except Exception as e:
        print(f"Parser Crashed: {e}")
        if parser.daftar_kesalahan:
            print("Last recorded errors:")
            for t, msg in parser.daftar_kesalahan:
                print(f"Line {t.baris}, Col {t.kolom}: {msg}")

if __name__ == "__main__":
    debug_file("greenfield/absolute_syntax_morph.fox")
