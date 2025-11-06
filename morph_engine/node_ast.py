# morph_engine/node_ast.py
# Changelog:
# - PATCH-023B: Menambahkan node AST C (Fase 2: Ekspresi, Inisialisasi, Atribut).
# - PATCH-023A: Menambahkan node AST C (Fase 1: Tipe, Deklarasi, Pernyataan).
# - PATCH-021B: Refaktor & Implementasi AST Fase 1: Fondasi, literal, variabel, ekspresi.
# - PATCH-020A: Menambahkan NodeAmbil untuk mendukung fungsi input bawaan.
# - PATCH-019B: Menambahkan NodeArray untuk mendukung sintaks array literal.
# - PATCH-016: Menambahkan NodeFungsiDeklarasi, NodePernyataanKembalikan, dan
#              NodeNil untuk user-defined functions.
# - PATCH-010: Menambahkan NodeAssignment untuk membedakan antara deklarasi
#              dan assignment variabel.

# ==============================================================================
# KELAS DASAR (KATEGORI INDUK)
# ==============================================================================

class NodeAST:
    """Kelas dasar untuk semua node dalam Abstract Syntax Tree."""
    _fields = []

class NodeModul(NodeAST):
    """Kelas dasar untuk node level-atas (root) seperti Module."""
    pass

class NodePernyataan(NodeAST):
    """Kelas dasar untuk semua jenis statement."""
    pass

class NodeEkspresi(NodeAST):
    """Kelas dasar untuk semua jenis expression."""
    pass

class NodeOperator(NodeAST):
    """Kelas dasar untuk semua token operator."""
    pass

class NodeOperatorBiner(NodeOperator):
    """Kelas dasar untuk operator biner (+, -, *, /)."""
    pass

class NodeOperatorUnary(NodeOperator):
    """Kelas dasar untuk operator unary (-, tidak)."""
    pass

class NodeOperatorBoolean(NodeOperator):
    """Kelas dasar untuk operator boolean (dan, atau)."""
    pass

class NodeOperatorPerbandingan(NodeOperator):
    """Kelas dasar untuk operator perbandingan (==, <, >)."""
    pass

class NodeKonteksEkspresi(NodeAST):
    """Kelas dasar untuk konteks ekspresi (Load, Store, Del)."""
    pass

# ==============================================================================
# NODE LEVEL-ATAS (MODUL)
# ==============================================================================

class NodeProgram(NodeModul):
    """Mewakili seluruh program, berisi daftar pernyataan."""
    _fields = ['daftar_pernyataan']
    def __init__(self, daftar_pernyataan):
        self.daftar_pernyataan = daftar_pernyataan

# ==============================================================================
# LITERAL, VARIABEL & STRUKTUR DATA
# ==============================================================================

class NodeKonstanta(NodeEkspresi):
    """Mewakili nilai literal konstan seperti angka, teks, boolean, atau nil."""
    _fields = ['nilai', 'token']
    def __init__(self, token, nilai):
        self.token = token
        self.nilai = nilai

class NodeNama(NodeEkspresi):
    """Mewakili sebuah identifier (nama variabel, fungsi, dll.)."""
    _fields = ['token', 'nilai']
    def __init__(self, token):
        self.token = token
        self.nilai = token.nilai

class NodeDaftar(NodeEkspresi):
    """Mewakili literal daftar (list): [a, b, c]."""
    _fields = ['elemen']
    def __init__(self, elemen):
        self.elemen = elemen

class NodeKamus(NodeEkspresi):
    """Mewakili literal kamus (dictionary): {"kunci": nilai}."""
    _fields = ['pasangan']
    def __init__(self, pasangan):
        self.pasangan = pasangan

# ==============================================================================
# KONTEKS EKSPRESI
# ==============================================================================

class NodeMuat(NodeKonteksEkspresi):
    """Menandakan variabel sedang dibaca/dimuat."""
    pass

class NodeSimpan(NodeKonteksEkspresi):
    """Menandakan variabel sedang ditulis/disimpan."""
    pass

class NodeHapus(NodeKonteksEkspresi):
    """Menandakan variabel sedang dihapus."""
    pass

