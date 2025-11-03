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

    # Simbol & Operator
    PENGENAL = "PENGENAL"
    TEKS = "TEKS"
    ANGKA = "ANGKA"
    SAMA_DENGAN = "="
    TITIK_DUA = ":"
    BUKA_KURUNG = "("
    TUTUP_KURUNG = ")"

    # Lain-lain
    AKHIR_BARIS = "AKHIR_BARIS"
    ADS = "ADS" # Akhir Dari Segalanya (End of File)

class Token:
    def __init__(self, tipe, nilai=None):
        self.tipe = tipe
        self.nilai = nilai

    def __repr__(self):
        return f"Token({self.tipe.name}, {repr(self.nilai)})"
