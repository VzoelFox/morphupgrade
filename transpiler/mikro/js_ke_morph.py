# transpiler/mikro/js_ke_morph.py
# PATCH-TRANS-003B: Implementasi Awal Transpiler-Mikro JS ke MORPH
# PATCH-TRANS-003C: Memperbaiki penanganan preseden dan EmptyStatement

import sys
import os
from pyjsparser import parse

class TranspilerJsKeMorph:
    """
    Menerjemahkan AST JavaScript (dari pyjsparser) ke dalam kode sumber MORPH.
    Fokus pada subset fitur yang sangat terbatas untuk PoC.
    """
    def __init__(self):
        self.kode_morph = []

    def terjemahkan(self, kode_js):
        """Fungsi utama untuk memulai proses penerjemahan."""
        try:
            pohon_ast = parse(kode_js)
            self._kunjungi(pohon_ast)
            return "".join(self.kode_morph).strip()
        except Exception as e:
            return f"# Gagal menerjemahkan: {repr(e)}"

    def _kunjungi(self, node):
        """Dispatcher manual untuk menelusuri AST dari pyjsparser."""
        if not isinstance(node, dict) or 'type' not in node:
            return

        tipe_node = node['type']
        nama_metode = f'_kunjungi_{tipe_node}'
        metode = getattr(self, nama_metode, self._kunjungan_umum)
        metode(node)

    def _kunjungi_Program(self, node):
        for i, item in enumerate(node['body']):
            # Jangan tambahkan newline jika statement-nya kosong
            if item['type'] == 'EmptyStatement':
                continue
            self._kunjungi(item)
            if i < len(node['body']) - 1:
                self.kode_morph.append("\n")

    def _kunjungi_VariableDeclaration(self, node):
        deklarasi = node['declarations'][0]
        nama_var = deklarasi['id']['name']
        self.kode_morph.append(f"biar {nama_var} = ")
        self._kunjungi(deklarasi['init'])

    def _kunjungi_ExpressionStatement(self, node):
        self._kunjungi(node['expression'])

    def _kunjungi_EmptyStatement(self, node):
        # Abaikan titik koma yang berdiri sendiri
        pass

    def _kunjungi_CallExpression(self, node):
        if (node['callee']['type'] == 'MemberExpression' and
                node['callee']['object']['name'] == 'console' and
                node['callee']['property']['name'] == 'log'):
            self.kode_morph.append("tulis(")
            for i, arg in enumerate(node['arguments']):
                if i > 0: self.kode_morph.append(", ")
                self._kunjungi(arg)
            self.kode_morph.append(")")
        else:
            self.kode_morph.append("# Panggilan fungsi kompleks tidak didukung")

    def _kunjungi_BinaryExpression(self, node):
        # FIX: Logika preseden yang lebih baik, mirip dengan transpiler Python
        is_left_binop = node['left']['type'] == 'BinaryExpression'
        is_right_binop = node['right']['type'] == 'BinaryExpression'

        if is_left_binop: self.kode_morph.append("(")
        self._kunjungi(node['left'])
        if is_left_binop: self.kode_morph.append(")")

        self.kode_morph.append(f" {node['operator']} ")

        if is_right_binop: self.kode_morph.append("(")
        self._kunjungi(node['right'])
        if is_right_binop: self.kode_morph.append(")")

    def _kunjungi_Identifier(self, node):
        self.kode_morph.append(node['name'])

    def _kunjungi_Literal(self, node):
        nilai = node['value']
        if isinstance(nilai, str):
            self.kode_morph.append(f'"{nilai}"')
        elif isinstance(nilai, bool):
            self.kode_morph.append("benar" if nilai else "salah")
        elif isinstance(nilai, (int, float)) and nilai == int(nilai):
            # Konversi float ke int jika memungkinkan (misal: 10.0 -> 10)
            self.kode_morph.append(str(int(nilai)))
        else:
            self.kode_morph.append(str(nilai))

    def _kunjungan_umum(self, node):
        self.kode_morph.append(f"# Node JS tipe '{node['type']}' tidak didukung")


def main():
    """Fungsionalitas CLI untuk menjalankan transpiler."""
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_js> <file_output_fox>")
        sys.exit(1)

    path_input = sys.argv[1]
    path_output = sys.argv[2]

    try:
        with open(path_input, 'r', encoding='utf-8') as f:
            kode_sumber_js = f.read()

        transpiler = TranspilerJsKeMorph()
        kode_hasil_morph = transpiler.terjemahkan(kode_sumber_js)

        with open(path_output, 'w', encoding='utf-8') as f:
            f.write(kode_hasil_morph)

        print(f"Penerjemahan berhasil: '{path_input}' -> '{path_output}'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
