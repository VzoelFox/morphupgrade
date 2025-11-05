# morph_engine/node_ast.py
# Changelog:
# morph_engine/node_ast.py
# Changelog:
# - PATCH-020A: Menambahkan NodeAmbil untuk mendukung fungsi input bawaan.
# - PATCH-019B: Menambahkan NodeArray untuk mendukung sintaks array literal.
# - PATCH-016: Menambahkan NodeFungsiDeklarasi, NodePernyataanKembalikan, dan
#              NodeNil untuk user-defined functions.
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
    def __init__(self, nama_fungsi, daftar_argumen):
        self.nama_fungsi = nama_fungsi
        self.daftar_argumen = daftar_argumen

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

class NodeJikaMaka(NodeAST):
    """
    Mewakili struktur kontrol jika-maka-lain.
    Mendukung 'lain jika' dan 'lain'.
    """
    def __init__(self, kondisi, blok_maka, rantai_lain_jika, blok_lain):
        self.kondisi = kondisi              # Node ekspresi untuk kondisi utama 'jika'
        self.blok_maka = blok_maka          # NodeProgram berisi pernyataan untuk blok 'maka'
        self.rantai_lain_jika = rantai_lain_jika # List dari tuple (kondisi, blok_maka)
        self.blok_lain = blok_lain          # NodeProgram berisi pernyataan untuk blok 'lain', bisa None

class NodeFungsiDeklarasi(NodeAST):
    """Mewakili deklarasi fungsi: 'fungsi nama(p1, p2) maka ... akhir'."""
    def __init__(self, nama_fungsi, parameter, badan):
        self.nama_fungsi = nama_fungsi
        self.parameter = parameter
        self.badan = badan

class NodePernyataanKembalikan(NodeAST):
    """Mewakili pernyataan 'kembalikan nilai'."""
    def __init__(self, nilai_kembalian):
        self.nilai_kembalian = nilai_kembalian

class NodeNil(NodeAST):
    """Mewakili nilai 'nil'."""
    def __init__(self, token):
        self.token = token
        self.nilai = None

class NodeArray(NodeAST):
    """Mewakili array literal: [1, 2, 3]"""
    def __init__(self, elemen):
        self.elemen = elemen  # List of nodes

class NodeAmbil(NodeAST):
    """Mewakili pemanggilan fungsi bawaan 'ambil("prompt")'."""
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node

# --- Node Baru untuk Fitur Perulangan, Kamus, dan Pencocokan Pola ---

class NodeSelama(NodeAST):
    """Mewakili perulangan 'selama': 'selama kondisi maka ... akhir'."""
    def __init__(self, kondisi, badan):
        self.kondisi = kondisi
        self.badan = badan

class NodeKamus(NodeAST):
    """Mewakili literal kamus: '{"kunci": nilai}'."""
    def __init__(self, pasangan):
        # pasangan adalah list dari tuple (NodeKunci, NodeNilai)
        self.pasangan = pasangan

class NodeAksesMember(NodeAST):
    """Mewakili akses anggota dari kamus atau objek: 'variabel["kunci"]'."""
    def __init__(self, sumber, kunci):
        self.sumber = sumber # Node yang diakses (misal: NodePengenal)
        self.kunci = kunci   # Node ekspresi untuk kunci

class NodePilih(NodeAST):
    """Mewakili struktur kontrol 'pilih': 'pilih ekspresi maka ... akhir'."""
    def __init__(self, ekspresi, kasus, kasus_lainnya):
        self.ekspresi = ekspresi
        self.kasus = kasus # list dari NodeKasusPilih
        self.kasus_lainnya = kasus_lainnya # bisa NodeKasusLainnya atau None

class NodeKasusPilih(NodeAST):
    """Mewakili satu cabang 'ketika' dalam blok 'pilih'."""
    def __init__(self, pola, badan):
        self.pola = pola # Node ekspresi untuk pola pencocokan
        self.badan = badan

class NodeKasusLainnya(NodeAST):
    """Mewakili cabang 'lainnya' dalam blok 'pilih'."""
    def __init__(self, badan):
        self.badan = badan
