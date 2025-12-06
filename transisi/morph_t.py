# transisi/morph_t.py
# Fondasi untuk "Kelahiran Kembali MORPH"
# Mendefinisikan struktur data Token dan tipe-tipe token.

from enum import Enum, auto
from typing import NamedTuple, Any

class TipeToken(Enum):
    # Penanda Akhir File
    ADS = auto() # Akhir Dari Segalanya

    # Tipe Literal
    TEKS = auto()          # "ini adalah teks"
    ANGKA = auto()         # 123, 45.67
    NAMA = auto()          # nama variabel atau fungsi

    # Operator Aritmatika
    TAMBAH = auto()        # +
    KURANG = auto()        # -
    KALI = auto()          # *
    BAGI = auto()          # /
    PANGKAT = auto()       # ^
    MODULO = auto()        # %

    # Operator Bitwise
    BIT_AND = auto()       # &
    BIT_OR = auto()        # |
    BIT_XOR = auto()       # ~ (XOR, tapi ~ biasanya NOT. Di sini kita pakai ~ untuk XOR?)
                           # Tunggu, standard:
                           # & = AND
                           # | = OR
                           # ^ = XOR (biasanya)
                           # ~ = NOT (Unary)
                           # << = LSHIFT
                           # >> = RSHIFT
                           # Di Python lx.py sebelumnya, ^ dipakai untuk PANGKAT (Exponent).
                           # Morph pakai ^ untuk pangkat.
                           # Jadi XOR butuh simbol lain? Atau operator teks 'xor'?
                           # Mari cek standar. Python pakai ** untuk pangkat, ^ untuk XOR.
                           # Morph pakai ^ untuk PANGKAT (TipeToken.PANGKAT).
                           # Jadi kita butuh simbol XOR.
                           # Opsi: gunakan '~^' atau keyword 'xor'?
                           # Atau ubah PANGKAT jadi '**' dan ^ jadi XOR?
                           # Ubah PANGKAT jadi '**' berisiko backward compat.
                           # Mari gunakan '~' untuk BIT_NOT (Unary).
                           # XOR? Mungkin tidak ada simbol? Atau gunakan fungsi?
                           # Cek instruksi user: "&, |, ^, <<, >>, ~".
                           # User minta ^ jadi XOR?
                           # Jika ^ jadi XOR, PANGKAT hilang?
                           # "Update Lexer... untuk mengenali token &, |, ^, <<, >>, ~"
                           # Ini berarti PANGKAT akan diganti atau ^ dioverload?
                           # Biasanya ^ adalah XOR. Pangkat pakai `**` atau fungsi.
                           # Saya akan ubah ^ menjadi BIT_XOR sesuai instruksi user.
                           # Dan tambahkan BIT_NOT (~), LSHIFT (<<), RSHIFT (>>).

    BIT_NOT = auto()       # ~
    GESER_KIRI = auto()    # <<
    GESER_KANAN = auto()   # >>

    # Operator Perbandingan
    SAMA_DENGAN = auto()   # ==
    TIDAK_SAMA = auto()    # !=
    KURANG_DARI = auto()   # <
    LEBIH_DARI = auto()    # >
    KURANG_SAMA = auto()   # <=
    LEBIH_SAMA = auto()    # >=

    # Operator Logika
    DAN = auto()           # dan
    ATAU = auto()          # atau
    TIDAK = auto()         # tidak

    # Tanda Baca & Simbol
    TITIK_KOMA = auto()    # ;
    KOMA = auto()          # ,
    TITIK_DUA = auto()     # :
    TITIK = auto()         # .
    TITIK_TIGA = auto()    # ...
    TANDA_PANAH = auto()   # ->

    KURUNG_BUKA = auto()   # (
    KURUNG_TUTUP = auto()  # )
    KURAWAL_BUKA = auto()  # {
    KURAWAL_TUTUP = auto() # }
    SIKU_BUKA = auto()     # [
    SIKU_TUTUP = auto()    # ]
    GARIS_PEMISAH = auto() # | (Digunakan untuk Pattern Matching, tapi bisa dioverload untuk BIT_OR?)
                           # Parser harus membedakan konteks.
                           # Tapi TipeToken harus unik.
                           # GARIS_PEMISAH vs BIT_OR.
                           # Simbolnya sama '|'.
                           # Lexer akan emit satu jenis token. Parser yang menafsirkan.
                           # Mari pakai nama BIT_OR saja, dan parser Jodohkan gunakan BIT_OR token.

    TANYA = auto()         # ?

    # Penugasan
    SAMADENGAN = auto()    # =

    # Kata Kunci (Keywords)
    KELAS = auto()         # Deklarasi kelas
    WARISI = auto()        # Pewarisan kelas
    INI = auto()           # Referensi instance (this/self)
    INDUK = auto()         # Referensi kelas induk (super)
    TIPE = auto()          # Deklarasi tipe varian
    BIAR = auto()          # Variabel (mutable)
    TETAP = auto()         # Konstanta (immutable)
    UBAH = auto()          # Re-assignment
    FUNGSI = auto()        # Deklarasi fungsi
    KEMBALI = auto()       # Return statement
    KEMBALIKAN = auto()    # Alias (tidak digunakan secara aktif oleh parser)
    JIKA = auto()          # If
    MAKA = auto()          # Then
    LAIN = auto()          # Else
    LAIN_JIKA = auto()     # Else if
    SELAMA = auto()        # While loop
    PILIH = auto()         # Switch
    KETIKA = auto()        # Case
    LAINNYA = auto()       # Default case in switch
    BERHENTI = auto()      # break
    LANJUTKAN = auto()     # continue
    AKHIR = auto()         # End of a block (fungsi, jika, dll.)
    JODOHKAN = auto()      # Pattern matching
    DENGAN = auto()        # 'with' in pattern matching
    JAGA = auto()          # 'jaga' guard in pattern matching
    AMBIL = auto()         # User input
    TULIS = auto()         # Print
    PINJAM = auto()        # FFI

    # Kata Kunci Modul
    AMBIL_SEMUA = auto()   # ambil_semua "module"
    AMBIL_SEBAGIAN = auto()# ambil_sebagian a, b dari "module"
    DARI = auto()          # 'dari' in ambil_sebagian
    SEBAGAI = auto()       # 'sebagai' in ambil_semua

    # Kata Kunci Error Handling
    COBA = auto()          # coba
    TANGKAP = auto()       # tangkap
    AKHIRNYA = auto()      # akhirnya
    LEMPARKAN = auto()     # lemparkan (throw)
    JENIS = auto()         # jenis (opsional, untuk sugar syntax)

    # Kata Kunci IO
    WARNAI = auto()        # warnai

    # Kata Kunci Async
    ASINK = auto()         # asink
    TUNGGU = auto()        # tunggu

    # Compiler Hint
    AOT = auto()           # aot (Ahead-of-Time)

    # Nilai Bawaan
    BENAR = auto()         # true
    SALAH = auto()         # false
    NIL = auto()           # null/nil

    # Lain-lain
    AKHIR_BARIS = auto()   # Newline (\n)
    TIDAK_DIKENAL = auto() # Token tidak dikenal/error

