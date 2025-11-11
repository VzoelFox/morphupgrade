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
    TANDA_PANAH = auto()   # ->

    KURUNG_BUKA = auto()   # (
    KURUNG_TUTUP = auto()  # )
    KURAWAL_BUKA = auto()  # {
    KURAWAL_TUTUP = auto() # }
    SIKU_BUKA = auto()     # [
    SIKU_TUTUP = auto()    # ]
    GARIS_PEMISAH = auto() # |

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
    KEMBALIKAN = auto()    # Return statement
    KEMBALI = auto()       # Alias untuk Kembalikan
    JIKA = auto()          # If
    MAKA = auto()          # Then
    LAIN = auto()          # Else
    LAIN_JIKA = auto()     # Else if
    SELAMA = auto()        # While loop
    PILIH = auto()         # Switch
    KETIKA = auto()        # Case
    LAINNYA = auto()       # Default case in switch
    AKHIR = auto()         # End of a block (fungsi, jika, dll.)
    JODOHKAN = auto()      # Pattern matching
    DENGAN = auto()        # 'with' in pattern matching and 'tugas' options
    AMBIL = auto()         # User input
    TULIS = auto()         # Print
    PINJAM = auto()        # FFI

    # Kata Kunci Modul
    AMBIL_SEMUA = auto()   # ambil_semua "module"
    AMBIL_SEBAGIAN = auto()# ambil_sebagian a, b dari "module"
    DARI = auto()          # 'dari' in ambil_sebagian
    SEBAGAI = auto()       # 'sebagai' in ambil_semua

    # Kata Kunci Async
    ASINK = auto()         # asink
    TUNGGU = auto()        # tunggu

    # Kata Kunci FoxEngine
    TUGAS = auto()         # tugas
    TFOX = auto()          # tfox (thread-fox)
    AOT = auto()           # aot (ahead-of-time)
    JIT = auto()           # jit (just-in-time)
    IO = auto()            # io (input/output)

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
    "kembalikan": TipeToken.KEMBALIKAN,
    "kembali": TipeToken.KEMBALI,
    "jika": TipeToken.JIKA,
    "maka": TipeToken.MAKA,
    "lain": TipeToken.LAIN,
    "lainjika": TipeToken.LAIN_JIKA,
    "selama": TipeToken.SELAMA,
    "pilih": TipeToken.PILIH,
    "ketika": TipeToken.KETIKA,
    "lainnya": TipeToken.LAINNYA,
    "akhir": TipeToken.AKHIR,
    "jodohkan": TipeToken.JODOHKAN,
    "dengan": TipeToken.DENGAN,
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
    "tugas": TipeToken.TUGAS,
    "tfox": TipeToken.TFOX,
    "aot": TipeToken.AOT,
    "jit": TipeToken.JIT,
    "io": TipeToken.IO,
}
