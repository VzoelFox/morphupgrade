# morph_engine/node_ast.py
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
# NODE LEVEL-ATAS (MODUL) - INTI UNIVERSAL AST
# ==============================================================================

class NodeProgram(NodeModul):
    """Mewakili seluruh program, berisi daftar pernyataan."""
    _fields = ['daftar_pernyataan']
    def __init__(self, daftar_pernyataan):
        self.daftar_pernyataan = daftar_pernyataan

# ==============================================================================
# LITERAL, VARIABEL & STRUKTUR DATA - INTI UNIVERSAL AST
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
# KONTEKS EKSPRESI - INTI UNIVERSAL AST (PYTHON)
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
# EKSPRESI - INTI UNIVERSAL AST
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
# PERNYATAAN (STATEMENTS) - INTI UNIVERSAL AST (MORPH)
# ==============================================================================

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
    def __init__(self, kondisi, badan, orelse=None):
        self.kondisi = kondisi
        self.badan = badan
        self.orelse = orelse if orelse is not None else []

class NodePerulanganFor(NodePernyataan):
    """Mewakili perulangan 'for': 'for target in iter maka ... akhir'."""
    def __init__(self, target, iter, badan, orelse=None):
        self.target = target
        self.iter = iter
        self.badan = badan
        self.orelse = orelse if orelse is not None else []

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
# PERNYATAAN (STATEMENTS) - TAMBAHAN DARI PYTHON AST (FASE 1)
# ==============================================================================

class NodeAugAssign(NodePernyataan):
    """Mewakili augmented assignment: target op= value."""
    def __init__(self, target, op, value):
        self.target = target
        self.op = op
        self.value = value

class NodeDelete(NodePernyataan):
    """Mewakili pernyataan 'del'."""
    def __init__(self, targets):
        self.targets = targets

class NodeWith(NodePernyataan):
    """Mewakili pernyataan 'with'."""
    def __init__(self, items, body):
        self.items = items
        self.body = body

class NodeWithItem:
    """Satu item dalam klausa 'with', yaitu 'context_expr [as optional_vars]'."""
    def __init__(self, context_expr, optional_vars=None):
        self.context_expr = context_expr
        self.optional_vars = optional_vars

class NodeAssert(NodePernyataan):
    """Mewakili pernyataan 'assert'."""
    def __init__(self, test, msg=None):
        self.test = test
        self.msg = msg

class NodeGlobal(NodePernyataan):
    """Mewakili pernyataan 'global'."""
    def __init__(self, names):
        self.names = names

class NodeNonlocal(NodePernyataan):
    """Mewakili pernyataan 'nonlocal'."""
    def __init__(self, names):
        self.names = names

# ==============================================================================
# EKSPRESI - TAMBAHAN DARI PYTHON AST (FASE 2)
# ==============================================================================

class NodeNamedExpr(NodeEkspresi):
    """Mewakili named expression (walrus operator): 'target := value'."""
    def __init__(self, target, value):
        self.target = target
        self.value = value

class NodeComprehension:
    """Helper node untuk 'for' clause dalam comprehensions."""
    def __init__(self, target, iter, ifs, is_async):
        self.target = target
        self.iter = iter
        self.ifs = ifs
        self.is_async = is_async

class NodeListComp(NodeEkspresi):
    """Mewakili list comprehension: '[elt for ...]'."""
    def __init__(self, elt, generators):
        self.elt = elt
        self.generators = generators

class NodeSetComp(NodeEkspresi):
    """Mewakili set comprehension: '{elt for ...}'."""
    def __init__(self, elt, generators):
        self.elt = elt
        self.generators = generators

class NodeDictComp(NodeEkspresi):
    """Mewakili dict comprehension: '{key: value for ...}'."""
    def __init__(self, key, value, generators):
        self.key = key
        self.value = value
        self.generators = generators

class NodeGeneratorExp(NodeEkspresi):
    """Mewakili generator expression: '(elt for ...)'."""
    def __init__(self, elt, generators):
        self.elt = elt
        self.generators = generators

