# morph_engine/absolute_sntx_morph.py
# Changelog:
# - PATCH-023B: Memindahkan semua node spesifik ESTree ke transpiler/ast_js.py.
# - PATCH-023A: Refactor AST dengan menghapus node yatim (ESTree) dan node konteks.
# - PATCH-022A: Menambahkan node AST dari spesifikasi ESTree (JS) untuk fondasi transpiler.
# - PATCH-021B: Refaktor & Implementasi AST Fase 1: Fondasi, literal, variabel, ekspresi.
# - PATCH-020A: Menambahkan NodeAmbil untuk mendukung fungsi input bawaan.
# - PATCH-019B: Menambahkan NodeArray untuk mendukung sintaks array literal.
# - PATCH-016: Menambahkan NodeFungsiDeklarasi, NodePernyataanKembalikan, dan
#              NodeNil untuk user-defined functions.
# - PATCH-010: Menambahkan NodeAssignment untuk membedakan antara deklarasi
#              dan assignment variabel.

# ==============================================================================
# KELAS DASAR (KATEGORI INDUK) - INTI UNIVERSAL AST
# ==============================================================================

class MRPH:
    """Kelas dasar untuk semua node dalam Abstract Syntax Tree."""
    _fields = []

class Core(MRPH):
    """Kelas dasar untuk node level-atas (root) seperti Module."""
    pass

class st(MRPH):
    """Kelas dasar untuk semua jenis statement."""
    pass

class XPrs(MRPH):
    """Kelas dasar untuk semua jenis expression."""
    pass

class Operator(MRPH):
    """Kelas dasar untuk semua token operator."""
    pass

class OperatorBiner(Operator):
    """Kelas dasar untuk operator biner (+, -, *, /)."""
    pass

class OperatorUnary(Operator):
    """Kelas dasar untuk operator unary (-, tidak)."""
    pass

class OperatorBoolean(Operator):
    """Kelas dasar untuk operator boolean (dan, atau)."""
    pass

class OperatorPerbandingan(Operator):
    """Kelas dasar untuk operator perbandingan (==, <, >)."""
    pass

class KonteksEkspresi(MRPH):
    """Kelas dasar untuk konteks ekspresi (Load, Store, Del)."""
    pass

# ==============================================================================
# NODE LEVEL-ATAS (MODUL) - INTI UNIVERSAL AST
# ==============================================================================

class Bagian(Core):
    """Mewakili seluruh program, berisi daftar pernyataan."""
    _fields = ['daftar_pernyataan']
    def __init__(self, daftar_pernyataan):
        self.daftar_pernyataan = daftar_pernyataan

# ==============================================================================
# LITERAL, VARIABEL & STRUKTUR DATA - INTI UNIVERSAL AST
# ==============================================================================

class Konstanta(XPrs):
    """Mewakili nilai literal konstan seperti angka, teks, boolean, atau nil."""
    _fields = ['nilai', 'token']
    def __init__(self, token, nilai):
        self.token = token
        self.nilai = nilai

class Identitas(XPrs):
    """Mewakili sebuah identifier (nama variabel, fungsi, dll.)."""
    _fields = ['token', 'nilai']
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class Daftar(XPrs):
    """Mewakili literal daftar (list): [a, b, c]."""
    _fields = ['elemen']
    def __init__(self, elemen):
        self.elemen = elemen

class Kamus(XPrs):
    """Mewakili literal kamus (dictionary): {"kunci": nilai}."""
    _fields = ['pasangan']
    def __init__(self, pasangan):
        self.pasangan = pasangan

# ==============================================================================
# EKSPRESI - INTI UNIVERSAL AST
# ==============================================================================

class FoxBinary(XPrs):
    """Mewakili operasi biner: kiri op kanan."""
    _fields = ['kiri', 'op', 'kanan']
    def __init__(self, kiri, op, kanan):
        self.kiri = kiri
        self.op = op
        self.kanan = kanan

