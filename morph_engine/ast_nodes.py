# morph_engine/ast_nodes.py

class ASTNode:
    """Kelas dasar untuk semua node AST."""
    pass

class ProgramNode(ASTNode):
    """Mewakili seluruh program, berisi daftar pernyataan."""
    def __init__(self, statements):
        self.statements = statements

class DeklarasiVariabelNode(ASTNode):
    """Mewakili deklarasi variabel: 'biar nama = nilai' atau 'tetap nama = nilai'."""
    def __init__(self, jenis_deklarasi, nama_variabel, nilai):
        self.jenis_deklarasi = jenis_deklarasi # 'biar' atau 'tetap'
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class PanggilFungsiNode(ASTNode):
    """Mewakili pemanggilan fungsi: 'tulis("Halo")'."""
    def __init__(self, nama_fungsi, argumen):
        self.nama_fungsi = nama_fungsi
        self.argumen = argumen

class IdentifierNode(ASTNode):
    """Mewakili nama variabel atau fungsi."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class StringNode(ASTNode):
    """Mewakili nilai string literal."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai
