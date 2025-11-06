# transpiler/mikro/c_ke_morph.py
# PATCH-TRANS-004B: Implementasi Awal Transpiler-Mikro C ke MORPH
# PATCH-TRANS-004E: Perbaikan final parsing AST C untuk ekspresi dan literal

import sys
import os
from pycparser import c_parser, c_ast

class TranspilerCKeMorph(c_ast.NodeVisitor):
    """Menerjemahkan AST C (dari pycparser) ke dalam kode sumber MORPH."""
    def __init__(self):
        self.kode_morph = []

    def terjemahkan(self, kode_c):
        try:
            parser = c_parser.CParser()
            ast = parser.parse(kode_c, filename='<stdin>')
            self.visit(ast)
            return "".join(self.kode_morph).strip()
        except Exception as e:
            return f"# Gagal menerjemahkan: {repr(e)}"

    def visit_FileAST(self, node):
        for ext in node.ext:
            if isinstance(ext, c_ast.FuncDef) and ext.decl.name == 'main':
                self.visit(ext.body)

    def visit_Compound(self, node):
        if node.block_items:
            for i, item in enumerate(node.block_items):
                self.visit(item)
                if i < len(node.block_items) - 1:
                    self.kode_morph.append("\n")

    def visit_Decl(self, node):
        nama_var = node.name
        self.kode_morph.append(f'biar {nama_var} = ')
        self.visit(node.init) # Kunjungi node inisialisasi secara rekursif

    def visit_Constant(self, node):
        # FIX: Konversi tipe secara manual
        tipe = node.type
        nilai = node.value
        if tipe == 'int':
            self.kode_morph.append(str(nilai))
        elif tipe == 'string':
            # Hapus kutip yang ditambahkan pycparser
            self.kode_morph.append(nilai)
        else:
            self.kode_morph.append(str(nilai))

    def visit_ID(self, node):
        self.kode_morph.append(node.name)

    def visit_BinaryOp(self, node):
        # FIX: Tangani ekspresi biner
        self.kode_morph.append("(")
        self.visit(node.left)
        self.kode_morph.append(f" {node.op} ")
        self.visit(node.right)
        self.kode_morph.append(")")

    def visit_FuncCall(self, node):
        if node.name.name == 'printf':
            # Asumsi paling sederhana: printf("string literal");
            if node.args and isinstance(node.args.exprs[0], c_ast.Constant):
                nilai_string = node.args.exprs[0].value.strip('"').replace('\\n', '')

                # Cek apakah ada argumen lain (variabel)
                if len(node.args.exprs) > 1:
                    # Hapus penentu format untuk PoC
                    nilai_string = nilai_string.replace("%d", "").strip()
                    self.kode_morph.append(f'tulis("{nilai_string}", ')
                    self.visit(node.args.exprs[1])
                    self.kode_morph.append(')')
                else:
                    self.kode_morph.append(f'tulis("{nilai_string}")')
            else:
                self.kode_morph.append("# printf dengan format kompleks tidak didukung")
        else:
            self.kode_morph.append("# Panggilan fungsi selain printf tidak didukung")

    def generic_visit(self, node):
        pass

def main():
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_c> <file_output_fox>")
        sys.exit(1)
    path_input, path_output = sys.argv[1], sys.argv[2]
    try:
        with open(path_input, 'r', encoding='utf-8') as f:
            kode_sumber_c = f.read()
        transpiler = TranspilerCKeMorph()
        kode_hasil_morph = transpiler.terjemahkan(kode_sumber_c)
        kode_hasil_morph = "\n".join(line for line in kode_hasil_morph.splitlines() if line.strip())
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
