# transisi/absolute_sntx_morph.py
# Kerangka Abstract Syntax Tree (AST) untuk "Kelahiran Kembali MORPH"

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from .morph_t import Token

# ==============================================================================
# Kelas Dasar (Base Classes)
# ==============================================================================

class MRPH(ABC):
    """Kelas dasar untuk semua node AST di MORPH."""
    pass

class St(MRPH):
    """Kelas dasar untuk semua jenis Pernyataan (Statements)."""
    pass

class Xprs(MRPH):
    """Kelas dasar untuk semua jenis Ekspresi (Expressions)."""
    pass

# ==============================================================================
# Node Level Atas (Struktur Program)
# ==============================================================================

class Bagian(MRPH):
    """Mewakili seluruh program atau satu file sumber."""
    def __init__(self, daftar_pernyataan: List[St]):
        self.daftar_pernyataan = daftar_pernyataan

# ==============================================================================
# Literal, Variabel & Struktur Data
# ==============================================================================

class Konstanta(Xprs):
    """Mewakili nilai literal (angka, teks, boolean, nil)."""
    def __init__(self, token: Token):
        self.token = token
        self.nilai = token.nilai

class Identitas(Xprs):
    """Mewakili sebuah identifier (nama variabel, fungsi, dll.)."""
    def __init__(self, token: Token):
        self.token = token
        self.nama = token.nilai

class Daftar(Xprs):
    """Mewakili literal daftar, contoh: [1, "dua", benar]."""
    def __init__(self, elemen: List[Xprs]):
        self.elemen = elemen

class Kamus(Xprs):
    """Mewakili literal kamus, contoh: {"kunci": "nilai", "angka": 123}."""
    def __init__(self, pasangan: List[tuple[Xprs, Xprs]]):
        self.pasangan = pasangan

# ==============================================================================
# Ekspresi (Expressions)
# ==============================================================================

class FoxBinary(Xprs):
    """Mewakili operasi dengan dua operand (kiri op kanan)."""
    def __init__(self, kiri: Xprs, op: Token, kanan: Xprs):
        self.kiri = kiri
        self.op = op
        self.kanan = kanan

class FoxUnary(Xprs):
    """Mewakili operasi dengan satu operand (op operand)."""
    def __init__(self, op: Token, kanan: Xprs):
        self.op = op
        self.kanan = kanan

class PanggilFungsi(Xprs):
    """Mewakili pemanggilan sebuah fungsi."""
    def __init__(self, callee: Xprs, token_penutup: Token, argumen: List[Xprs]):
        self.callee = callee
        self.token = token_penutup # Untuk pelaporan error
        self.argumen = argumen

class Akses(Xprs):
    """Mewakili akses anggota/elemen menggunakan kurung siku []."""
    def __init__(self, objek: Xprs, kunci: Xprs):
        self.objek = objek
        self.kunci = kunci

# ==============================================================================
# Pernyataan (Statements)
# ==============================================================================

class AmbilSemua(St):
    """Mewakili 'ambil_semua "path" [sebagai alias]'"""
    def __init__(self, path_file: Token, alias: Optional[Token]):
        self.path_file = path_file
        self.alias = alias  # None jika tanpa alias

class AmbilSebagian(St):
    """Mewakili 'ambil_sebagian simbol1, simbol2 dari "path"'"""
    def __init__(self, daftar_simbol: List[Token], path_file: Token):
        self.daftar_simbol = daftar_simbol
        self.path_file = path_file

class DeklarasiVariabel(St):
    """Mewakili deklarasi `biar nama = nilai` atau `tetap nama = nilai`."""
    def __init__(self, jenis_deklarasi: Token, nama: Token, nilai: Optional[Xprs]):
        self.jenis_deklarasi = jenis_deklarasi
        self.nama = nama
        self.nilai = nilai

class Assignment(St):
    """Mewakili penugasan ulang `ubah nama = nilai`."""
    def __init__(self, nama: Token, nilai: Xprs):
        self.nama = nama
        self.nilai = nilai

class PernyataanEkspresi(St):
    """Mewakili sebuah ekspresi yang berdiri sendiri sebagai pernyataan."""
    def __init__(self, ekspresi: Xprs):
        self.ekspresi = ekspresi

class JikaMaka(St):
    """Mewakili struktur kontrol `jika-maka-lain`."""
    def __init__(self, kondisi: Xprs, blok_maka: Bagian, rantai_lain_jika: List[tuple[Xprs, Bagian]], blok_lain: Optional[Bagian]):
        self.kondisi = kondisi
        self.blok_maka = blok_maka
        self.rantai_lain_jika = rantai_lain_jika # List of (kondisi, blok)
        self.blok_lain = blok_lain

class FungsiDeklarasi(St):
    """Mewakili deklarasi fungsi: `fungsi nama(p1, p2) maka ... akhir`."""
    def __init__(self, nama: Token, parameter: List[Token], badan: Bagian):
        self.nama = nama
        self.parameter = parameter
        self.badan = badan

class PernyataanKembalikan(St):
    """Mewakili pernyataan `kembalikan nilai`."""
    def __init__(self, kata_kunci: Token, nilai: Optional[Xprs]):
        self.kata_kunci = kata_kunci
        self.nilai = nilai

class Selama(St):
    """Mewakili perulangan `selama kondisi maka ... akhir`."""
    def __init__(self, kondisi: Xprs, badan: Bagian):
        self.kondisi = kondisi
        self.badan = badan

# --- Node untuk Fitur Bawaan ---

class Tulis(St):
    """Mewakili pernyataan `tulis(...)`."""
    def __init__(self, argumen: List[Xprs]):
        self.argumen = argumen

class Ambil(Xprs):
    """Mewakili ekspresi `ambil("prompt")`."""
    def __init__(self, prompt: Optional[Xprs]):
        self.prompt = prompt

class Pinjam(St):
    """Mewakili FFI `pinjam "nama_file.py"`."""
    def __init__(self, path_file: Token):
        self.path_file = path_file

# --- Node untuk Pernyataan `pilih` (Switch-Case) ---

class Pilih(St):
    """Mewakili struktur `pilih ... ketika ... lainnya ... akhir`."""
    def __init__(self, ekspresi: Xprs, kasus: List['PilihKasus'], kasus_lainnya: Optional['KasusLainnya']):
        self.ekspresi = ekspresi
        self.kasus = kasus
        self.kasus_lainnya = kasus_lainnya

class PilihKasus(MRPH):
    """Mewakili satu cabang `ketika` dalam blok `pilih`."""
    def __init__(self, nilai: Xprs, badan: Bagian):
        self.nilai = nilai
        self.badan = badan

class KasusLainnya(MRPH):
    """Mewakili cabang `lainnya` dalam blok `pilih`."""
    def __init__(self, badan: Bagian):
        self.badan = badan
