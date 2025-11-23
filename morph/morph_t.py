"""
SKELETON SELF-HOSTING: DEFINISI TOKEN
=====================================
File ini berisi draf kode Morph untuk mendefinisikan Token.
Ini adalah padanan dari `transisi/morph_t.py` tetapi ditulis dalam sintaks Morph.
"""

MORPH_SOURCE = r"""
# core/morph_t.fox
# Definisi Token dan Tipe Token

# Konstanta Tipe Token
biar EOF = "EOF"
biar ILLEGAL = "ILLEGAL"
biar IDENTIFIER = "IDENTIFIER"
biar INT = "INT"
biar STRING = "STRING"

# Operator
biar ASSIGN = "="
biar PLUS = "+"
biar MINUS = "-"
biar BANG = "!"
biar ASTERISK = "*"
biar SLASH = "/"
biar EQ = "=="
biar NOT_EQ = "!="
biar LT = "<"
biar GT = ">"
biar COMMA = ","
biar SEMICOLON = ";"
biar LPAREN = "("
biar RPAREN = ")"
biar LBRACE = "{"
biar RBRACE = "}"
biar LBRACKET = "["
biar RBRACKET = "]"

# Keyword
biar FUNGSI = "FUNGSI"
biar BIAR = "BIAR"
biar TETAP = "TETAP"
biar JIKA = "JIKA"
biar MAKA = "MAKA"
biar LAIN = "LAIN"
biar AKHIR = "AKHIR"
biar KELAS = "KELAS"
biar WARISI = "WARISI"
biar KEMBALI = "KEMBALI"
biar ASINK = "ASINK"
biar TUNGGU = "TUNGGU"
biar PINJAM = "PINJAM"
biar SEBAGAI = "SEBAGAI"

# Peta Kata Kunci
biar keywords = {
    "fungsi": FUNGSI,
    "biar": BIAR,
    "tetap": TETAP,
    "jika": JIKA,
    "maka": MAKA,
    "lain": LAIN,
    "akhir": AKHIR,
    "kelas": KELAS,
    "warisi": WARISI,
    "kembali": KEMBALI,
    "asink": ASINK,
    "tunggu": TUNGGU,
    "pinjam": PINJAM,
    "sebagai": SEBAGAI
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
