# morph_engine/utama.py
import sys
from .leksikal import Leksikal
from .pengurai import Pengurai
from .penerjemah import Penerjemah

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

    # 1. Leksikal: Teks -> Token
    leksikal = Leksikal(konten)
    daftar_token = leksikal.buat_token()

    # 2. Pengurai: Token -> AST
    pengurai = Pengurai(daftar_token)
    try:
        ast = pengurai.urai()
    except SyntaxError as e:
        print(e)
        sys.exit(1)

    # 3. Penerjemah: AST -> Eksekusi
    penerjemah = Penerjemah(ast)
    try:
        penerjemah.interpretasi()
    except NameError as e:
        print(e)
        sys.exit(1)