# ==============================================================================
# EKSPRESI
# ==============================================================================

class NodeOperasiBiner(NodeEkspresi):
    """Mewakili operasi biner: kiri op kanan."""
    _fields = ['kiri', 'op', 'kanan']
    def __init__(self, kiri, op, kanan):
        self.kiri = kiri
        self.op = op
        self.kanan = kanan

class NodeOperasiUnary(NodeEkspresi):
    """Mewakili operasi unary: op operand."""
    _fields = ['op', 'operand']
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class NodePanggilFungsi(NodeEkspresi):
    """Mewakili pemanggilan fungsi: fungsi(arg1, arg2)."""
    _fields = ['nama_fungsi', 'daftar_argumen']
    def __init__(self, nama_fungsi, daftar_argumen):
        self.nama_fungsi = nama_fungsi
        self.daftar_argumen = daftar_argumen

class NodeAksesTitik(NodeEkspresi):
    """Mewakili akses member dengan notasi titik: 'objek.properti'."""
    _fields = ['sumber', 'properti']
    def __init__(self, sumber, properti):
        self.sumber = sumber
        self.properti = properti

class NodeAksesMember(NodeEkspresi):
    """Mewakili akses anggota dari kamus atau objek: 'variabel["kunci"]'."""
    _fields = ['sumber', 'kunci']
    def __init__(self, sumber, kunci):
        self.sumber = sumber
        self.kunci = kunci

# ==============================================================================
# PERNYATAAN (STATEMENTS) - DASAR
# ==============================================================================
# Node-node ini dipertahankan karena sudah digunakan secara luas
# dan termasuk dalam cakupan dasar.

class NodeDeklarasiVariabel(NodePernyataan):
    """Mewakili deklarasi variabel: 'biar nama = nilai' atau 'tetap nama = nilai'."""
    def __init__(self, jenis_deklarasi, nama_variabel, nilai):
        self.jenis_deklarasi = jenis_deklarasi
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class NodeAssignment(NodePernyataan):
    """Mewakili assignment variabel: 'nama = nilai'."""
    def __init__(self, nama_variabel, nilai):
        self.nama_variabel = nama_variabel
        self.nilai = nilai

class NodeJikaMaka(NodePernyataan):
    """Mewakili struktur kontrol jika-maka-lain."""
    def __init__(self, kondisi, blok_maka, rantai_lain_jika, blok_lain):
        self.kondisi = kondisi
        self.blok_maka = blok_maka
        self.rantai_lain_jika = rantai_lain_jika
        self.blok_lain = blok_lain

class NodeFungsiDeklarasi(NodePernyataan):
    """Mewakili deklarasi fungsi: 'fungsi nama(p1, p2) maka ... akhir'."""
    def __init__(self, nama_fungsi, parameter, badan):
        self.nama_fungsi = nama_fungsi
        self.parameter = parameter
        self.badan = badan

class NodePernyataanKembalikan(NodePernyataan):
    """Mewakili pernyataan 'kembalikan nilai'."""
    def __init__(self, nilai_kembalian):
        self.nilai_kembalian = nilai_kembalian

class NodeAmbil(NodeEkspresi):
    """Mewakili pemanggilan fungsi bawaan 'ambil("prompt")'."""
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node

class NodeImpor(NodePernyataan):
    """Mewakili pernyataan 'ambil_semua' atau 'ambil_sebagian'."""
    def __init__(self, jenis_impor, path_modul, daftar_nama=None, alias=None):
        self.jenis_impor = jenis_impor
        self.path_modul = path_modul
        self.daftar_nama = daftar_nama
        self.alias = alias

class NodePinjam(NodePernyataan):
    """Mewakili pernyataan 'pinjam "path.py" sebagai alias'."""
    def __init__(self, path_modul, alias):
        self.path_modul = path_modul
        self.alias = alias

class NodeSelama(NodePernyataan):
    """Mewakili perulangan 'selama': 'selama kondisi maka ... akhir'."""
    def __init__(self, kondisi, badan):
        self.kondisi = kondisi
        self.badan = badan

