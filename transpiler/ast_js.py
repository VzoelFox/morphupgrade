# transpiler/ast_js.py
# Berisi definisi Abstract Syntax Tree (AST) spesifik untuk JavaScript (ESTree).

from morph_engine.node_ast import NodeAST, NodePernyataan, NodeEkspresi

# ==============================================================================
# PERNYATAAN (STATEMENTS) - LANJUTAN (DARI ESTREE)
# ==============================================================================

class NodePernyataanEkspresi(NodePernyataan):
    """Mewakili sebuah ekspresi yang digunakan sebagai pernyataan."""
    _fields = ['ekspresi']
    def __init__(self, ekspresi):
        self.ekspresi = ekspresi

# ==============================================================================
# POLA (PATTERNS) - UNTUK DESTRUKTURISASI
# ==============================================================================

class NodePola(NodeAST):
    """Kelas dasar untuk semua jenis pattern."""
    pass

class NodePolaArray(NodePola):
    """Mewakili pola destrukturisasi array: [a, b]."""
    _fields = ['elemen']
    def __init__(self, elemen):
        self.elemen = elemen

class NodePolaObjek(NodePola):
    """Mewakili pola destrukturisasi objek: {a, b: c}."""
    _fields = ['properti']
    def __init__(self, properti):
        self.properti = properti

class NodePolaPenugasan(NodePola):
    """Mewakili nilai default dalam pola: [a=1]."""
    _fields = ['kiri', 'kanan']
    def __init__(self, kiri, kanan):
        self.kiri = kiri
        self.kanan = kanan

class NodeElemenSisa(NodePola):
    """Mewakili elemen sisa dalam destrukturisasi: [...sisa]."""
    _fields = ['argumen']
    def __init__(self, argumen):
        self.argumen = argumen

# ==============================================================================
# KELAS (CLASSES)
# ==============================================================================

class NodeDeklarasiKelas(NodePernyataan):
    """Mewakili deklarasi kelas."""
    _fields = ['id', 'super_kelas', 'badan']
    def __init__(self, id, super_kelas, badan):
        self.id = id
        self.super_kelas = super_kelas
        self.badan = badan

class NodeEkspresiKelas(NodeDeklarasiKelas):
    """Mewakili ekspresi kelas."""
    pass

class NodeBadanKelas(NodeAST):
    """Mewakili badan dari sebuah kelas, berisi daftar definisi."""
    _fields = ['badan']
    def __init__(self, badan):
        self.badan = badan

class NodeDefinisiMetode(NodeAST):
    """Mewakili definisi metode di dalam kelas."""
    _fields = ['kunci', 'nilai', 'jenis', 'static', 'computed']
    def __init__(self, kunci, nilai, jenis, static=False, computed=False):
        self.kunci = kunci
        self.nilai = nilai  # NodeEkspresiFungsi
        self.jenis = jenis  # 'constructor', 'method', 'get', 'set'
        self.static = static
        self.computed = computed

class NodeDefinisiProperti(NodeAST):
    """Mewakili field/properti kelas."""
    _fields = ['kunci', 'nilai', 'static', 'computed']
    def __init__(self, kunci, nilai=None, static=False, computed=False):
        self.kunci = kunci
        self.nilai = nilai
        self.static = static
        self.computed = computed

class NodeIdentifierPrivat(NodeAST):
    """Mewakili identifier privat dalam kelas: #nama."""
    _fields = ['nama']
    def __init__(self, nama):
        self.nama = nama

class NodeBlokStatis(NodeAST):
    """Mewakili blok inisialisasi statis di dalam kelas."""
    _fields = ['badan']
    def __init__(self, badan):
        self.badan = badan

class NodeSuper(NodeEkspresi):
    """Mewakili kata kunci 'super'."""
    pass

# ==============================================================================
# PROPERTI OBJEK
# ==============================================================================

class NodeProperti(NodeAST):
    """Mewakili properti dalam literal objek."""
    _fields = ['kunci', 'nilai', 'jenis', 'metode', 'shorthand', 'computed']
    def __init__(self, kunci, nilai, jenis='init', metode=False, shorthand=False, computed=False):
        self.kunci = kunci
        self.nilai = nilai
        self.jenis = jenis  # 'init', 'get', 'set'
        self.metode = metode
        self.shorthand = shorthand
        self.computed = computed

class NodeElemenSpread(NodeEkspresi):
    """Mewakili spread syntax: {...objek} atau [...array]."""
    _fields = ['argumen']
    def __init__(self, argumen):
        self.argumen = argumen

# ==============================================================================
# MODUL (ESM)
# ==============================================================================

class NodeDeklarasiImpor(NodePernyataan):
    """Mewakili pernyataan 'import'."""
    _fields = ['specifiers', 'sumber']
    def __init__(self, specifiers, sumber):
        self.specifiers = specifiers
        self.sumber = sumber

class NodeSpesifierImpor(NodeAST):
    """Mewakili satu item dalam 'import {item}'."""
    _fields = ['imported', 'local']
    def __init__(self, imported, local):
        self.imported = imported
        self.local = local

