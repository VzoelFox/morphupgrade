# morphupgrade/morph_engine_py/generator_py.py
# Backend untuk Transpiler Morph-ke-Python

# Definisi Visitor disalin dari penerjemah.py untuk dependensi lokal
class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

class GeneratorPython(NodeVisitor):
    """
    Visitor yang berjalan di atas AST MORPH dan menghasilkan
    string kode Python yang setara.
    """

    def __init__(self, ast):
        self.ast = ast
        self.python_code = []
        self.indent_level = 0

    def _indent(self):
        return "    " * self.indent_level

    def generate(self):
        """Mulai proses generasi kode."""
        self.visit(self.ast)
        return "".join(self.python_code)

    # --- Metode Visitor untuk setiap Node AST ---

    def visit_NodeProgram(self, node):
        for stmt in node.daftar_pernyataan:
            self.visit(stmt)

    def visit_NodeDeklarasiVariabel(self, node):
        var_name = node.nama_variabel.token.nilai

        if node.jenis_deklarasi.tipe.name == 'TETAP':
            var_name = var_name.upper()

        if node.nilai:
            value_code = self.visit(node.nilai)
            self.python_code.append(f"{self._indent()}{var_name} = {value_code}\n")
        else:
            self.python_code.append(f"{self._indent()}{var_name} = None\n")

    def visit_NodeKonstanta(self, node):
        if isinstance(node.token.nilai, str):
            return f'"{node.token.nilai}"'
        elif isinstance(node.token.nilai, bool):
            return "True" if node.token.nilai else "False"
        elif node.token.nilai is None:
            return "None"
        return str(node.token.nilai)

    def visit_NodeNama(self, node):
        # Asumsi sederhana: jika nama variabel sudah UPPERCASE (dari TETAP), pertahankan.
        if node.token.nilai.isupper():
            return node.token.nilai
        return node.token.nilai

    def visit_NodeOperasiBiner(self, node):
        left = self.visit(node.kiri)
        right = self.visit(node.kanan)
        op = node.op.nilai

        if op == '^':
            op = '**'

        return f"({left} {op} {right})"

    def visit_NodePanggilFungsi(self, node):
        """Mengubah pemanggilan fungsi MORPH menjadi pemanggilan fungsi Python."""
        nama_fungsi = node.nama_fungsi.nilai
        args = ", ".join([self.visit(arg) for arg in node.daftar_argumen])

        # Terjemahkan fungsi bawaan
        if nama_fungsi == 'tulis':
            self.python_code.append(f"{self._indent()}print({args})\n")
            return # Tidak mengembalikan apa-apa karena sudah ditambahkan ke output

        # Untuk fungsi lain, asumsikan namanya sama dan itu adalah ekspresi
        return f"{nama_fungsi}({args})"

    def visit_NodePernyataanEkspresi(self, node):
        expr_code = self.visit(node.ekspresi)
        if expr_code:
            self.python_code.append(f"{self._indent()}{expr_code}\n")

    def generic_visit(self, node):
        self.python_code.append(f"{self._indent()}# Node tipe '{type(node).__name__}' belum didukung\n")