# ==============================================================================
# FITUR PYTHON LANJUTAN (FASE 3A)
# ==============================================================================

class AsyncFunctionDef(NodePernyataan):
    """Mewakili deklarasi fungsi 'async def'."""
    def __init__(self, name, args, body, decorator_list, returns=None):
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.returns = returns

class AsyncWith(NodePernyataan):
    """Mewakili pernyataan 'async with'."""
    def __init__(self, items, body):
        self.items = items
        self.body = body

class JoinedStr(NodeEkspresi):
    """Mewakili f-string."""
    def __init__(self, values):
        self.values = values

class FormattedValue(NodeEkspresi):
    """Mewakili satu bagian dalam f-string, seperti '{nama}'."""
    def __init__(self, value, conversion=-1, format_spec=None):
        self.value = value
        self.conversion = conversion
        self.format_spec = format_spec

# ==============================================================================
# FITUR PYTHON LANJUTAN (FASE 3B - TYPE HINTS)
# ==============================================================================

class AnnAssign(NodePernyataan):
    """Mewakili anoted assignment: 'target: annotation = value'."""
    def __init__(self, target, annotation, value=None, simple=0):
        self.target = target
        self.annotation = annotation
        self.value = value
        self.simple = simple

class TypeAlias(NodePernyataan):
    """Mewakili pernyataan 'type' (PEP 613)."""
    def __init__(self, name, type_params, value):
        self.name = name
        self.type_params = type_params
        self.value = value

class TypeVar(NodeAST):
    """Mewakili TypeVar."""
    def __init__(self, name, bound=None, default_value=None):
        self.name = name
        self.bound = bound
        self.default_value = default_value

class ParamSpec(NodeAST):
    """Mewakili ParamSpec."""
    def __init__(self, name, default_value=None):
        self.name = name
        self.default_value = default_value

class TypeVarTuple(NodeAST):
    """Mewakili TypeVarTuple."""
    def __init__(self, name, default_value=None):
        self.name = name
        self.default_value = default_value

# ==============================================================================
# FITUR PYTHON LANJUTAN (FASE 3C - PATTERN MATCHING)
# ==============================================================================

class Match(NodePernyataan):
    """Mewakili pernyataan 'match'."""
    def __init__(self, subject, cases):
        self.subject = subject
        self.cases = cases

class MatchCase:
    """Mewakili satu blok 'case' dalam pernyataan 'match'."""
    def __init__(self, pattern, guard=None, body=None):
        self.pattern = pattern
        self.guard = guard
        self.body = body

class MatchValue(NodeAST):
    """Mewakili pola literal atau nilai dalam 'case'."""
    def __init__(self, value):
        self.value = value

class MatchSingleton(NodeAST):
    """Mewakili pola singleton (True, False, None) dalam 'case'."""
    def __init__(self, value):
        self.value = value

class MatchSequence(NodeAST):
    """Mewakili pola sekuens (list/tuple) dalam 'case'."""
    def __init__(self, patterns):
        self.patterns = patterns

class MatchStar(NodeAST):
    """Mewakili pola '*' dalam sekuens 'case'."""
    def __init__(self, name=None):
        self.name = name

class MatchMapping(NodeAST):
    """Mewakili pola mapping (dict) dalam 'case'."""
    def __init__(self, keys, patterns, rest=None):
        self.keys = keys
        self.patterns = patterns
        self.rest = rest

class MatchClass(NodeAST):
    """Mewakili pola kelas dalam 'case'."""
    def __init__(self, cls, patterns, kwd_attrs, kwd_patterns):
        self.cls = cls
        self.patterns = patterns
        self.kwd_attrs = kwd_attrs
        self.kwd_patterns = kwd_patterns

class MatchAs(NodeAST):
    """Mewakili pola penangkapan ('as') atau wildcard ('_') dalam 'case'."""
    def __init__(self, pattern=None, name=None):
        self.pattern = pattern
        self.name = name

class MatchOr(NodeAST):
    """Mewakili pola 'or' ('|') dalam 'case'."""
    def __init__(self, patterns):
        self.patterns = patterns
