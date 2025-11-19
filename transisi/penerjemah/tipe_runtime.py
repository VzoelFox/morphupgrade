# transisi/penerjemah/tipe_runtime.py
# File ini berisi kelas-kelas yang merepresentasikan objek dan struktur data
# saat runtime di dalam interpreter Morph.

from .. import absolute_sntx_morph as ast
from ..morph_t import TipeToken, Token
from ..kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama
)
import asyncio

# Exception khusus untuk menangani alur kontrol 'kembalikan'
class NilaiKembalian(Exception):
    def __init__(self, nilai):
        self.nilai = nilai

class BerhentiLoop(Exception): pass
class LanjutkanLoop(Exception): pass

class FungsiBawaan:
    """Wrapper untuk fungsi Python yang diekspos sebagai fungsi built-in MORPH."""
    def __init__(self, panggil_logic):
        self.panggil_logic = panggil_logic

    def __call__(self, argumen):
        return self.panggil_logic(argumen)

    def __str__(self):
        return "<fungsi bawaan>"

class FungsiBawaanAsink:
    """Wrapper untuk fungsi async Python yang diekspos sebagai fungsi built-in MORPH."""
    def __init__(self, panggil_logic):
        self.panggil_logic = panggil_logic

    async def __call__(self, argumen):
        return await self.panggil_logic(argumen)

    def __str__(self):
        return "<fungsi bawaan asinkron>"

class Lingkungan:
    """Manajemen scope dan simbol (variabel/fungsi)."""
    def __init__(self, induk=None):
        self.nilai = {}
        self.konstanta = set()
        self.induk = induk

    def definisi(self, nama: str, nilai, adalah_konstan=False):
        self.nilai[nama] = nilai
        if adalah_konstan:
            self.konstanta.add(nama)

    def dapatkan(self, token):
        nama = token.nilai
        lingkungan = self
        while lingkungan is not None:
            if nama in lingkungan.nilai:
                return lingkungan.nilai[nama]
            lingkungan = lingkungan.induk
        raise KesalahanNama(token, f"Variabel '{nama}' belum didefinisikan.")

    def tetapkan(self, token, nilai):
        nama = token.nilai
        lingkungan = self
        while lingkungan is not None:
            if nama in lingkungan.nilai:
                if nama in lingkungan.konstanta:
                    raise KesalahanRuntime(
                        token,
                        f"Tidak bisa mengubah konstanta '{nama}'. Variabel ini dideklarasikan dengan 'tetap'."
                    )
                lingkungan.nilai[nama] = nilai
                return
            lingkungan = lingkungan.induk
        raise KesalahanNama(token, f"Variabel '{nama}' belum didefinisikan.")

class InstansiVarian:
    """Mewakili sebuah instance dari sebuah varian, misal: Sukses("data")."""
    def __init__(self, konstruktor, argumen):
        self.konstruktor = konstruktor
        self.argumen = argumen

    def __repr__(self):
        if not self.argumen:
            return self.konstruktor.nama
        args_str = ', '.join(map(repr, self.argumen))
        return f"{self.konstruktor.nama}({args_str})"

class KonstruktorVarian:
    """Mewakili satu konstruktor varian (misal: Sukses) yang bisa dipanggil."""
    def __init__(self, nama: str, aritas: int): # aritas = jumlah parameter
        self.nama = nama
        self.aritas = aritas

    def __call__(self, argumen, token_panggil):
        if len(argumen) != self.aritas:
            raise KesalahanTipe(
                token_panggil,
                f"Konstruktor varian '{self.nama}' mengharapkan {self.aritas} argumen, tapi menerima {len(argumen)}."
            )
        return InstansiVarian(self, argumen)

    def __repr__(self):
        return f"<konstruktor varian {self.nama}/{self.aritas}>"

class TipeVarian:
    """Mewakili definisi sebuah tipe varian (misal: Respon)."""
    def __init__(self, nama: str):
        self.nama = nama
        self.konstruktor = {} # nama_varian -> KonstruktorVarian

    def __repr__(self):
        return f"<tipe {self.nama}>"

class MorphInstance:
    """Mewakili sebuah instance dari sebuah kelas."""
    def __init__(self, kelas):
        self.kelas = kelas
        self.properti = {}

    def __str__(self):
        return f"<instance dari {self.kelas.nama}>"

    def dapatkan(self, nama_token, dari_internal=False):
        nama = nama_token.nilai
        if nama.startswith('_') and not dari_internal:
            raise KesalahanNama(nama_token, f"Properti atau metode '{nama}' bersifat privat dan tidak bisa diakses dari luar kelas.")
        if nama in self.properti:
            return self.properti[nama]
        metode = self.kelas.cari_metode(nama)
        if metode is not None:
            return metode.bind(self)
        raise KesalahanNama(nama_token, f"Properti atau metode '{nama}' tidak ditemukan pada instance {self.kelas.nama}.")

    def tetapkan(self, nama_token, nilai, dari_internal=False):
        nama = nama_token.nilai
        if nama.startswith('_') and not dari_internal:
            raise KesalahanNama(nama_token, f"Properti '{nama}' bersifat privat dan tidak bisa diubah dari luar kelas.")
        self.properti[nama] = nilai

class MorphKelas:
    """Mewakili sebuah kelas itu sendiri."""
    def __init__(self, nama: str, superkelas, metode: dict):
        self.nama = nama
        self.superkelas = superkelas
        self.metode = metode

    def __str__(self):
        return f"<kelas {self.nama}>"

    async def panggil(self, interpreter, node_panggil: ast.PanggilFungsi):
        instance = MorphInstance(self)
        inisiasi = self.cari_metode("inisiasi")
        if inisiasi:
            tasks = [interpreter._evaluasi(arg) for arg in node_panggil.argumen]
            argumen = await asyncio.gather(*tasks)
            await inisiasi.bind(instance).panggil(interpreter, argumen, node_panggil.token)
        elif len(node_panggil.argumen) > 0:
            raise KesalahanTipe(node_panggil.token, "Konstruktor default tidak menerima argumen.")
        return instance

    def cari_metode(self, nama: str):
        if nama in self.metode:
            return self.metode[nama]
        if self.superkelas is not None:
            return self.superkelas.cari_metode(nama)
        return None

class Fungsi:
    """Kelas untuk representasi fungsi saat runtime."""
    def __init__(self, deklarasi: ast.FungsiDeklarasi, penutup: Lingkungan, adalah_inisiasi=False):
        self.deklarasi = deklarasi
        self.penutup = penutup
        self.adalah_inisiasi = adalah_inisiasi

    def __str__(self):
        return f"<fungsi {self.deklarasi.nama.nilai}>"

    def bind(self, instance):
        lingkungan = Lingkungan(induk=self.penutup)
        lingkungan.definisi("ini", instance)
        return Fungsi(self.deklarasi, lingkungan, self.adalah_inisiasi)

    def panggil(self, interpreter, argumen: list, token_panggil: Token):
        async def _eksekusi_internal():
            lingkungan_fungsi = Lingkungan(induk=self.penutup)
            if len(argumen) != len(self.deklarasi.parameter):
                raise KesalahanTipe(
                    token_panggil,
                    f"Jumlah argumen tidak cocok. Diharapkan {len(self.deklarasi.parameter)}, diterima {len(argumen)}."
                )
            for param, arg in zip(self.deklarasi.parameter, argumen):
                lingkungan_fungsi.definisi(param.nilai, arg)
            interpreter.call_stack.append(f"fungsi '{self.deklarasi.nama.nilai}' dipanggil dari baris {token_panggil.baris}")
            try:
                await interpreter._eksekusi_blok(self.deklarasi.badan, lingkungan_fungsi)
            except KesalahanRuntime as e:
                if not hasattr(e, 'morph_stack'):
                    e.morph_stack = list(interpreter.call_stack)
                raise
            except NilaiKembalian as e:
                if self.adalah_inisiasi:
                    return self.penutup.dapatkan(Token(TipeToken.NAMA, "ini", 0, 0))
                return e.nilai
            finally:
                interpreter.call_stack.pop()
                if self.adalah_inisiasi:
                    return self.penutup.dapatkan(Token(TipeToken.NAMA, "ini", 0, 0))
            return None
        return _eksekusi_internal()

class FungsiAsink(Fungsi):
    def __str__(self):
        return f"<fungsi asinkron {self.deklarasi.nama.nilai}>"

    def bind(self, instance):
        lingkungan = Lingkungan(induk=self.penutup)
        lingkungan.definisi("ini", instance)
        return FungsiAsink(self.deklarasi, lingkungan, self.adalah_inisiasi)
