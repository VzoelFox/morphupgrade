# morphupgrade/morph_engine_py/main.py
# Titik Masuk Utama untuk Transpiler Morph-ke-Python

import sys
import os

# Menambahkan path agar bisa mengimpor dari direktori induk
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from morphupgrade.morph_engine_py.leksikal import Leksikal
from morphupgrade.morph_engine_py.pengurai import Pengurai
from morphupgrade.morph_engine_py.generator_py import GeneratorPython

def transpilasi_ke_python(path_file_fox):
    """
    Menjalankan pipeline lengkap: file.fox -> Leksikal -> Pengurai -> Generator -> file.py
    """
    try:
        with open(path_file_fox, 'r', encoding='utf-8') as f:
            sumber_kode = f.read()
    except FileNotFoundError:
        print(f"Kesalahan: File sumber '{path_file_fox}' tidak ditemukan.")
        sys.exit(1)

    # 1. Leksikal
    lexer = Leksikal(sumber_kode)
    # Leksikal lama melempar exception, bukan mengembalikan tuple error
    try:
        tokens = lexer.buat_token()
    except Exception as e:
        print(f"Kesalahan Leksikal ditemukan: {e}")
        sys.exit(1)

    # 2. Pengurai
    parser = Pengurai(tokens)
    ast = parser.urai()
    if parser.daftar_kesalahan:
        print("Kesalahan Sintaks ditemukan:")
        for err in parser.daftar_kesalahan:
            print(err)
        sys.exit(1)

    # 3. Generator
    generator = GeneratorPython(ast)
    kode_python = generator.generate()

    # 4. Tulis ke file output
    path_file_py = os.path.splitext(path_file_fox)[0] + ".py"
    with open(path_file_py, 'w', encoding='utf-8') as f:
        f.write("# Dihasilkan oleh Transpiler MORPH-ke-Python\n")
        f.write("#\n")
        f.write(kode_python)

    print(f"Transpilasi berhasil: '{path_file_fox}' -> '{path_file_py}'")
    return path_file_py


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Penggunaan: python -m morphupgrade.morph_engine_py.main <nama_file.fox>")
        sys.exit(1)

    file_input = sys.argv[1]
    transpilasi_ke_python(file_input)
