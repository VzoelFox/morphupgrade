# morph_engine/main.py
import sys
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter

def jalankan(nama_file):
    """Fungsi utama untuk menjalankan program Morph dari file."""
    try:
        with open(nama_file, 'r', encoding='utf-8') as f:
            konten = f.read()
    except FileNotFoundError:
        print(f"Error: File '{nama_file}' tidak ditemukan.")
        sys.exit(1)

    if not konten.strip():
        # File kosong, tidak perlu melakukan apa-apa.
        return

    # 1. Lexer: Teks -> Token
    lexer = Lexer(konten)
    daftar_token = lexer.buat_token()

    # 2. Parser: Token -> AST
    parser = Parser(daftar_token)
    try:
        ast = parser.parse()
    except SyntaxError as e:
        print(e)
        sys.exit(1)

    # 3. Interpreter: AST -> Eksekusi
    interpreter = Interpreter(ast)
    try:
        interpreter.interpretasi()
    except NameError as e:
        print(e)
        sys.exit(1)