class NodeSpesifierImporDefault(NodeAST):
    """Mewakili 'import item'."""
    _fields = ['local']
    def __init__(self, local):
        self.local = local

class NodeSpesifierImporNamespace(NodeAST):
    """Mewakili 'import * as item'."""
    _fields = ['local']
    def __init__(self, local):
        self.local = local

class NodeDeklarasiEksporBernama(NodePernyataan):
    """Mewakili 'export { a, b }' atau 'export const a = 1'."""
    _fields = ['deklarasi', 'specifiers', 'sumber']
    def __init__(self, deklarasi=None, specifiers=None, sumber=None):
        self.deklarasi = deklarasi
        self.specifiers = specifiers
        self.sumber = sumber

class NodeDeklarasiEksporDefault(NodePernyataan):
    """Mewakili 'export default ...'."""
    _fields = ['deklarasi']
    def __init__(self, deklarasi):
        self.deklarasi = deklarasi

class NodeDeklarasiEksporSemua(NodePernyataan):
    """Mewakili 'export * from "modul"'."""
    _fields = ['sumber', 'exported']
    def __init__(self, sumber, exported=None):
        self.sumber = sumber
        self.exported = exported

class NodeSpesifierEkspor(NodeAST):
    """Mewakili satu item dalam 'export {item}'."""
    _fields = ['local', 'exported']
    def __init__(self, local, exported):
        self.local = local
        self.exported = exported

class NodeAtributImpor(NodeAST):
    """Mewakili atribut impor: import ... with { type: 'json' }."""
    _fields = ['kunci', 'nilai']
    def __init__(self, kunci, nilai):
        self.kunci = kunci
        self.nilai = nilai

class NodePernyataanBlok(NodePernyataan):
    """Mewakili sebuah blok kode: { pernyataan1; pernyataan2; }."""
    _fields = ['badan']
    def __init__(self, badan):
        self.badan = badan

class NodePernyataanKosong(NodePernyataan):
    """Mewakili pernyataan kosong (titik koma)."""
    pass

class NodePernyataanDebugger(NodePernyataan):
    """Mewakili pernyataan debugger."""
    pass

class NodePernyataanWith(NodePernyataan):
    """Mewakili pernyataan 'with' (tidak direkomendasikan)."""
    _fields = ['objek', 'badan']
    def __init__(self, objek, badan):
        self.objek = objek
        self.badan = badan

class NodePernyataanBerlabel(NodePernyataan):
    """Mewakili pernyataan berlabel: 'label: pernyataan'."""
    _fields = ['label', 'badan']
    def __init__(self, label, badan):
        self.label = label
        self.badan = badan

class NodePernyataanHenti(NodePernyataan):
    """Mewakili pernyataan 'break'."""
    _fields = ['label']
    def __init__(self, label=None):
        self.label = label

class NodePernyataanLanjut(NodePernyataan):
    """Mewakili pernyataan 'continue'."""
    _fields = ['label']
    def __init__(self, label=None):
        self.label = label

class NodePernyataanSwitch(NodePernyataan):
    """Mewakili pernyataan 'switch'."""
    _fields = ['diskriminan', 'kasus']
    def __init__(self, diskriminan, kasus):
        self.diskriminan = diskriminan
        self.kasus = kasus

class NodeKasusSwitch(NodeAST):
    """Mewakili satu kasus 'case' atau 'default' dalam 'switch'."""
    _fields = ['tes', 'konsekuen']
    def __init__(self, tes, konsekuen):
        self.tes = tes  # None untuk 'default'
        self.konsekuen = konsekuen

class NodePernyataanLempar(NodePernyataan):
    """Mewakili pernyataan 'throw'."""
    _fields = ['argumen']
    def __init__(self, argumen):
        self.argumen = argumen

class NodePernyataanCoba(NodePernyataan):
    """Mewakili pernyataan 'try-catch-finally'."""
    _fields = ['blok', 'penangan', 'finalizer']
    def __init__(self, blok, penangan=None, finalizer=None):
        self.blok = blok
        self.penangan = penangan
        self.finalizer = finalizer

class NodeKlausulTangkap(NodeAST):
    """Mewakili blok 'catch' dalam pernyataan 'try'."""
    _fields = ['parameter', 'badan']
    def __init__(self, parameter, badan):
        self.parameter = parameter
        self.badan = badan

class NodePernyataanLakukanSelama(NodePernyataan):
    """Mewakili perulangan 'do-while'."""
    _fields = ['badan', 'tes']
    def __init__(self, badan, tes):
        self.badan = badan
        self.tes = tes

class NodePernyataanFor(NodePernyataan):
    """Mewakili perulangan 'for' gaya C."""
    _fields = ['init', 'tes', 'update', 'badan']
    def __init__(self, init, tes, update, badan):
        self.init = init
        self.tes = tes
        self.update = update
        self.badan = badan

class NodePernyataanForIn(NodePernyataan):
    """Mewakili perulangan 'for-in'."""
    _fields = ['kiri', 'kanan', 'badan']
    def __init__(self, kiri, kanan, badan):
        self.kiri = kiri
        self.kanan = kanan
        self.badan = badan

