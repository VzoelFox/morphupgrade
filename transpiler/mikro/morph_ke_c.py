# transpiler/mikro/morph_ke_c.py
# PATCH-TRANS-004A: Implementasi Awal Transpiler-Mikro MORPH ke C
# PATCH-TRANS-004D: Perbaikan final inferensi tipe untuk ekspresi dan printf

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.penerjemah import PengunjungNode
from morph_engine.node_ast import *

class TranspilerMorphKeC(PengunjungNode):
    """Menerjemahkan AST MORPH ke dalam kode sumber C."""
    def __init__(self, pohon_ast):
        self.pohon_ast = pohon_ast
        self.kode_c = []
        self.tipe_variabel = {}

    def terjemahkan(self):
        try:
            self.kode_c.append('#include <stdio.h>\n\n')
            self.kode_c.append('int main() {\n')
            self.kunjungi(self.pohon_ast)
            self.kode_c.append('\n    return 0;\n}')
            return "".join(self.kode_c)
        except Exception as e:
            return f"// Gagal menerjemahkan: {repr(e)}"

    def kunjungi_NodeProgram(self, node):
        for pernyataan in node.daftar_pernyataan:
            self.kode_c.append("    ")
            self.kunjungi(pernyataan)
            self.kode_c.append(";\n")

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai

        tipe_c = self._infer_tipe_node(node.nilai)
        self.tipe_variabel[nama_var] = tipe_c

        self.kode_c.append(f"{tipe_c} {nama_var} = ")
        self.kunjungi(node.nilai)

    def _infer_tipe_node(self, node):
        """Helper untuk menginfer tipe C dari sebuah node AST MORPH."""
        if isinstance(node, NodeAngka):
            return "double" if isinstance(node.nilai, float) else "int"
        if isinstance(node, NodeTeks):
            return "const char*"
        if isinstance(node, NodeBoolean):
            return "int"
        if isinstance(node, NodeOperasiBiner):
            # Prioritaskan tipe double jika salah satu sisinya double
            tipe_kiri = self._infer_tipe_node(node.kiri)
            tipe_kanan = self._infer_tipe_node(node.kanan)
            return "double" if "double" in (tipe_kiri, tipe_kanan) else "int"
        if isinstance(node, NodePengenal):
            # FIX: Cari tipe variabel yang sudah disimpan
            return self.tipe_variabel.get(node.nilai, "int") # Asumsi int jika tidak ada
        return "void"

    def kunjungi_NodePanggilFungsi(self, node):
        if isinstance(node.nama_fungsi, NodePengenal) and node.nama_fungsi.nilai == 'tulis':
            self.kode_c.append('printf(')
            format_string = []
            args_printf = []

            for i, arg in enumerate(node.daftar_argumen):
                if i > 0: format_string.append(" ")

                if isinstance(arg, NodeTeks):
                    format_string.append(arg.nilai.replace("%", "%%"))
                else:
                    tipe_arg = self._infer_tipe_node(arg)
                    if tipe_arg == "int": format_string.append("%d")
                    elif tipe_arg == "double": format_string.append("%f")
                    elif tipe_arg == "const char*": format_string.append("%s")
                    else: format_string.append("[TIPE_TIDAK_DIKETAHUI]")

                    if isinstance(arg, NodePengenal):
                        args_printf.append(arg.nilai)
                    else:
                        args_printf.append(self.kunjungi_to_string(arg))

            self.kode_c.append(f'"{ "".join(format_string) }\\n"')
            if args_printf:
                self.kode_c.append(f', {", ".join(args_printf)}')
            self.kode_c.append(')')
        else:
            self.kode_c.append("// Panggilan fungsi selain 'tulis' tidak didukung")

    def kunjungi_NodeOperasiBiner(self, node):
        self.kode_c.append("(")
        self.kunjungi(node.kiri)
        self.kode_c.append(f" {node.operator.nilai} ")
        self.kunjungi(node.kanan)
        self.kode_c.append(")")

    def kunjungi_NodePengenal(self, node):
        self.kode_c.append(node.nilai)

    def kunjungi_NodeAngka(self, node):
        self.kode_c.append(str(node.nilai))

    def kunjungi_NodeTeks(self, node):
        self.kode_c.append(f'"{node.nilai}"')

    def kunjungi_NodeBoolean(self, node):
        self.kode_c.append("1" if node.nilai else "0")

    def kunjungan_umum(self, node):
        self.kode_c.append(f"// Node tipe '{type(node).__name__}' tidak didukung")

    def kunjungi_to_string(self, node):
        original_kode_c = self.kode_c
        self.kode_c = []
        self.kunjungi(node)
        result = "".join(self.kode_c)
        self.kode_c = original_kode_c
        return result

def main():
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_fox> <file_output_c>")
        sys.exit(1)

    path_input, path_output = sys.argv[1], sys.argv[2]

    try:
        with open(path_input, 'r', encoding='utf-8') as f:
            kode_sumber_morph = f.read()

        leksikal = Leksikal(kode_sumber_morph)
        tokens = leksikal.buat_token()
        pengurai = Pengurai(tokens)
        ast_morph = pengurai.urai()

        transpiler = TranspilerMorphKeC(ast_morph)
        kode_hasil_c = transpiler.terjemahkan()

        with open(path_output, 'w', encoding='utf-8') as f:
            f.write(kode_hasil_c)

        print(f"Penerjemahan berhasil: '{path_input}' -> '{path_output}'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
