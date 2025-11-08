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

    def visit_NodeAssignment(self, node):
        var_name = self.visit(node.nama_variabel)
        value_code = self.visit(node.nilai)
        self.python_code.append(f"{self._indent()}{var_name} = {value_code}\n")

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
        nama_fungsi = self.visit(node.nama_fungsi)
        args = ", ".join([self.visit(arg) for arg in node.daftar_argumen])

        # Terjemahkan fungsi bawaan
        if nama_fungsi == 'tulis':
            return f"print({args})"

        # Untuk fungsi lain, asumsikan namanya sama dan itu adalah ekspresi
        return f"{nama_fungsi}({args})"

    def visit_NodePernyataanEkspresi(self, node):
        expr_code = self.visit(node.ekspresi)
        if expr_code:
            self.python_code.append(f"{self._indent()}{expr_code}\n")

    def visit_NodeJikaMaka(self, node):
        condition = self.visit(node.kondisi)
        self.python_code.append(f"{self._indent()}if {condition}:\n")

        # Handle blok_maka
        self.indent_level += 1
        for stmt in node.blok_maka:
            self.visit(stmt)
        self.indent_level -= 1

        # Handle lain_jika chains
        if hasattr(node, 'rantai_lain_jika'):
            for lain_jika_kondisi, lain_jika_blok in node.rantai_lain_jika:
                condition_elif = self.visit(lain_jika_kondisi)
                self.python_code.append(f"{self._indent()}elif {condition_elif}:\n")
                self.indent_level += 1
                for stmt in lain_jika_blok:
                    self.visit(stmt)
                self.indent_level -= 1

        # Handle blok_lain
        if node.blok_lain:
            self.python_code.append(f"{self._indent()}else:\n")
            self.indent_level += 1
            for stmt in node.blok_lain:
                self.visit(stmt)
            self.indent_level -= 1

    def visit_NodeSelama(self, node):
        condition = self.visit(node.kondisi)
        self.python_code.append(f"{self._indent()}while {condition}:\n")

        # Handle badan loop
        self.indent_level += 1
        for stmt in node.badan:
            self.visit(stmt)
        self.indent_level -= 1

        # Handle orelse block
        if node.orelse:
            self.python_code.append(f"{self._indent()}else:\n")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1

    def generic_visit(self, node):
        node_type = type(node).__name__
        self.python_code.append(f"{self._indent()}# TODO: {node_type} not yet implemented\n")
        self.python_code.append(f"{self._indent()}raise NotImplementedError('{node_type} transpilation pending')\n")
