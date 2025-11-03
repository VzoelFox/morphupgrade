# morph_engine/node_ast.py
# Changelog:
# - PATCH-010: Menambahkan NodeAssignment untuk membedakan antara deklarasi
#              dan assignment variabel.

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

class NodeAssignment(NodeAST):
    """Mewakili assignment variabel: 'nama = nilai'."""
    def __init__(self, nama_variabel, nilai):
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

# --- Node Baru untuk Sprint 1 ---

class NodeAngka(NodeAST):
    """Mewakili nilai angka (integer atau float)."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class NodeBoolean(NodeAST):
    """Mewakili nilai boolean (benar atau salah)."""
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class NodeOperasiBiner(NodeAST):
    """Mewakili operasi dengan dua operand, contoh: a + b."""
    def __init__(self, kiri, operator, kanan):
        self.kiri = kiri
        self.operator = operator
        self.kanan = kanan

class NodeOperasiUnary(NodeAST):
    """Mewakili operasi dengan satu operand, contoh: -5 atau tidak benar."""
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class NodeJika(NodeAST):
    """Mewakili pernyataan jika-maka."""
    def __init__(self, kondisi, blok_maka):
        self.kondisi = kondisi
        self.blok_maka = blok_maka