class NodePilih(NodePernyataan):
    """Mewakili struktur kontrol 'pilih': 'pilih ekspresi maka ... akhir'."""
    def __init__(self, ekspresi, kasus, kasus_lainnya):
        self.ekspresi = ekspresi
        self.kasus = kasus
        self.kasus_lainnya = kasus_lainnya

class NodeKasusPilih(NodePernyataan):
    """Mewakili satu cabang 'ketika' dalam blok 'pilih'."""
    def __init__(self, pola, badan):
        self.pola = pola
        self.badan = badan

class NodeKasusLainnya(NodePernyataan):
    """Mewakili cabang 'lainnya' dalam blok 'pilih'."""
    def __init__(self, badan):
        self.badan = badan

# ==============================================================================
# ==============================================================================
# ==                                                                          ==
# ==                 AST UNTUK BAHASA C (FONDASI TRANSPILER C)                ==
# ==                                                                          ==
# ==============================================================================
# ==============================================================================

# ==============================================================================
# C: UNIT TRANSLASI & PREPROCESSOR
# ==============================================================================

class NodeUnitTranslasiC(NodeModul):
    """Mewakili seluruh unit translasi (file sumber setelah preprocessing)."""
    _fields = ['deklarasi']
    def __init__(self, deklarasi):
        self.deklarasi = deklarasi

class NodeArahanPreprocessorC(NodeAST):
    """Kelas dasar untuk semua arahan preprocessor."""
    pass

class NodePreprocessorIncludeC(NodeArahanPreprocessorC):
    """Mewakili arahan '#include <...>' atau '#include "..."'."""
    _fields = ['path', 'jenis_kurung']
    def __init__(self, path, jenis_kurung):
        self.path = path  # string
        self.jenis_kurung = jenis_kurung  # 'angle' atau 'quote'

class NodePreprocessorDefineC(NodeArahanPreprocessorC):
    """Mewakili arahan '#define NAMA ...'."""
    _fields = ['nama', 'parameter', 'isi']
    def __init__(self, nama, parameter, isi):
        self.nama = nama
        self.parameter = parameter  # list of string atau None
        self.isi = isi  # list of token

class NodePreprocessorUndefC(NodeArahanPreprocessorC):
    """Mewakili arahan '#undef NAMA'."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama

class NodePreprocessorIfC(NodeArahanPreprocessorC):
    """Mewakili arahan '#if', '#ifdef', '#ifndef'."""
    _fields = ['jenis', 'kondisi', 'blok_then', 'blok_elif', 'blok_else']
    def __init__(self, jenis, kondisi, blok_then, blok_elif=None, blok_else=None):
        self.jenis = jenis # 'if', 'ifdef', 'ifndef'
        self.kondisi = kondisi
        self.blok_then = blok_then
        self.blok_elif = blok_elif
        self.blok_else = blok_else

class NodePreprocessorElifC(NodeArahanPreprocessorC):
    """Mewakili arahan '#elif'."""
    _fields = ['kondisi', 'blok']
    def __init__(self, kondisi, blok):
        self.kondisi = kondisi
        self.blok = blok

class NodePreprocessorElseC(NodeArahanPreprocessorC):
    """Mewakili arahan '#else'."""
    _fields = ['blok']
    def __init__(self, blok):
        self.blok = blok

class NodePreprocessorEndifC(NodeArahanPreprocessorC):
    """Mewakili arahan '#endif'."""
    pass

class NodePreprocessorPragmaC(NodeArahanPreprocessorC):
    """Mewakili arahan '#pragma ...'."""
    _fields = ['isi']
    def __init__(self, isi):
        self.isi = isi

class NodePreprocessorErrorC(NodeArahanPreprocessorC):
    """Mewakili arahan '#error ...'."""
    _fields = ['pesan']
    def __init__(self, pesan):
        self.pesan = pesan

# ==============================================================================
# C: TIPE (TYPES)
# ==============================================================================

class NodeTipeC(NodeAST):
    """Kelas dasar untuk semua spesifier tipe C."""
    pass

class NodeTipeBawaanC(NodeTipeC):
    """Mewakili tipe bawaan (int, char, float, dll)."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama  # e.g., "int", "void", "long double"

