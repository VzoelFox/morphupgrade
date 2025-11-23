"""
SKELETON SELF-HOSTING: DEFINISI TOKEN
=====================================
File ini berisi draf kode Morph untuk mendefinisikan Token lengkap.
Ini adalah padanan dari `transisi/morph_t.py`.
"""

MORPH_SOURCE = r"""
# core/morph_t.fox
# Definisi Token dan Tipe Token

# Konstanta Tipe Token (Enum values)
biar EOF = "EOF"
biar ILLEGAL = "ILLEGAL"
biar IDENTIFIER = "IDENTIFIER"

# Tipe Literal
biar STRING = "STRING"
biar INT = "INT"
biar FLOAT = "FLOAT" # Added FLOAT

# Operator Aritmatika
biar PLUS = "+"
biar MINUS = "-"
biar ASTERISK = "*"
biar SLASH = "/"
biar PERCENT = "%"   # MODULO
biar CARET = "^"     # PANGKAT

# Operator Perbandingan
biar ASSIGN = "="
biar EQ = "=="
biar NOT_EQ = "!="
biar LT = "<"
biar GT = ">"
biar LTE = "<="
biar GTE = ">="

# Operator Logika (Keywords in Morph, but types here)
biar AND = "DAN"
biar OR = "ATAU"
biar NOT = "TIDAK"

# Delimiter & Punctuation
biar COMMA = ","
biar SEMICOLON = ";"
biar COLON = ":"
biar DOT = "."
biar ELLIPSIS = "..."
biar ARROW = "->"

biar LPAREN = "("
biar RPAREN = ")"
biar LBRACE = "{"
biar RBRACE = "}"
biar LBRACKET = "["
biar RBRACKET = "]"
biar PIPE = "|"

# Keywords (Kata Kunci)
biar KELAS = "KELAS"
biar WARISI = "WARISI"
biar INI = "INI"
biar INDUK = "INDUK"
biar TIPE = "TIPE"
biar BIAR = "BIAR"
biar TETAP = "TETAP"
biar UBAH = "UBAH"
biar FUNGSI = "FUNGSI"
biar KEMBALI = "KEMBALI"
biar JIKA = "JIKA"
biar MAKA = "MAKA"
biar LAIN = "LAIN"
biar LAIN_JIKA = "LAIN_JIKA"
biar SELAMA = "SELAMA"
biar PILIH = "PILIH"
biar KETIKA = "KETIKA"
biar LAINNYA = "LAINNYA"
biar BERHENTI = "BERHENTI"
biar LANJUTKAN = "LANJUTKAN"
biar AKHIR = "AKHIR"
biar JODOHKAN = "JODOHKAN"
biar DENGAN = "DENGAN"
biar JAGA = "JAGA"
biar AMBIL = "AMBIL"
biar TULIS = "TULIS"
biar PINJAM = "PINJAM"
biar AMBIL_SEMUA = "AMBIL_SEMUA"
biar AMBIL_SEBAGIAN = "AMBIL_SEBAGIAN"
biar DARI = "DARI"
biar SEBAGAI = "SEBAGAI"

# Keywords: Literals & Async & Error
biar BENAR = "BENAR"
biar SALAH = "SALAH"
biar NIL = "NIL"
biar ASINK = "ASINK"
biar TUNGGU = "TUNGGU"
biar AOT = "AOT"
biar COBA = "COBA"
biar TANGKAP = "TANGKAP"
biar AKHIRNYA = "AKHIRNYA"
biar LEMPARKAN = "LEMPARKAN"
biar JENIS = "JENIS"

# Peta Kata Kunci (String -> Tipe)
biar keywords = {
    "kelas": KELAS,
    "warisi": WARISI,
    "ini": INI,
    "induk": INDUK,
    "tipe": TIPE,
    "biar": BIAR,
    "tetap": TETAP,
    "ubah": UBAH,
    "fungsi": FUNGSI,
    "kembali": KEMBALI,
    "jika": JIKA,
    "maka": MAKA,
    "lain": LAIN,
    "lainjika": LAIN_JIKA,
    "selama": SELAMA,
    "pilih": PILIH,
    "ketika": KETIKA,
    "lainnya": LAINNYA,
    "berhenti": BERHENTI,
    "lanjutkan": LANJUTKAN,
    "akhir": AKHIR,
    "jodohkan": JODOHKAN,
    "dengan": DENGAN,
    "jaga": JAGA,
    "ambil": AMBIL,
    "tulis": TULIS,
    "pinjam": PINJAM,
    "ambil_semua": AMBIL_SEMUA,
    "ambil_sebagian": AMBIL_SEBAGIAN,
    "dari": DARI,
    "sebagai": SEBAGAI,
    "benar": BENAR,
    "salah": SALAH,
    "nil": NIL,
    "dan": AND,
    "atau": OR,
    "tidak": NOT,
    "asink": ASINK,
    "tunggu": TUNGGU,
    "aot": AOT,
    "coba": COBA,
    "tangkap": TANGKAP,
    "akhirnya": AKHIRNYA,
    "lemparkan": LEMPARKAN,
    "jenis": JENIS
}

fungsi cari_keyword(ident) maka
    jika keywords.punya(ident) maka
        kembali keywords[ident]
    lain
        kembali IDENTIFIER
    akhir
akhir

# Definisi Kelas Token
kelas Token maka
    biar tipe
    biar literal
    biar baris
    biar kolom

    fungsi init(tipe_token, nilai_literal, no_baris, no_kolom) maka
        ini.tipe = tipe_token
        ini.literal = nilai_literal
        ini.baris = no_baris
        ini.kolom = no_kolom
    akhir

    fungsi string() maka
        kembali "Token(" + ini.tipe + ", " + ini.literal + ")"
    akhir
akhir
"""