class Token(NamedTuple):
    tipe: TipeToken
    nilai: Any
    baris: int
    kolom: int

# Membuat pemetaan dari kata kunci string ke TipeToken
KATA_KUNCI = {
    "kelas": TipeToken.KELAS,
    "warisi": TipeToken.WARISI,
    "ini": TipeToken.INI,
    "induk": TipeToken.INDUK,
    "tipe": TipeToken.TIPE,
    "biar": TipeToken.BIAR,
    "tetap": TipeToken.TETAP,
    "ubah": TipeToken.UBAH,
    "fungsi": TipeToken.FUNGSI,
    "kembali": TipeToken.KEMBALI,
    "kembalikan": TipeToken.KEMBALIKAN, # Tetap ada untuk jaga-jaga, tapi tidak jadi andalan
    "jika": TipeToken.JIKA,
    "maka": TipeToken.MAKA,
    "lain": TipeToken.LAIN,
    "lainjika": TipeToken.LAIN_JIKA,
    "selama": TipeToken.SELAMA,
    "pilih": TipeToken.PILIH,
    "ketika": TipeToken.KETIKA,
    "lainnya": TipeToken.LAINNYA,
    "berhenti": TipeToken.BERHENTI,
    "lanjutkan": TipeToken.LANJUTKAN,
    "akhir": TipeToken.AKHIR,
    "jodohkan": TipeToken.JODOHKAN,
    "dengan": TipeToken.DENGAN,
    "jaga": TipeToken.JAGA,
    "ambil": TipeToken.AMBIL,
    "tulis": TipeToken.TULIS,
    "pinjam": TipeToken.PINJAM,
    "ambil_semua": TipeToken.AMBIL_SEMUA,
    "ambil_sebagian": TipeToken.AMBIL_SEBAGIAN,
    "dari": TipeToken.DARI,
    "sebagai": TipeToken.SEBAGAI,
    "benar": TipeToken.BENAR,
    "salah": TipeToken.SALAH,
    "nil": TipeToken.NIL,
    "dan": TipeToken.DAN,
    "atau": TipeToken.ATAU,
    "tidak": TipeToken.TIDAK,
    "asink": TipeToken.ASINK,
    "tunggu": TipeToken.TUNGGU,
    "aot": TipeToken.AOT,
    "coba": TipeToken.COBA,
    "tangkap": TipeToken.TANGKAP,
    "akhirnya": TipeToken.AKHIRNYA,
    "lemparkan": TipeToken.LEMPARKAN,
    "jenis": TipeToken.JENIS,
    "warnai": TipeToken.WARNAI,
}