class NodeTipeBitIntC(NodeTipeC):
    """Mewakili tipe _BitInt(N) dari C23."""
    _fields = ['lebar_bit', 'is_signed']
    def __init__(self, lebar_bit, is_signed):
        self.lebar_bit = lebar_bit
        self.is_signed = is_signed

class NodeTipeNullptrC(NodeTipeC):
    """Mewakili tipe nullptr_t dari C23."""
    pass

class NodeTipeDariC(NodeTipeC):
    """Mewakili tipe typeof(...) dari C23."""
    _fields = ['operand']
    def __init__(self, operand):
        self.operand = operand # Bisa NodeEkspresi atau NodeTipeC

class NodeTipeAtomikC(NodeTipeC):
    """Mewakili tipe _Atomic(T)."""
    _fields = ['tipe_dasar']
    def __init__(self, tipe_dasar):
        self.tipe_dasar = tipe_dasar

class NodeTipeKualifikasiC(NodeTipeC):
    """Mewakili tipe dengan kualifikasi (const, volatile, restrict)."""
    _fields = ['tipe_dasar', 'kualifikasi']
    def __init__(self, tipe_dasar, kualifikasi):
        self.tipe_dasar = tipe_dasar
        self.kualifikasi = kualifikasi # list of string

class NodeSpesifierAlignasC(NodeAST):
    """Mewakili spesifier alignas(...) dari C23."""
    _fields = ['operand']
    def __init__(self, operand):
        self.operand = operand # Bisa NodeEkspresi atau NodeTipeC

class NodeTipePointerC(NodeTipeC):
    """Mewakili tipe pointer."""
    _fields = ['tipe_tujuan', 'kualifikasi']
    def __init__(self, tipe_tujuan, kualifikasi=None):
        self.tipe_tujuan = tipe_tujuan
        self.kualifikasi = kualifikasi

class NodeTipeArrayC(NodeTipeC):
    """Mewakili tipe array."""
    _fields = ['tipe_elemen', 'ukuran', 'is_vla']
    def __init__(self, tipe_elemen, ukuran=None, is_vla=False):
        self.tipe_elemen = tipe_elemen
        self.ukuran = ukuran # NodeEkspresi atau None
        self.is_vla = is_vla

class NodeTipeFungsiC(NodeTipeC):
    """Mewakili tipe fungsi."""
    _fields = ['tipe_kembalian', 'tipe_parameter', 'is_var_arg']
    def __init__(self, tipe_kembalian, tipe_parameter, is_var_arg=False):
        self.tipe_kembalian = tipe_kembalian
        self.tipe_parameter = tipe_parameter
        self.is_var_arg = is_var_arg

class NodeTipeStructC(NodeTipeC):
    """Mewakili tipe struct."""
    _fields = ['nama_tag', 'deklarasi_field']
    def __init__(self, nama_tag=None, deklarasi_field=None):
        self.nama_tag = nama_tag
        self.deklarasi_field = deklarasi_field

class NodeTipeUnionC(NodeTipeC):
    """Mewakili tipe union."""
    _fields = ['nama_tag', 'deklarasi_field']
    def __init__(self, nama_tag=None, deklarasi_field=None):
        self.nama_tag = nama_tag
        self.deklarasi_field = deklarasi_field

class NodeTipeEnumC(NodeTipeC):
    """Mewakili tipe enum."""
    _fields = ['nama_tag', 'enumerators', 'tipe_dasar']
    def __init__(self, nama_tag=None, enumerators=None, tipe_dasar=None):
        self.nama_tag = nama_tag
        self.enumerators = enumerators
        self.tipe_dasar = tipe_dasar # C23 feature