class FoxUnary(XPrs):
    """Mewakili operasi unary: op operand."""
    _fields = ['op', 'operand']
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class PanggilFungsi(XPrs):
    """Mewakili pemanggilan fungsi: fungsi(arg1, arg2)."""
    _fields = ['nama_fungsi', 'daftar_argumen']
    def __init__(self, nama_fungsi, daftar_argumen):
        self.nama_fungsi = nama_fungsi
        self.daftar_argumen = daftar_argumen

class AksesTitik(XPrs):
    """Mewakili akses member dengan notasi titik: 'objek.properti'."""
    _fields = ['sumber', 'properti']
    def __init__(self, sumber, properti):
        self.sumber = sumber
        self.properti = properti

class Akses(XPrs):
    """Mewakili akses anggota dari kamus atau objek: 'variabel["kunci"]'."""
    _fields = ['sumber', 'kunci']
    def __init__(self, sumber, kunci):
        self.sumber = sumber
        self.kunci = kunci

# ==============================================================================
# PERNYATAAN (STATEMENTS) - INTI UNIVERSAL AST (MORPH)
# ==============================================================================

class DeklarasiVariabel(st):
    """Mewakili deklarasi variabel: 'biar nama = nilai' atau 'tetap nama = nilai'."""
    def __init__(self, jenis_deklarasi, nama_variabel, nilai):
        self.jenis_deklarasi = jenis_deklarasi
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class Assignment(st):
    """Mewakili assignment variabel: 'nama = nilai'."""
    def __init__(self, nama_variabel, nilai):
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class Jika_Maka(st):
    """Mewakili struktur kontrol jika-maka-lain."""
    def __init__(self, kondisi, blok_maka, rantai_lain_jika, blok_lain):
        self.kondisi = kondisi
        self.blok_maka = blok_maka
        self.rantai_lain_jika = rantai_lain_jika
        self.blok_lain = blok_lain

class FungsiDeklarasi(st):
    """Mewakili deklarasi fungsi: 'fungsi nama(p1, p2) maka ... akhir'."""
    def __init__(self, nama_fungsi, parameter, badan):
        self.nama_fungsi = nama_fungsi
        self.parameter = parameter
        self.badan = badan

class PernyataanKembalikan(st):
    """Mewakili pernyataan 'kembalikan nilai'."""
    def __init__(self, nilai_kembalian):
        self.nilai_kembalian = nilai_kembalian

class ambil(XPrs):
    """Mewakili pemanggilan fungsi bawaan 'ambil("prompt")'."""
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node

class Ambil(st):
    """Mewakili pernyataan 'ambil_semua' atau 'ambil_sebagian'."""
    def __init__(self, jenis_impor, path_modul, daftar_nama=None, alias=None):
        self.jenis_impor = jenis_impor
        self.path_modul = path_modul
        self.daftar_nama = daftar_nama
        self.alias = alias

class Pinjam(st):
    """Mewakili pernyataan 'pinjam "path.py" sebagai alias'."""
    def __init__(self, path_modul, alias):
        self.path_modul = path_modul
        self.alias = alias

class Selama(st):
    """Mewakili perulangan 'selama': 'selama kondisi maka ... akhir'."""
    def __init__(self, kondisi, badan, orelse=None):
        self.kondisi = kondisi
        self.badan = badan
        self.orelse = orelse if orelse is not None else []

class Pilih(st):
    """Mewakili struktur kontrol 'pilih': 'pilih ekspresi maka ... akhir'."""
    def __init__(self, ekspresi, kasus, kasus_lainnya):
        self.ekspresi = ekspresi
        self.kasus = kasus
        self.kasus_lainnya = kasus_lainnya

class PilihKasus(st):
    """Mewakili satu cabang 'ketika' dalam blok 'pilih'."""
    def __init__(self, pola, badan):
        self.pola = pola
        self.badan = badan

class KasusLainnya(st):
    """Mewakili cabang 'lainnya' dalam blok 'pilih'."""
    def __init__(self, badan):
        self.badan = badan
