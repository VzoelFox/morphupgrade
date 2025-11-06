# transpiler/mikro/python_ke_morph.py
# PATCH-TRANS-002A: Implementasi Awal Transpiler-Mikro Python ke MORPH

import ast

class TranspilerPyKeMorph(ast.NodeVisitor):
    """
    Menerjemahkan AST Python ke dalam kode sumber MORPH.
    Fokus pada subset fitur yang sangat terbatas untuk PoC.
    """
    def __init__(self):
        self.kode_morph = []

    def terjemahkan(self, kode_python):
        """Fungsi utama untuk memulai proses penerjemahan."""
        try:
            pohon_ast = ast.parse(kode_python)
            self.visit(pohon_ast)
            # Menggunakan strip() untuk menghapus newline ekstra di akhir
            return "".join(self.kode_morph).strip()
        except Exception as e:
            return f"# Gagal menerjemahkan: {e}"

    # --- Metode Visitor per Node ---

    def visit_Module(self, node):
        """Mulai dari root AST."""
        for i, item in enumerate(node.body):
            self.visit(item)
            # Tambah baris baru antar pernyataan, kecuali yang terakhir
            if i < len(node.body) - 1:
                self.kode_morph.append("\n")

    def visit_Assign(self, node):
        """Menerjemahkan assignment: x = 10 -> biar x = 10"""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            nama_var = node.targets[0].id
            self.kode_morph.append(f"biar {nama_var} = ")
            self.visit(node.value)
        else:
            self.kode_morph.append("# Assignment kompleks tidak didukung")

    def visit_Expr(self, node):
        """Menerjemahkan sebuah ekspresi (misal: panggilan fungsi)."""
        self.visit(node.value)

    def visit_Call(self, node):
        """Menerjemahkan panggilan fungsi (fokus pada print)."""
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.kode_morph.append("tulis(")
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.kode_morph.append(", ")
                self.visit(arg)
            self.kode_morph.append(")")
        else:
            nama_fungsi = getattr(node.func, 'id', 'fungsi_tidak_dikenal')
            self.kode_morph.append(f"# Panggilan fungsi '{nama_fungsi}' tidak didukung")

    def visit_Constant(self, node):
        """Menerjemahkan konstanta (angka, teks, boolean)."""
        if isinstance(node.value, str):
            self.kode_morph.append(f'"{node.value}"')
        elif isinstance(node.value, bool):
            self.kode_morph.append("benar" if node.value else "salah")
        else:
            self.kode_morph.append(str(node.value))

    def visit_Name(self, node):
        """Menerjemahkan nama variabel."""
        self.kode_morph.append(node.id)

    def visit_BinOp(self, node):
        """Menerjemahkan operasi biner dengan penanganan preseden."""
        is_left_binop = isinstance(node.left, ast.BinOp)
        is_right_binop = isinstance(node.right, ast.BinOp)

        if is_left_binop:
            self.kode_morph.append("(")
        self.visit(node.left)
        if is_left_binop:
            self.kode_morph.append(")")

        self.kode_morph.append(f" {self._terjemahkan_operator(node.op)} ")

        if is_right_binop:
            self.kode_morph.append("(")
        self.visit(node.right)
        if is_right_binop:
            self.kode_morph.append(")")

    def _terjemahkan_operator(self, op):
        """Helper untuk menerjemahkan objek operator AST ke simbol."""
        if isinstance(op, ast.Add): return '+'
        if isinstance(op, ast.Sub): return '-'
        if isinstance(op, ast.Mult): return '*'
        if isinstance(op, ast.Div): return '/'
        return '?'

    def generic_visit(self, node):
        """Fallback untuk node yang tidak kita tangani secara eksplisit."""
        self.kode_morph.append(f"# Node tipe '{type(node).__name__}' tidak didukung")

def main():
    """Fungsionalitas CLI untuk menjalankan transpiler."""
    import sys
    if len(sys.argv) != 3:
        print("Penggunaan: python <script> <file_input_py> <file_output_fox>")
        sys.exit(1)

    path_input = sys.argv[1]
    path_output = sys.argv[2]

    try:
        with open(path_input, 'r', encoding='utf-8') as f:
            kode_sumber_python = f.read()

        transpiler = TranspilerPyKeMorph()
        kode_hasil_morph = transpiler.terjemahkan(kode_sumber_python)

        with open(path_output, 'w', encoding='utf-8') as f:
            f.write(kode_hasil_morph)

        print(f"Penerjemahan berhasil: '{path_input}' -> '{path_output}'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