class NodeTipeTypedefC(NodeTipeC):
    """Mewakili nama tipe yang didefinisikan oleh typedef."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama

# ==============================================================================
# C: DEKLARASI (DECLARATIONS)
# ==============================================================================

class NodeDeklarasiC(NodePernyataan):
    """Mewakili sebuah deklarasi di C (variabel, fungsi, tipe)."""
    _fields = ['spesifier', 'init_declarators', 'atribut']
    def __init__(self, spesifier, init_declarators=None, atribut=None):
        self.spesifier = spesifier # List NodeSpesifier...
        self.init_declarators = init_declarators # List NodeInitDeclaratorC
        self.atribut = atribut

class NodeDefinisiFungsiC(NodeDeklarasiC):
    """Mewakili definisi sebuah fungsi."""
    _fields = ['spesifier', 'deklarator', 'badan', 'atribut']
    def __init__(self, spesifier, deklarator, badan, atribut=None):
        self.spesifier = spesifier
        self.deklarator = deklarator
        self.badan = badan
        self.atribut = atribut

class NodeDeklarasiTypedefC(NodeDeklarasiC):
    """Mewakili sebuah deklarasi typedef."""
    pass

class NodeDeklarasiAssertStatisC(NodeDeklarasiC):
    """Mewakili deklarasi _Static_assert."""
    _fields = ['kondisi', 'pesan']
    def __init__(self, kondisi, pesan):
        self.kondisi = kondisi
        self.pesan = pesan

class NodeDeklaratorC(NodeAST):
    """Mewakili seorang deklarator, yang mengikat nama ke sebuah tipe."""
    _fields = ['pointer', 'deklarator_langsung']
    def __init__(self, pointer=None, deklarator_langsung=None):
        self.pointer = pointer # NodeTipePointerC atau None
        self.deklarator_langsung = deklarator_langsung # Node...

class NodeInitDeclaratorC(NodeAST):
    """Sepasang deklarator dan inisialisasi opsional."""
    _fields = ['deklarator', 'inisialisasi']
    def __init__(self, deklarator, inisialisasi=None):
        self.deklarator = deklarator
        self.inisialisasi = inisialisasi

class NodeDeklarasiFieldC(NodeDeklarasiC):
    """Mewakili deklarasi field di dalam struct atau union."""
    _fields = ['spesifier', 'deklarator_list', 'lebar_bit']
    def __init__(self, spesifier, deklarator_list, lebar_bit=None):
        self.spesifier = spesifier
        self.deklarator_list = deklarator_list
        self.lebar_bit = lebar_bit # Untuk bit-fields

class NodeEnumeratorC(NodeAST):
    """Mewakili satu item dalam sebuah enum."""
    _fields = ['nama', 'nilai']
    def __init__(self, nama, nilai=None):
        self.nama = nama
        self.nilai = nilai

class NodeDeklarasiParameterC(NodeDeklarasiC):
    """Mewakili deklarasi parameter dalam sebuah fungsi."""
    _fields = ['spesifier', 'deklarator']
    def __init__(self, spesifier, deklarator=None):
        self.spesifier = spesifier
        self.deklarator = deklarator

# ==============================================================================
# C: PERNYATAAN (STATEMENTS)
# ==============================================================================

class NodePernyataanBlokC(NodePernyataan):
    """Mewakili blok pernyataan di C, yang bisa berisi deklarasi dan pernyataan."""
    _fields = ['item']
    def __init__(self, item):
        self.item = item # Campuran NodeDeklarasiC dan NodePernyataan

class NodePernyataanForC(NodePernyataan):
    """Mewakili perulangan 'for' gaya C."""
    _fields = ['init', 'kondisi', 'iterasi', 'badan']
    def __init__(self, init, kondisi, iterasi, badan):
        self.init = init # Bisa NodeDeklarasiC atau NodeEkspresi
        self.kondisi = kondisi # NodeEkspresi
        self.iterasi = iterasi # NodeEkspresi
        self.badan = badan

class NodePernyataanGotoC(NodePernyataan):
    """Mewakili pernyataan 'goto'."""
    _fields = ['label']
    def __init__(self, label):
        self.label = label # NodeNama

class NodePernyataanBerlabelC(NodePernyataan):
    """Mewakili pernyataan berlabel (untuk goto)."""
    _fields = ['label', 'pernyataan']
    def __init__(self, label, pernyataan):
        self.label = label
        self.pernyataan = pernyataan

class NodeKasusSwitchC(NodeAST):
    """Mewakili satu kasus 'case' di C, bisa dengan rentang (ekstensi GNU)."""
    _fields = ['nilai_awal', 'nilai_akhir', 'badan']
    def __init__(self, nilai_awal, nilai_akhir=None, badan=None):
        self.nilai_awal = nilai_awal # NodeEkspresi
        self.nilai_akhir = nilai_akhir # NodeEkspresi atau None
        self.badan = badan

class NodeKasusDefaultC(NodeAST):
    """Mewakili kasus 'default' di C."""
    _fields = ['badan']
    def __init__(self, badan):
        self.badan = badan

# ==============================================================================
# C: EKSPRESI (EXPRESSIONS) - LITERAL & PRIMER
# ==============================================================================

class NodeEkspresiC(NodeEkspresi):
    """Kelas dasar untuk semua ekspresi C."""
    pass

class NodeLiteralIntegerC(NodeEkspresiC):
    """Mewakili literal integer di C, termasuk sufiksnya."""
    _fields = ['nilai', 'sufiks']
    def __init__(self, nilai, sufiks=None):
        self.nilai = nilai
        self.sufiks = sufiks

class NodeLiteralFloatingC(NodeEkspresiC):
    """Mewakili literal floating-point di C."""
    _fields = ['nilai', 'sufiks']
    def __init__(self, nilai, sufiks=None):
        self.nilai = nilai
        self.sufiks = sufiks

class NodeLiteralKarakterC(NodeEkspresiC):
    """Mewakili literal karakter di C, termasuk prefiksnya."""
    _fields = ['nilai', 'prefiks']
    def __init__(self, nilai, prefiks=None):
        self.nilai = nilai
        self.prefiks = prefiks

class NodeLiteralStringC(NodeEkspresiC):
    """Mewakili literal string di C, termasuk gabungan string."""
    _fields = ['nilai', 'prefiks']
    def __init__(self, nilai, prefiks=None):
        self.nilai = nilai # Bisa berupa list jika ada gabungan
        self.prefiks = prefiks

class NodeLiteralNullptrC(NodeEkspresiC):
    """Mewakili literal nullptr dari C23."""
    pass

class NodeEkspresiIdentifierC(NodeEkspresiC):
    """Mewakili penggunaan sebuah identifier dalam ekspresi."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama

