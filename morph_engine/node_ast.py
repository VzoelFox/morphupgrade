# morph_engine/node_ast.py

class NodeAST:
    """Kelas dasar untuk semua node AST."""
    pass

class NodeProgram(NodeAST):
    """Mewakili seluruh program, berisi daftar pernyataan."""
    def __init__(self, daftar_pernyataan):
        self.daftar_pernyataan = daftar_pernyataan

class NodeDeklarasiVariabel(NodeAST):
    """Mewakili deklarasi variabel: 'biar nama = nilai' atau 'tetap nama = nilai'."""
    def __init__(self, jenis_deklarasi, nama_variabel, nilai):
        self.jenis_deklarasi = jenis_deklarasi # 'biar' atau 'tetap'
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class NodePanggilFungsi(NodeAST):
    """Mewakili pemanggilan fungsi: 'tulis("Halo")'."""
    def __init__(self, nama_fungsi, argumen):
        self.nama_fungsi = nama_fungsi
        self.argumen = argumen

class NodePengenal(NodeAST):
    """Mewakili nama variabel atau fungsi."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class NodeTeks(NodeAST):
    """Mewakili nilai teks literal."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai
