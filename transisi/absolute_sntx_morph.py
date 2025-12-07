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
    def __init__(self, lokasi: Optional[Any] = None):
        self.lokasi = lokasi

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
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token
        self.nilai = token.nilai

class Identitas(Xprs):
    """Mewakili sebuah identifier (nama variabel, fungsi, dll.)."""
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token
        self.nama = token.nilai

class Daftar(Xprs):
    """Mewakili literal daftar, contoh: [1, "dua", benar]."""
    def __init__(self, elemen: List[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.elemen = elemen

class Kamus(Xprs):
    """Mewakili literal kamus, contoh: {"kunci": "nilai", "angka": 123}."""
    def __init__(self, pasangan: List[tuple[Xprs, Xprs]], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.pasangan = pasangan

# ==============================================================================
# Ekspresi (Expressions)
# ==============================================================================

class FoxBinary(Xprs):
    """Mewakili operasi dengan dua operand (kiri op kanan)."""
    def __init__(self, kiri: Xprs, op: Token, kanan: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kiri = kiri
        self.op = op
        self.kanan = kanan

class FoxUnary(Xprs):
    """Mewakili operasi dengan satu operand (op operand)."""
    def __init__(self, op: Token, kanan: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.op = op
        self.kanan = kanan

class PanggilFungsi(Xprs):
    """Mewakili pemanggilan sebuah fungsi."""
    def __init__(self, callee: Xprs, token_penutup: Token, argumen: List[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.callee = callee
        self.token = token_penutup # Untuk pelaporan error
        self.argumen = argumen

class Akses(Xprs):
    """Mewakili akses anggota/elemen menggunakan kurung siku []."""
    def __init__(self, objek: Xprs, kunci: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.objek = objek
        self.kunci = kunci

class EkspresiIrisan(Xprs):
    """Mewakili irisan/slicing native: objek[awal:akhir]."""
    def __init__(self, objek: Xprs, awal: Optional[Xprs], akhir: Optional[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.objek = objek
        self.awal = awal
        self.akhir = akhir

class Tunggu(Xprs):
    """Mewakili ekspresi `tunggu`."""
    def __init__(self, kata_kunci: Token, ekspresi: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kata_kunci = kata_kunci
        self.ekspresi = ekspresi

# ==============================================================================
# Pernyataan (Statements)
# ==============================================================================

class AmbilSemua(St):
    """Mewakili 'ambil_semua "path" [sebagai alias]'"""
    def __init__(self, path_file: Token, alias: Optional[Token], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.path_file = path_file
        self.alias = alias  # None jika tanpa alias

class AmbilSebagian(St):
    """Mewakili 'ambil_sebagian simbol1, simbol2 dari "path"'"""
    def __init__(self, daftar_simbol: List[Token], path_file: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.daftar_simbol = daftar_simbol
        self.path_file = path_file

class DeklarasiVariabel(St):
    """Mewakili deklarasi `biar nama = nilai` atau `tetap nama = nilai`.
    'nama' bisa berupa Token (variabel tunggal) atau List[Token] (destructuring)."""
    def __init__(self, jenis_deklarasi: Token, nama: Any, nilai: Optional[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.jenis_deklarasi = jenis_deklarasi
        self.nama = nama # Bisa Token atau List[Token]
        self.nilai = nilai

class Assignment(St):
    """Mewakili penugasan ulang `ubah target = nilai`."""
    def __init__(self, target: Xprs, nilai: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.target = target
        self.nilai = nilai

class PernyataanEkspresi(St):
    """Mewakili sebuah ekspresi yang berdiri sendiri sebagai pernyataan."""
    def __init__(self, ekspresi: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.ekspresi = ekspresi

class JikaMaka(St):
    """Mewakili struktur kontrol `jika-maka-lain`."""
    def __init__(self, kondisi: Xprs, blok_maka: Bagian, rantai_lain_jika: List[tuple[Xprs, Bagian]], blok_lain: Optional[Bagian], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kondisi = kondisi
        self.blok_maka = blok_maka
        self.rantai_lain_jika = rantai_lain_jika # List of (kondisi, blok)
        self.blok_lain = blok_lain

class Ternary(Xprs):
    """Mewakili operasi ternary `kondisi ? benar : salah`."""
    def __init__(self, kondisi: Xprs, benar: Xprs, salah: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kondisi = kondisi
        self.benar = benar
        self.salah = salah

class FungsiDeklarasi(St):
    """Mewakili deklarasi fungsi: `fungsi nama(p1, p2) maka ... akhir`."""
    def __init__(self, nama: Token, parameter: List[Token], badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.parameter = parameter
        self.badan = badan

class PernyataanKembalikan(St):
    """Mewakili pernyataan `kembalikan nilai`."""
    def __init__(self, kata_kunci: Token, nilai: Optional[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kata_kunci = kata_kunci
        self.nilai = nilai

class Berhenti(St):
    """Mewakili pernyataan `berhenti`."""
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token

class Lanjutkan(St):
    """Mewakili pernyataan `lanjutkan`."""
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token

class FungsiAsinkDeklarasi(St):
    """Mewakili deklarasi fungsi asinkron: `asink fungsi nama(p1) maka ... akhir`."""
    def __init__(self, nama: Token, parameter: List[Token], badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.parameter = parameter
        self.badan = badan

# ==============================================================================
# Node untuk Sistem Kelas
# ==============================================================================

class Kelas(St):
    """Mewakili deklarasi `kelas Nama [warisi Induk] maka ... akhir`."""
    def __init__(self, nama: Token, superkelas: Optional['Identitas'], metode: List['FungsiDeklarasi'], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.superkelas = superkelas
        self.metode = metode

class AmbilProperti(Xprs):
    """Mewakili akses properti atau metode, contoh: `objek.properti`."""
    def __init__(self, objek: Xprs, nama: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.objek = objek
        self.nama = nama

class AturProperti(Xprs):
    """Mewakili penugasan properti, contoh: `objek.properti = nilai`."""
    def __init__(self, objek: Xprs, nama: Token, nilai: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.objek = objek
        self.nama = nama
        self.nilai = nilai

class Ini(Xprs):
    """Mewakili kata kunci `ini`."""
    def __init__(self, kata_kunci: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kata_kunci = kata_kunci

class Induk(Xprs):
    """Mewakili kata kunci `induk` untuk akses superkelas."""
    def __init__(self, kata_kunci: Token, metode: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.kata_kunci = kata_kunci
        self.metode = metode


class Selama(St):
    """Mewakili perulangan `selama kondisi maka ... akhir`."""
    def __init__(self, token: Token, kondisi: Xprs, badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token  # Token dari kata kunci 'selama'
        self.kondisi = kondisi
        self.badan = badan

# --- Node untuk Deklarasi Tipe Varian ---

class Varian(MRPH):
    """Mewakili satu varian dalam deklarasi tipe, misal: 'Sukses(data)'."""
    def __init__(self, nama: Token, parameter: List[Token], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.parameter = parameter

class TipeDeklarasi(St):
    """Mewakili deklarasi tipe varian: `tipe Nama = Varian1 | Varian2`."""
    def __init__(self, nama: Token, daftar_varian: List[Varian], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.daftar_varian = daftar_varian

# --- Node untuk Pattern Matching `jodohkan` ---

class Pola(MRPH):
    """Kelas dasar untuk semua jenis pola dalam `jodohkan`."""
    pass

class PolaLiteral(Pola):
    """Pola yang cocok dengan nilai literal (angka, teks, dll.)."""
    def __init__(self, nilai: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nilai = nilai

class PolaWildcard(Pola):
    """Pola `_` yang cocok dengan nilai apa pun."""
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token

class PolaIkatanVariabel(Pola):
    """Pola yang mengikat nilai ke sebuah nama variabel baru."""
    def __init__(self, token: Token, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.token = token

class PolaVarian(Pola):
    """Pola yang cocok dengan sebuah varian tipe, misal: `Sukses(data)`."""
    def __init__(self, nama: Token, daftar_ikatan: List[Token], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama = nama
        self.daftar_ikatan = daftar_ikatan

class PolaDaftar(Pola):
    """Pola yang cocok dengan sebuah daftar, misal: `[x, _, ...sisa]`."""
    def __init__(self, daftar_pola: List[Pola], pola_sisa: Optional[Token], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.daftar_pola = daftar_pola
        self.pola_sisa = pola_sisa

class JodohkanKasus(MRPH):
    """Mewakili satu cabang `| pola [jaga kondisi] maka ...` dalam `jodohkan`."""
    def __init__(self, pola: Pola, jaga: Optional[Xprs], badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.pola = pola
        self.jaga = jaga
        self.badan = badan

class Jodohkan(St):
    """Mewakili struktur `jodohkan ekspresi dengan ... akhir`."""
    def __init__(self, ekspresi: Xprs, kasus: List[JodohkanKasus], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.ekspresi = ekspresi
        self.kasus = kasus

# --- Node untuk Fitur Bawaan ---

class Tulis(St):
    """Mewakili pernyataan `tulis(...)`."""
    def __init__(self, argumen: List[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.argumen = argumen

class Warnai(St):
    """Mewakili struktur `warnai <kode> maka ... akhir`."""
    def __init__(self, warna: Xprs, badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.warna = warna
        self.badan = badan

class Ambil(Xprs):
    """Mewakili ekspresi `ambil("prompt")`."""
    def __init__(self, prompt: Optional[Xprs], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.prompt = prompt

class Pinjam(St):
    """Mewakili FFI `pinjam "nama_file.py" [sebagai alias]`."""
    def __init__(self, path_file: Token, alias: Optional[Token], butuh_aot: bool = False, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.path_file = path_file
        self.alias = alias
        self.butuh_aot = butuh_aot

# --- Node untuk Pernyataan `pilih` (Switch-Case) ---

class Pilih(St):
    """Mewakili struktur `pilih ... ketika ... lainnya ... akhir`."""
    def __init__(self, ekspresi: Xprs, kasus: List['PilihKasus'], kasus_lainnya: Optional['KasusLainnya'], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.ekspresi = ekspresi
        self.kasus = kasus
        self.kasus_lainnya = kasus_lainnya

class PilihKasus(MRPH):
    """Mewakili satu cabang `ketika` dalam blok `pilih`."""
    def __init__(self, nilai: List[Xprs], badan: Bagian):
        self.nilai = nilai
        self.badan = badan

class KasusLainnya(MRPH):
    """Mewakili cabang `lainnya` dalam blok `pilih`."""
    def __init__(self, badan: Bagian):
        self.badan = badan

# --- Node untuk Error Handling ---

class Tangkap(MRPH):
    """
    Mewakili satu blok 'tangkap' dalam struktur coba.
    tangkap nama [jika kondisi]
       ...
    """
    def __init__(self, nama_error: Optional[Token], kondisi_jaga: Optional[Xprs], badan: Bagian, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.nama_error = nama_error
        self.kondisi_jaga = kondisi_jaga
        self.badan = badan

class CobaTangkap(St):
    """
    Mewakili struktur error handling:
    coba
      ...
    tangkap e [jika ...]
      ...
    [akhirnya ...]
    akhir
    """
    def __init__(self, blok_coba: Bagian, daftar_tangkap: List[Tangkap], blok_akhirnya: Optional[Bagian], lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.blok_coba = blok_coba
        self.daftar_tangkap = daftar_tangkap
        self.blok_akhirnya = blok_akhirnya

class Lemparkan(St):
    """Mewakili pernyataan `lemparkan <pesan> [jenis <tipe>]`."""
    def __init__(self, ekspresi: Xprs, jenis: Optional[Xprs] = None, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.ekspresi = ekspresi
        self.jenis = jenis

class KonversiTeks(Xprs):
    """Mewakili konversi intrinsik ke teks, digunakan untuk interpolasi string."""
    def __init__(self, ekspresi: Xprs, lokasi: Optional[Any] = None):
        super().__init__(lokasi)
        self.ekspresi = ekspresi