class NodeEkspresiDalamKurungC(NodeEkspresiC):
    """Mewakili ekspresi yang dikelompokkan dalam tanda kurung."""
    _fields = ['ekspresi']
    def __init__(self, ekspresi):
        self.ekspresi = ekspresi

class NodeEkspresiSeleksiGenerikC(NodeEkspresiC):
    """Mewakili ekspresi _Generic."""
    _fields = ['ekspresi_kontrol', 'asosiasi', 'default']
    def __init__(self, ekspresi_kontrol, asosiasi, default=None):
        self.ekspresi_kontrol = ekspresi_kontrol
        self.asosiasi = asosiasi # List of NodeAsosiasiGenerikC
        self.default = default

class NodeAsosiasiGenerikC(NodeAST):
    """Satu asosiasi dalam _Generic (tipe: ekspresi)."""
    _fields = ['tipe', 'ekspresi']
    def __init__(self, tipe, ekspresi):
        self.tipe = tipe
        self.ekspresi = ekspresi

class NodeLiteralKompositC(NodeEkspresiC):
    """Mewakili literal komposit: (tipe){...}."""
    _fields = ['tipe', 'inisialisasi']
    def __init__(self, tipe, inisialisasi):
        self.tipe = tipe
        self.inisialisasi = inisialisasi

class NodeEkspresiSizeofC(NodeEkspresiC):
    """Mewakili ekspresi sizeof."""
    _fields = ['operand']
    def __init__(self, operand):
        self.operand = operand # Bisa NodeTipeC atau NodeEkspresiC

class NodeEkspresiAlignofC(NodeEkspresiC):
    """Mewakili ekspresi alignof (C23)."""
    _fields = ['operand']
    def __init__(self, operand):
        self.operand = operand # Bisa NodeTipeC

# ==============================================================================
# C: EKSPRESI (EXPRESSIONS) - KOMPLEKS
# ==============================================================================

