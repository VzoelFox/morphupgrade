# transpiler/mikro/morph_ke_python.py
# PATCH-TRANS-002B: Implementasi Awal Transpiler-Mikro MORPH ke Python
# PATCH-TRANS-002C: Memperbaiki inkonsistensi nama metode (visit vs kunjungi)

import sys
import os

# Menambahkan path ke `morph_engine` agar bisa diimpor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.penerjemah import PengunjungNode
from morph_engine.node_ast import NodeOperasiBiner, NodeAngka, NodeDeklarasiVariabel, NodePengenal, NodeTeks, NodeBoolean, NodePanggilFungsi, NodeProgram

class TranspilerMorphKePy(PengunjungNode):
    """
    Menerjemahkan AST MORPH ke dalam kode sumber Python.
    Fokus pada subset fitur yang sangat terbatas untuk PoC.
    """
    def __init__(self, pohon_ast):
        self.pohon_ast = pohon_ast
        self.kode_python = []

    def terjemahkan(self):
        """Fungsi utama untuk memulai proses penerjemahan."""
        try:
            # FIX: Panggil metode yang benar dari kelas dasar
            self.kunjungi(self.pohon_ast)
            return "".join(self.kode_python).strip()
        except Exception as e:
            # Menggunakan repr(e) untuk mendapatkan detail exception yang lebih baik
            return f"# Gagal menerjemahkan: {repr(e)}"

    # FIX: Mengganti nama semua metode visit_* menjadi kunjungi_*
    def kunjungi_NodeProgram(self, node):
        for i, pernyataan in enumerate(node.daftar_pernyataan):
            self.kunjungi(pernyataan)
            if i < len(node.daftar_pernyataan) - 1:
                self.kode_python.append("\n")

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai
        self.kode_python.append(f"{nama_var} = ")
        self.kunjungi(node.nilai)

    def kunjungi_NodePanggilFungsi(self, node):
        if isinstance(node.nama_fungsi, NodePengenal) and node.nama_fungsi.nilai == 'tulis':
            self.kode_python.append("print(")
        else:
            self.kunjungi(node.nama_fungsi)
            self.kode_python.append("(")

        for i, arg in enumerate(node.daftar_argumen):
            if i > 0:
                self.kode_python.append(", ")
            self.kunjungi(arg)
        self.kode_python.append(")")

    def kunjungi_NodeOperasiBiner(self, node):
        is_left_binop = isinstance(node.kiri, NodeOperasiBiner)
        is_right_binop = isinstance(node.kanan, NodeOperasiBiner)

        if is_left_binop: self.kode_python.append("(")
        self.kunjungi(node.kiri)
        if is_left_binop: self.kode_python.append(")")

        self.kode_python.append(f" {node.operator.nilai} ")

        if is_right_binop: self.kode_python.append("(")
        self.kunjungi(node.kanan)
        if is_right_binop: self.kode_python.append(")")

    def kunjungi_NodePengenal(self, node):
        self.kode_python.append(node.nilai)

    def kunjungi_NodeAngka(self, node):
        self.kode_python.append(str(node.nilai))

    def kunjungi_NodeTeks(self, node):
        self.kode_python.append(f'"{node.nilai}"')

    def kunjungi_NodeBoolean(self, node):
        self.kode_python.append("True" if node.nilai else "False")

    def kunjungan_umum(self, node):
        """Fallback untuk node yang tidak kita tangani secara eksplisit."""
        self.kode_python.append(f"# Node tipe '{type(node).__name__}' tidak didukung")


def main():
    """Fungsionalitas CLI untuk menjalankan transpiler."""
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_fox> <file_output_py>")
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

        transpiler = TranspilerMorphKePy(ast_morph)
        kode_hasil_python = transpiler.terjemahkan()

        with open(path_output, 'w', encoding='utf-8') as f:
            f.write(kode_hasil_python)

        print(f"Penerjemahan berhasil: '{path_input}' -> '{path_output}'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
