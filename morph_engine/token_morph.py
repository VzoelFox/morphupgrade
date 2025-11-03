# morph_engine/token_morph.py
from enum import Enum

class TipeToken(Enum):
    # Kata Kunci
    BIAR = "BIAR"
    TETAP = "TETAP"
    TULIS = "TULIS"
    AMBIL = "AMBIL"
    DARI = "DARI"
    BUKA = "BUKA"
    TUTUP = "TUTUP"
    DAN = "DAN"
    ATAU = "ATAU"
    TIDAK = "TIDAK"
    BENAR = "BENAR"
    SALAH = "SALAH"
    JIKA = "JIKA"
    MAKA = "MAKA"
    AKHIR = "AKHIR"

    # Simbol & Operator
    PENGENAL = "PENGENAL"
    TEKS = "TEKS"
    ANGKA = "ANGKA"
    SAMA_DENGAN = "="
    TITIK_DUA = ":"
    BUKA_KURUNG = "("
    TUTUP_KURUNG = ")"
    KOMA = ","

    # Operator Aritmatika
    TAMBAH = "+"
    KURANG = "-"
    KALI = "*"
    BAGI = "/"
    MODULO = "%"

    # Operator Perbandingan
    SAMA_DENGAN_SAMA = "=="
    TIDAK_SAMA = "!="
    LEBIH_BESAR = ">"
    LEBIH_KECIL = "<"
    LEBIH_BESAR_SAMA = ">="
    LEBIH_KECIL_SAMA = "<="

    # Lain-lain
    AKHIR_BARIS = "AKHIR_BARIS"
    ADS = "ADS" # Akhir Dari Segalanya (End of File)

class Token:
    def __init__(self, tipe, nilai=None, baris=None, kolom=None):
        self.tipe = tipe
        self.nilai = nilai
        self.baris = baris
        self.kolom = kolom

    def __repr__(self):
        if self.baris is not None:
            return f"Token({self.tipe.name}, {repr(self.nilai)}, baris={self.baris}, kolom={self.kolom})"
        return f"Token({self.tipe.name}, {repr(self.nilai)})"