class NodeEkspresiUnaryC(NodeEkspresiC):
    """Mewakili operasi unary C (+, -, ~, !, *, &)."""
    _fields = ['operator', 'operand']
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class NodeEkspresiPostfixC(NodeEkspresiC):
    """Mewakili operasi postfix (++, --)."""
    _fields = ['operator', 'operand']
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class NodeEkspresiBinerC(NodeEkspresiC):
    """Mewakili operasi biner C."""
    _fields = ['kiri', 'operator', 'kanan']
    def __init__(self, kiri, operator, kanan):
        self.kiri = kiri
        self.operator = operator
        self.kanan = kanan

class NodeEkspresiCastC(NodeEkspresiC):
    """Mewakili cast eksplisit: (tipe)ekspresi."""
    _fields = ['tipe_tujuan', 'ekspresi']
    def __init__(self, tipe_tujuan, ekspresi):
        self.tipe_tujuan = tipe_tujuan
        self.ekspresi = ekspresi

class NodeEkspresiKondisionalC(NodeEkspresiC):
    """Mewakili ekspresi kondisional (ternary)."""
    _fields = ['kondisi', 'ekspresi_then', 'ekspresi_else']
    def __init__(self, kondisi, ekspresi_then, ekspresi_else):
        self.kondisi = kondisi
        self.ekspresi_then = ekspresi_then
        self.ekspresi_else = ekspresi_else

class NodeEkspresiAssignmentC(NodeEkspresiC):
    """Mewakili operasi assignment C (=, +=, -=, dll)."""
    _fields = ['kiri', 'operator', 'kanan']
    def __init__(self, kiri, operator, kanan):
        self.kiri = kiri
        self.operator = operator
        self.kanan = kanan

class NodeEkspresiPanggilanFungsiC(NodeEkspresiC):
    """Mewakili pemanggilan fungsi di C."""
    _fields = ['callee', 'argumen']
    def __init__(self, callee, argumen):
        self.callee = callee
        self.argumen = argumen

class NodeEkspresiAksesMemberC(NodeEkspresiC):
    """Mewakili akses member struct/union (. atau ->)."""
    _fields = ['basis', 'operator', 'member']
    def __init__(self, basis, operator, member):
        self.basis = basis
        self.operator = operator # '.' atau '->'
        self.member = member

# ==============================================================================
# C: INISIALISASI & DESIGNATOR
# ==============================================================================

class NodeInisialisasiC(NodeAST):
    """Kelas dasar untuk inisialisasi."""
    pass

class NodeInisialisasiEkspresiC(NodeInisialisasiC):
    """Inisialisasi dengan ekspresi tunggal."""
    _fields = ['ekspresi']
    def __init__(self, ekspresi):
        self.ekspresi = ekspresi

class NodeInisialisasiDaftarC(NodeInisialisasiC):
    """Inisialisasi dengan daftar inisialisasi: {...}."""
    _fields = ['item']
    def __init__(self, item):
        self.item = item # List of NodeInisialisasi...

class NodeInisialisasiTerdesainC(NodeAST):
    """Mewakili satu item dalam inisialisasi terdesain."""
    _fields = ['designator', 'nilai']
    def __init__(self, designator, nilai):
        self.designator = designator # List of NodeDesignatorC
        self.nilai = nilai

class NodeDesignatorC(NodeAST):
    """Mewakili satu designator (.field atau [index])."""
    _fields = ['jenis', 'nilai']
    def __init__(self, jenis, nilai):
        self.jenis = jenis # 'field' atau 'index'
        self.nilai = nilai

# ==============================================================================
# C: ATRIBUT & SPESIFIER
# ==============================================================================

class NodeAtributC(NodeAST):
    """Mewakili atribut C23 [[...]]."""
    _fields = ['nama', 'argumen']
    def __init__(self, nama, argumen=None):
        self.nama = nama
        self.argumen = argumen

class NodeSpesifierPenyimpananC(NodeAST):
    """Mewakili spesifier kelas penyimpanan (extern, static, dll)."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama # 'extern', 'static', 'typedef', 'thread_local'

class NodeDeklarasiAutoInferC(NodeDeklarasiC):
    """Mewakili deklarasi dengan 'auto' untuk inferensi tipe (C23)."""
    _fields = ['nama', 'inisialisasi']
    def __init__(self, nama, inisialisasi):
        self.nama = nama
        self.inisialisasi = inisialisasi
