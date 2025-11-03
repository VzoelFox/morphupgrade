# morph_engine/interpreter.py
from .ast_nodes import *

class NodeVisitor:
    """
    Kelas dasar untuk 'mengunjungi' setiap node di AST.
    Secara dinamis memanggil metode visit_<NodeType> berdasarkan tipe node.
    """
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Tidak ada metode visit_{type(node).__name__}')

class Interpreter(NodeVisitor):
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {} # Tabel untuk menyimpan variabel

    def visit_ProgramNode(self, node):
        """Mengeksekusi setiap pernyataan dalam program."""
        for statement in node.statements:
            self.visit(statement)

    def visit_DeklarasiVariabelNode(self, node):
        """Menyimpan variabel dan nilainya ke dalam symbol table."""
        nama_var = node.nama_variabel.nilai
        nilai_var = self.visit(node.nilai)
        self.symbol_table[nama_var] = nilai_var
        # print(f"Deklarasi: {nama_var} = {nilai_var}") # Untuk debug

    def visit_PanggilFungsiNode(self, node):
        """Menangani pemanggilan fungsi, khusus untuk 'tulis'."""
        nama_fungsi = node.nama_fungsi.nilai
        if nama_fungsi == 'tulis':
            argumen = self.visit(node.argumen)
            print(argumen)
        else:
            raise NameError(f"Fungsi '{nama_fungsi}' tidak didefinisikan.")

    def visit_IdentifierNode(self, node):
        """Mengambil nilai variabel dari symbol table."""
        nama_var = node.nilai
        nilai = self.symbol_table.get(nama_var)
        if nilai is None:
            raise NameError(f"Variabel '{nama_var}' tidak didefinisikan.")
        return nilai

    def visit_StringNode(self, node):
        """Mengembalikan nilai literal dari string."""
        return node.nilai

    def interpretasi(self):
        """Memulai proses interpretasi dari node akar (program)."""
        self.visit(self.ast)
