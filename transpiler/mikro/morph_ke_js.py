# transpiler/mikro/morph_ke_js.py
# PATCH-TRANS-003A: Implementasi Awal Transpiler-Mikro MORPH ke JS

import sys
import os

# Menambahkan path ke `morph_engine` agar bisa diimpor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.penerjemah import PengunjungNode
from morph_engine.node_ast import NodeOperasiBiner, NodeAngka, NodeDeklarasiVariabel, NodePengenal, NodeTeks, NodeBoolean, NodePanggilFungsi, NodeProgram

class TranspilerMorphKeJs(PengunjungNode):
    """
    Menerjemahkan AST MORPH ke dalam kode sumber JavaScript.
    Fokus pada subset fitur yang sangat terbatas untuk PoC.
    """
    def __init__(self, pohon_ast):
        self.pohon_ast = pohon_ast
        self.kode_js = []

    def terjemahkan(self):
        """Fungsi utama untuk memulai proses penerjemahan."""
        try:
            self.kunjungi(self.pohon_ast)
            return "".join(self.kode_js).strip()
        except Exception as e:
            return f"// Gagal menerjemahkan: {repr(e)}"

    def kunjungi_NodeProgram(self, node):
        for i, pernyataan in enumerate(node.daftar_pernyataan):
            self.kunjungi(pernyataan)
            # JavaScript menggunakan titik koma di akhir baris
            self.kode_js.append(";")
            if i < len(node.daftar_pernyataan) - 1:
                self.kode_js.append("\n")

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai
        # Menggunakan 'let' untuk deklarasi variabel di JS
        self.kode_js.append(f"let {nama_var} = ")
        self.kunjungi(node.nilai)

    def kunjungi_NodePanggilFungsi(self, node):
        if isinstance(node.nama_fungsi, NodePengenal) and node.nama_fungsi.nilai == 'tulis':
            self.kode_js.append("console.log(")
        else:
            self.kunjungi(node.nama_fungsi)
            self.kode_js.append("(")

        for i, arg in enumerate(node.daftar_argumen):
            if i > 0:
                self.kode_js.append(", ")
            self.kunjungi(arg)
        self.kode_js.append(")")

    def kunjungi_NodeOperasiBiner(self, node):
        is_left_binop = isinstance(node.kiri, NodeOperasiBiner)
        is_right_binop = isinstance(node.kanan, NodeOperasiBiner)

        if is_left_binop: self.kode_js.append("(")
        self.kunjungi(node.kiri)
        if is_left_binop: self.kode_js.append(")")

        self.kode_js.append(f" {node.operator.nilai} ")

        if is_right_binop: self.kode_js.append("(")
        self.kunjungi(node.kanan)
        if is_right_binop: self.kode_js.append(")")

    def kunjungi_NodePengenal(self, node):
        self.kode_js.append(node.nilai)

    def kunjungi_NodeAngka(self, node):
        self.kode_js.append(str(node.nilai))

    def kunjungi_NodeTeks(self, node):
        # JS umumnya menggunakan kutip ganda, jadi kita konsisten
        self.kode_js.append(f'"{node.nilai}"')

    def kunjungi_NodeBoolean(self, node):
        # JS menggunakan 'true' dan 'false' (huruf kecil)
        self.kode_js.append("true" if node.nilai else "false")

    def kunjungan_umum(self, node):
        self.kode_js.append(f"// Node tipe '{type(node).__name__}' tidak didukung")


def main():
    """Fungsionalitas CLI untuk menjalankan transpiler."""
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_fox> <file_output_js>")
        sys.exit(1)

    path_input = sys.argv[1]
    path_output = sys.argv[2]

    try:
        with open(path_input, 'r', encoding='utf-8') as f:
            kode_sumber_morph = f.read()

        leksikal = Leksikal(kode_sumber_morph)
        tokens = leksikal.buat_token()
        pengurai = Pengurai(tokens)
        ast_morph = pengurai.urai()

        transpiler = TranspilerMorphKeJs(ast_morph)
        kode_hasil_js = transpiler.terjemahkan()

        with open(path_output, 'w', encoding='utf-8') as f:
            f.write(kode_hasil_js)

        print(f"Penerjemahan berhasil: '{path_input}' -> '{path_output}'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