class NodePernyataanForOf(NodePernyataanForIn):
    """Mewakili perulangan 'for-of'."""
    # Mewarisi struktur dari ForIn, tetapi memiliki penanganan berbeda di interpreter
    pass

# ==============================================================================
# EKSPRESI (EXPRESSIONS) - LANJUTAN (DARI ESTREE)
# ==============================================================================

class NodeEkspresiIni(NodeEkspresi):
    """Mewakili kata kunci 'this'."""
    pass

class NodeEkspresiFungsi(NodeEkspresi):
    """Mewakili sebuah ekspresi fungsi (anonim atau bernama)."""
    _fields = ['id', 'parameter', 'badan']
    def __init__(self, id, parameter, badan):
        self.id = id  # Bisa NodeNama atau None
        self.parameter = parameter
        self.badan = badan

class NodeEkspresiFungsiPanah(NodeEkspresiFungsi):
    """Mewakili ekspresi fungsi panah: (a, b) => a + b."""
    # Strukturnya mirip dengan NodeEkspresiFungsi
    pass

class NodeEkspresiYield(NodeEkspresi):
    """Mewakili ekspresi 'yield' dalam generator."""
    _fields = ['argumen', 'delegate']
    def __init__(self, argumen=None, delegate=False):
        self.argumen = argumen
        self.delegate = delegate

class NodeEkspresiPembaruan(NodeEkspresi):
    """Mewakili operasi pembaruan (increment/decrement): ++var, var--."""
    _fields = ['operator', 'argumen', 'prefix']
    def __init__(self, operator, argumen, prefix):
        self.operator = operator
        self.argumen = argumen
        self.prefix = prefix

class NodeEkspresiPenugasan(NodeEkspresi):
    """Mewakili operasi penugasan: a = b, a += b."""
    _fields = ['operator', 'kiri', 'kanan']
    def __init__(self, operator, kiri, kanan):
        self.operator = operator
        self.kiri = kiri
        self.kanan = kanan

class NodeEkspresiLogis(NodeEkspresi):
    """Mewakili operasi logis: a && b, a || b."""
    _fields = ['operator', 'kiri', 'kanan']
    def __init__(self, operator, kiri, kanan):
        self.operator = operator
        self.kiri = kiri
        self.kanan = kanan

class NodeEkspresiKondisional(NodeEkspresi):
    """Mewakili ekspresi kondisional (ternary): tes ? konsekuen : alternatif."""
    _fields = ['tes', 'konsekuen', 'alternatif']
    def __init__(self, tes, konsekuen, alternatif):
        self.tes = tes
        self.konsekuen = konsekuen
        self.alternatif = alternatif

class NodeEkspresiBaru(NodeEkspresi):
    """Mewakili ekspresi 'new': new Konstruktor()."""
    _fields = ['callee', 'argumen']
    def __init__(self, callee, argumen):
        self.callee = callee
        self.argumen = argumen

class NodeEkspresiUrutan(NodeEkspresi):
    """Mewakili serangkaian ekspresi yang dipisahkan koma."""
    _fields = ['daftar_ekspresi']
    def __init__(self, daftar_ekspresi):
        self.daftar_ekspresi = daftar_ekspresi

class NodeLiteralTemplate(NodeEkspresi):
    """Mewakili sebuah template literal: `halo ${nama}`."""
    _fields = ['quasis', 'ekspresi']
    def __init__(self, quasis, ekspresi):
        self.quasis = quasis
        self.ekspresi = ekspresi

class NodeElemenTemplate(NodeAST):
    """Bagian dari TemplateLiteral, bisa mentah atau hasil komputasi."""
    _fields = ['nilai', 'tail']
    def __init__(self, nilai, tail):
        self.nilai = nilai
        self.tail = tail

class NodeEkspresiTemplateBertag(NodeEkspresi):
    """Mewakili pemanggilan fungsi dengan template literal: tag`template`."""
    _fields = ['tag', 'quasi']
    def __init__(self, tag, quasi):
        self.tag = tag
        self.quasi = quasi

class NodePropertiMeta(NodeEkspresi):
    """Mewakili meta-properti seperti 'new.target' atau 'import.meta'."""
    _fields = ['meta', 'properti']
    def __init__(self, meta, properti):
        self.meta = meta
        self.properti = properti

class NodeEkspresiAwait(NodeEkspresi):
    """Mewakili ekspresi 'await'."""
    _fields = ['argumen']
    def __init__(self, argumen):
        self.argumen = argumen

class NodeEkspresiImpor(NodeEkspresi):
    """Mewakili ekspresi impor dinamis: import('...')."""
    _fields = ['sumber']
    def __init__(self, sumber):
        self.sumber = sumber

class NodeEkspresiRantai(NodeEkspresi):
    """Mewakili optional chaining: obj?.prop atau obj?.()."""
    _fields = ['ekspresi']
    def __init__(self, ekspresi):
        self.ekspresi = ekspresi
