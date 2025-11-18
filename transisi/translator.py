# transisi/translator.py
# Interpreter untuk "Kelahiran Kembali MORPH"

import os
import json
import asyncio
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token
from .kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama,
    KesalahanIndeks, KesalahanKunci, KesalahanPembagianNol,
    KesalahanPola
)
from .lx import Leksikal
from .crusher import Pengurai
from .modules import ModuleLoader
from .ffi import FFIBridge, PythonModule, PythonObject
from .kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama,
    KesalahanIndeks, KesalahanKunci, KesalahanPembagianNol,
    KesalahanAtributFFI
)

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

# --- Representasi Runtime untuk Tipe Varian ---

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

# --- Representasi Runtime untuk Sistem Kelas ---

class MorphInstance:
    """Mewakili sebuah instance dari sebuah kelas."""
    def __init__(self, kelas):
        self.kelas = kelas
        self.properti = {}

    def __str__(self):
        return f"<instance dari {self.kelas.nama}>"

    def dapatkan(self, nama_token, dari_internal=False):
        nama = nama_token.nilai

        # Aturan akses privat
        if nama.startswith('_') and not dari_internal:
            raise KesalahanNama(nama_token, f"Properti atau metode '{nama}' bersifat privat dan tidak bisa diakses dari luar kelas.")

        if nama in self.properti:
            return self.properti[nama]

        metode = self.kelas.cari_metode(nama)
        if metode is not None:
            # Saat metode dipanggil, `ini` sudah ter-bind, jadi kita anggap 'internal'
            return metode.bind(self)

        raise KesalahanNama(nama_token, f"Properti atau metode '{nama}' tidak ditemukan pada instance {self.kelas.nama}.")

    def tetapkan(self, nama_token, nilai, dari_internal=False):
        nama = nama_token.nilai
        # Aturan akses privat
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
            # Ekstrak argumen dari node PanggilFungsi
            tasks = [interpreter._evaluasi(arg) for arg in node_panggil.argumen]
            argumen = await asyncio.gather(*tasks)
            # Panggil konstruktor dengan argumen yang dievaluasi
            await inisiasi.bind(instance).panggil(interpreter, argumen, node_panggil.token)
        elif len(node_panggil.argumen) > 0:
            # Jika tidak ada inisiasi tapi ada argumen, ini adalah error
            raise KesalahanTipe(node_panggil.token, "Konstruktor default tidak menerima argumen.")
        return instance

    def cari_metode(self, nama: str):
        if nama in self.metode:
            return self.metode[nama]

        if self.superkelas is not None:
            return self.superkelas.cari_metode(nama)

        return None

# Kelas untuk representasi fungsi saat runtime
class Fungsi:
    def __init__(self, deklarasi: ast.FungsiDeklarasi, penutup: Lingkungan, adalah_inisiasi=False):
        self.deklarasi = deklarasi
        self.penutup = penutup
        self.adalah_inisiasi = adalah_inisiasi

    def __str__(self):
        return f"<fungsi {self.deklarasi.nama.nilai}>"

    def bind(self, instance):
        """Membuat instance metode yang terikat pada sebuah objek."""
        lingkungan = Lingkungan(induk=self.penutup)
        lingkungan.definisi("ini", instance)
        return Fungsi(self.deklarasi, lingkungan, self.adalah_inisiasi)

    def panggil(self, interpreter, argumen: list, token_panggil: Token):
        # Metode ini sekarang SINKRON dan mengembalikan COROUTINE.
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

        # Kembalikan coroutine untuk dijalankan oleh `kunjungi_PanggilFungsi` atau `tunggu`.
        return _eksekusi_internal()

        # Kembalikan coroutine untuk dijalankan oleh `kunjungi_PanggilFungsi` atau `tunggu`.
        return _eksekusi_internal()

class FungsiAsink(Fungsi):
    def __str__(self):
        return f"<fungsi asinkron {self.deklarasi.nama.nilai}>"

    def bind(self, instance):
        """Membuat instance metode yang terikat pada sebuah objek."""
        lingkungan = Lingkungan(induk=self.penutup)
        lingkungan.definisi("ini", instance)
        # Pastikan bind mengembalikan instance dari FungsiAsink
        return FungsiAsink(self.deklarasi, lingkungan, self.adalah_inisiasi)

import io
import sys
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .runtime_fox import RuntimeMORPHFox
from .aot_visitor import AotVisitor

class Penerjemah:
    """Visitor yang mengekusi AST."""
    def __init__(self, formatter, output_stream=sys.stdout):
        self.lingkungan_global = Lingkungan()
        self.lingkungan = self.lingkungan_global
        self.formatter = formatter
        self.output_stream = output_stream
        self.call_stack = []
        self.current_file = None
        self.module_loader = ModuleLoader(self)
        self.ffi_bridge = FFIBridge()
        self.runtime: "RuntimeMORPHFox" | None = None

        # --- Batas Rekursi ---
        BATAS_REKURSI_DEFAULT = 800
        batas_dari_env = os.environ.get('MORPH_RECURSION_LIMIT')
        if batas_dari_env and batas_dari_env.isdigit():
            self.batas_rekursi = int(batas_dari_env)
        else:
            self.batas_rekursi = BATAS_REKURSI_DEFAULT
        self.tingkat_rekursi = 0
        # ---------------------

        # Daftarkan fungsi built-in
        self.lingkungan_global.definisi("baca_json", FungsiBawaan(self._fungsi_baca_json))
        self.lingkungan_global.definisi("tidur", FungsiBawaan(self._fungsi_tidur_sync_wrapper))

    def _fungsi_baca_json(self, argumen):
        if len(argumen) != 1:
            raise KesalahanTipe(None, f"Fungsi 'baca_json' memerlukan 1 argumen (path file), tetapi menerima {len(argumen)}.")

        path_file = argumen[0]
        if not isinstance(path_file, str):
            raise KesalahanTipe(None, f"Argumen untuk 'baca_json' harus berupa teks (string) path file.")

        try:
            with open(path_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise KesalahanRuntime(None, f"File tidak ditemukan: '{path_file}'")
        except json.JSONDecodeError as e:
            raise KesalahanRuntime(None, f"Gagal mem-parsing file '{path_file}'. Format JSON tidak valid: {e.msg}")
        except Exception as e:
            raise KesalahanRuntime(None, f"Terjadi kesalahan saat membaca file '{path_file}': {e}")

    def _fungsi_tidur_sync_wrapper(self, argumen):
        if len(argumen) != 1:
            raise KesalahanTipe(None, "Fungsi 'tidur' memerlukan 1 argumen (durasi dalam detik).")
        durasi = argumen[0]
        if not isinstance(durasi, (int, float)):
            raise KesalahanTipe(None, "Argumen untuk 'tidur' harus berupa angka.")
        # Kembalikan coroutine, jangan di-await di sini
        return asyncio.sleep(durasi)


    async def terjemahkan(self, program: ast.Bagian, current_file: str | None = None):
        # Inisialisasi dan pembersihan state untuk eksekusi
        self.module_loader._loading_stack.clear()
        self.current_file = current_file
        self.lingkungan = self.lingkungan_global
        daftar_kesalahan = []

        # Tambahkan file utama ke stack untuk pelacakan impor sirkular yang akurat
        if current_file:
            abs_path = os.path.abspath(current_file)
            self.module_loader._loading_stack.append(abs_path)

        # --- AOT Pass ---
        await self._jalankan_aot_pass(program)

        try:
            for pernyataan in program.daftar_pernyataan:
                # Panggil pembungkus yang menangani error top-level
                hasil_eksekusi = await self._eksekusi_dan_tangkap_error(pernyataan)
                if hasil_eksekusi is not None: # Jika ada error yang dikembalikan
                    daftar_kesalahan.append(hasil_eksekusi)
                    return daftar_kesalahan
            return daftar_kesalahan
        finally:
            # Pastikan stack selalu bersih setelah eksekusi, apa pun hasilnya
            self.module_loader._loading_stack.clear()

    async def _jalankan_aot_pass(self, program: ast.Bagian):
        """
        Menganalisis program untuk mencari petunjuk AOT dan secara proaktif
        memicu kompilasi untuk fungsi-fungsi yang relevan.
        """
        if not self.runtime:
            return

        aot_aliases = set()
        declared_functions = {}

        # 1. Jalankan pernyataan `pinjam` terlebih dahulu untuk mengisi lingkungan
        for pernyataan in program.daftar_pernyataan:
            if isinstance(pernyataan, ast.Pinjam):
                await self._eksekusi(pernyataan)
                if pernyataan.butuh_aot and pernyataan.alias:
                    aot_aliases.add(pernyataan.alias.nilai)
            elif isinstance(pernyataan, (ast.FungsiDeklarasi, ast.FungsiAsinkDeklarasi)):
                # Simpan node deklarasi untuk analisis nanti
                declared_functions[pernyataan.nama.nilai] = pernyataan

        if not aot_aliases:
            return

        # 2. Analisis fungsi-fungsi yang menggunakan alias AOT
        visitor = AotVisitor(aot_aliases)
        tasks_kompilasi = []
        for nama_fungsi, node_fungsi in declared_functions.items():
            if visitor.periksa(node_fungsi.badan):
                print(f"INFO: AOT hint ditemukan. Memicu kompilasi untuk fungsi '{nama_fungsi}'.")
                # Buat objek Fungsi untuk diteruskan ke runtime
                fungsi_obj = Fungsi(node_fungsi, self.lingkungan_global)
                # Kumpulkan tugas kompilasi
                tasks_kompilasi.append(self.runtime.paksa_kompilasi_aot(fungsi_obj))

        # Jalankan semua kompilasi AOT secara bersamaan
        if tasks_kompilasi:
            await asyncio.gather(*tasks_kompilasi)

    async def _eksekusi_dan_tangkap_error(self, pernyataan: ast.St):
        """Metode ini adalah pembungkus top-level yang menangkap dan memformat error."""
        try:
            await self._eksekusi(pernyataan)
            return None # Menandakan tidak ada error
        except KesalahanRuntime as e:
            stack_untuk_dilaporkan = getattr(e, 'morph_stack', self.call_stack)
            # Gunakan node ekspresi yang lebih spesifik jika tersedia, jika tidak, gunakan pernyataan
            node_untuk_dilaporkan = getattr(e, 'node', pernyataan)
            return self.formatter.format_runtime(e, stack_untuk_dilaporkan, node=node_untuk_dilaporkan)

    async def _eksekusi(self, pernyataan: ast.St):
        """Metode ini hanya menjalankan pernyataan dan membiarkan exception menyebar."""
        await pernyataan.terima(self)

    async def _evaluasi(self, ekspresi: ast.Xprs):
        try:
            return await ekspresi.terima(self)
        except KesalahanRuntime as e:
            # Lemparkan kembali agar bisa ditangkap di _eksekusi dengan node pernyataan yang lengkap
            # atau di level yang lebih tinggi yang memiliki konteks lebih baik.
            # Di masa depan, kita bisa menambahkan node ekspresi ke 'e' di sini.
            if not hasattr(e, 'node'):
                 e.node = ekspresi
            raise e

    # --- Visitor untuk Pernyataan (Statements) ---

    async def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            await self._eksekusi(pernyataan)

    async def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        await self._evaluasi(node.ekspresi)

    async def kunjungi_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        nilai = None
        if node.nilai is not None:
            nilai = await self._evaluasi(node.nilai)

        adalah_konstan = (node.jenis_deklarasi.tipe == TipeToken.TETAP)
        self.lingkungan.definisi(node.nama.nilai, nilai, adalah_konstan)

    async def kunjungi_Tulis(self, node: ast.Tulis):
        output = []
        for arg in node.argumen:
            nilai = await self._evaluasi(arg)
            output.append(self._ke_string(nilai))
        self.output_stream.write(' '.join(output))

    async def kunjungi_Assignment(self, node: ast.Assignment):
        nilai = await self._evaluasi(node.nilai)

        if isinstance(node.nama, Token):
            # Assignment variabel biasa: ubah x = 10
            self.lingkungan.tetapkan(node.nama, nilai)
        elif isinstance(node.nama, ast.Akses):
            # Assignment item: ubah daftar[0] = 10
            target_node = node.nama
            objek = await self._evaluasi(target_node.objek)
            kunci = await self._evaluasi(target_node.kunci)

            if isinstance(objek, list):
                if not isinstance(kunci, int):
                    raise KesalahanTipe(target_node.kunci.token, "Indeks daftar harus berupa angka.")
                if not (0 <= kunci < len(objek)):
                    raise KesalahanIndeks(target_node.kunci.token, "Indeks di luar jangkauan.")
                objek[kunci] = nilai
            elif isinstance(objek, dict):
                # Kunci kamus MORPH harus string, tapi mari kita izinkan angka juga untuk fleksibilitas
                if not isinstance(kunci, (str, int, float)):
                    raise KesalahanKunci(target_node.kunci.token, "Kunci kamus harus berupa teks atau angka.")
                objek[kunci] = nilai
            else:
                raise KesalahanTipe(target_node.objek.token, "Hanya item dalam daftar atau kamus yang dapat diubah.")
        else:
            # Seharusnya tidak pernah terjadi dengan parser yang benar
            raise KesalahanRuntime(node.nama, "Target assignment tidak valid.")

    async def kunjungi_Kelas(self, node: ast.Kelas):
        superkelas = None
        if node.superkelas is not None:
            superkelas = await self._evaluasi(node.superkelas)
            if not isinstance(superkelas, MorphKelas):
                raise KesalahanTipe(node.superkelas.token, "Superkelas harus berupa sebuah kelas.")

        self.lingkungan.definisi(node.nama.nilai, None) # Deklarasi maju untuk rekursi

        lingkungan_kelas = self.lingkungan
        if superkelas is not None:
            lingkungan_kelas = Lingkungan(induk=self.lingkungan)
            lingkungan_kelas.definisi("induk", superkelas)

        metode = {}
        for metode_node in node.metode:
            adalah_inisiasi = metode_node.nama.nilai == "inisiasi"
            # Periksa apakah metode ini asinkron
            if isinstance(metode_node, ast.FungsiAsinkDeklarasi):
                 fungsi = FungsiAsink(metode_node, lingkungan_kelas, adalah_inisiasi)
            else:
                 fungsi = Fungsi(metode_node, lingkungan_kelas, adalah_inisiasi)
            metode[metode_node.nama.nilai] = fungsi

        kelas = MorphKelas(node.nama.nilai, superkelas, metode)
        self.lingkungan.tetapkan(node.nama, kelas)


    async def kunjungi_TipeDeklarasi(self, node: ast.TipeDeklarasi):
        nama_tipe = node.nama.nilai
        tipe_varian = TipeVarian(nama_tipe)

        # Mendefinisikan tipe itu sendiri di lingkungan
        self.lingkungan.definisi(nama_tipe, tipe_varian)

        # Mendefinisikan setiap konstruktor varian di lingkungan
        for varian_node in node.daftar_varian:
            nama_varian = varian_node.nama.nilai
            aritas = len(varian_node.parameter)
            konstruktor = KonstruktorVarian(nama_varian, aritas)

            # Simpan konstruktor di dalam tipe untuk referensi
            tipe_varian.konstruktor[nama_varian] = konstruktor

            # Buat konstruktor tersedia secara global di scope
            if nama_varian in self.lingkungan.nilai:
                raise KesalahanNama(varian_node.nama, f"Nama '{nama_varian}' sudah didefinisikan sebelumnya.")
            self.lingkungan.definisi(nama_varian, konstruktor)

    async def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        fungsi = Fungsi(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)

    async def kunjungi_FungsiAsinkDeklarasi(self, node: ast.FungsiAsinkDeklarasi):
        fungsi = FungsiAsink(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)


    async def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        nilai = None
        if node.nilai is not None:
            nilai = await self._evaluasi(node.nilai)
        raise NilaiKembalian(nilai)

    async def kunjungi_Berhenti(self, node: ast.Berhenti):
        raise BerhentiLoop()

    async def kunjungi_Lanjutkan(self, node: ast.Lanjutkan):
        raise LanjutkanLoop()

    async def kunjungi_Selama(self, node: ast.Selama):
        loop_counter = 0
        MAX_ITERATIONS = int(os.getenv('MORPH_LOOP_LIMIT', '10000'))

        while self._apakah_benar(await self._evaluasi(node.kondisi)):
            loop_counter += 1
            if loop_counter > MAX_ITERATIONS:
                print(f"PERINGATAN: Loop limit tercapai di baris {node.token.baris}", file=sys.stderr)
                raise KesalahanRuntime(
                    node.token,
                    f"Loop melebihi batas iterasi maksimum ({MAX_ITERATIONS})."
                )
            try:
                await self._eksekusi_blok(node.badan, Lingkungan(induk=self.lingkungan))
            except LanjutkanLoop:
                continue
            except BerhentiLoop:
                break

    async def kunjungi_AmbilSemua(self, node: ast.AmbilSemua):
        exports = await self.module_loader.load_module(node.path_file, self.current_file)

        if node.alias:
            self.lingkungan.definisi(node.alias.nilai, exports)
        else:
            for nama, nilai in exports.items():
                self.lingkungan.definisi(nama, nilai)

    async def kunjungi_AmbilSebagian(self, node: ast.AmbilSebagian):
        exports = await self.module_loader.load_module(node.path_file, self.current_file)

        for simbol_token in node.daftar_simbol:
            nama = simbol_token.nilai
            if nama not in exports:
                raise KesalahanNama(
                    simbol_token,
                    f"Simbol '{nama}' tidak ditemukan di modul '{node.path_file.nilai}'."
                )
            self.lingkungan.definisi(nama, exports[nama])

    async def kunjungi_Pinjam(self, node: ast.Pinjam):
        module_path = node.path_file.nilai
        alias = node.alias.nilai if node.alias else None

        if not alias:
            raise KesalahanRuntime(node.path_file, "FFI import harus pakai alias ('sebagai').")

        py_module = self.ffi_bridge.import_module(module_path, node.path_file)
        self.lingkungan.definisi(alias, py_module)

    # --- Metode Internal untuk Modul ---

    async def _jalankan_modul(self, module_path: str) -> Dict[str, Any]:
        """Membaca file modul dan mendelegasikannya ke _jalankan_modul_dari_sumber."""
        try:
            # Operasi I/O yang akan kita ganti
            with open(module_path, 'r', encoding='utf-8') as f:
                source = f.read()
            return await self._jalankan_modul_dari_sumber(module_path, source)
        except IOError as e:
            raise KesalahanRuntime(None, f"Tidak bisa membaca file modul: {module_path}. Detail: {e}")

    async def _jalankan_modul_dari_sumber(self, module_path: str, source: str) -> Dict[str, Any]:
        """
        Mengeksekusi kode sumber modul dalam lingkungan baru.
        Ini adalah inti dari eksekusi modul, terpisah dari I/O.
        """
        lingkungan_sebelumnya = self.lingkungan
        file_sebelumnya = self.current_file

        # Setiap modul memiliki lingkungannya sendiri yang terisolasi (tidak mewarisi dari global)
        lingkungan_modul = Lingkungan(induk=None)
        self.lingkungan = lingkungan_modul
        self.current_file = module_path

        try:
            # Proses lexing, parsing, dan eksekusi
            leksikal = Leksikal(source, f"modul '{os.path.basename(module_path)}'")
            tokens, daftar_kesalahan_lexer = leksikal.buat_token()
            if daftar_kesalahan_lexer:
                kesalahan = daftar_kesalahan_lexer[0]
                pesan_error = kesalahan.get("pesan", "Error tidak diketahui")
                token_dummy = Token(TipeToken.TIDAK_DIKENAL, module_path, kesalahan.get("baris", 1), kesalahan.get("kolom", 1))
                raise KesalahanRuntime(token_dummy, f"Kesalahan leksikal di modul '{os.path.basename(module_path)}': {pesan_error}")

            parser = Pengurai(tokens)
            ast_modul = parser.urai()
            if parser.daftar_kesalahan:
                token_kesalahan, pesan = parser.daftar_kesalahan[0]
                raise KesalahanRuntime(token_kesalahan, f"Kesalahan sintaks di modul '{os.path.basename(module_path)}': {pesan}")

            for pernyataan in ast_modul.daftar_pernyataan:
                await self._eksekusi(pernyataan)

            # Kumpulkan ekspor (variabel/fungsi yang tidak diawali dengan '_')
            exports = {nama: nilai for nama, nilai in self.lingkungan.nilai.items() if not nama.startswith('_')}
            return exports

        finally:
            # Pulihkan lingkungan dan file sebelumnya
            self.lingkungan = lingkungan_sebelumnya
            self.current_file = file_sebelumnya

    # --- Visitor untuk Ekspresi (Expressions) ---

    async def kunjungi_Tunggu(self, node: ast.Tunggu):
        # Evaluasi ekspresi di dalam `tunggu`, yang SEHARUSNYA menghasilkan coroutine.
        awaitable = await self._evaluasi(node.ekspresi)

        # Sekarang, jalankan `await` pada hasilnya.
        if asyncio.iscoroutine(awaitable) or hasattr(awaitable, '__await__'):
            return await awaitable

        raise KesalahanTipe(node.kata_kunci, "Ekspresi yang mengikuti 'tunggu' harus bisa ditunggu (awaitable).")

    async def kunjungi_AmbilProperti(self, node: ast.AmbilProperti):
        objek = await self._evaluasi(node.objek)

        if isinstance(objek, (PythonModule, PythonObject)):
            attr_name = node.nama.nilai
            try:
                py_attr = objek.get_attribute(attr_name)
                return self.ffi_bridge.python_to_morph(py_attr)
            except AttributeError as e:
                obj_name = objek.name if isinstance(objek, PythonModule) else type(objek.obj).__name__
                raise KesalahanAtributFFI(
                    node.nama,
                    f"Atribut '{attr_name}' tidak ditemukan di objek Python '{obj_name}'.",
                    python_exception=e
                )

        if isinstance(objek, MorphInstance):
            adalah_akses_internal = isinstance(node.objek, ast.Ini)
            return objek.dapatkan(node.nama, dari_internal=adalah_akses_internal)

        if isinstance(objek, str):
             try:
                py_attr = getattr(objek, node.nama.nilai)
                return self.ffi_bridge.python_to_morph(py_attr)
             except AttributeError:
                pass

        raise KesalahanTipe(node.nama, "Hanya instance kelas atau modul FFI yang memiliki properti.")

    async def kunjungi_AturProperti(self, node: ast.AturProperti):
        adalah_akses_internal = isinstance(node.objek, ast.Ini)
        objek = await self._evaluasi(node.objek)
        if not isinstance(objek, MorphInstance):
            raise KesalahanTipe(node.nama, "Hanya instance dari kelas yang dapat diatur propertinya.")
        nilai = await self._evaluasi(node.nilai)
        objek.tetapkan(node.nama, nilai, dari_internal=adalah_akses_internal)
        return nilai

    async def kunjungi_Ini(self, node: ast.Ini):
        return self.lingkungan.dapatkan(node.kata_kunci)

    async def kunjungi_Induk(self, node: ast.Induk):
        superkelas = self.lingkungan.dapatkan(node.kata_kunci)
        instance = self.lingkungan.dapatkan(Token(TipeToken.NAMA, "ini", node.kata_kunci.baris, node.kata_kunci.kolom))
        metode = superkelas.cari_metode(node.metode.nilai)
        if metode is None:
            raise KesalahanRuntime(node.metode, f"Metode '{node.metode.nilai}' tidak ditemukan di superkelas.")
        return metode.bind(instance)

    async def kunjungi_Kamus(self, node: ast.Kamus):
        kamus = {}
        for kunci_node, nilai_node in node.pasangan:
            kunci = await self._evaluasi(kunci_node)
            if not isinstance(kunci, str):
                raise KesalahanKunci(kunci_node.token, "Kunci kamus harus berupa teks.")
            nilai = await self._evaluasi(nilai_node)
            kamus[kunci] = nilai
        return kamus

    async def kunjungi_Daftar(self, node: ast.Daftar):
        tasks = [self._evaluasi(elem) for elem in node.elemen]
        return await asyncio.gather(*tasks)

    async def kunjungi_Akses(self, node: ast.Akses):
        objek = await self._evaluasi(node.objek)
        kunci = await self._evaluasi(node.kunci)

        if isinstance(objek, (list, str)):
            if not isinstance(kunci, int):
                raise KesalahanTipe(node.kunci.token, "Indeks untuk daftar atau teks harus berupa angka.")
            if 0 <= kunci < len(objek):
                return objek[kunci]
            else:
                raise KesalahanIndeks(node.kunci.token, "Indeks di luar jangkauan.")

        if isinstance(objek, dict):
            if not isinstance(kunci, str):
                raise KesalahanKunci(node.kunci.token, "Kunci kamus harus berupa teks.")
            return objek.get(kunci, None)

        raise KesalahanTipe(node.objek.token, "Objek tidak dapat diakses menggunakan '[]'. Hanya berlaku untuk daftar, teks, dan kamus.")

    async def kunjungi_Ambil(self, node: ast.Ambil):
        prompt_str = ""
        if node.prompt:
            prompt_evaluasi = await self._evaluasi(node.prompt)
            prompt_str = self._ke_string(prompt_evaluasi)
        try:
            return input(prompt_str)
        except EOFError:
            return None

    async def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi):
        callee = await self._evaluasi(node.callee)

        is_morph_callable = isinstance(callee, (Fungsi, MorphKelas))

        if is_morph_callable:
            self.tingkat_rekursi += 1
            if self.tingkat_rekursi > self.batas_rekursi:
                self.tingkat_rekursi -= 1
                raise KesalahanRuntime(
                    node.token,
                    "wah ternyata batas kedalaman sudah tercapai,dan saya cuma bisa menggapainya sampai disini. coba anda gali lebih dalam dan saya akan menyelam kembali"
                )

        try:
            callee = await self._evaluasi(node.callee)
            tasks = [self._evaluasi(arg) for arg in node.argumen]
            argumen = await asyncio.gather(*tasks)

            is_morph_callable = isinstance(callee, (Fungsi, MorphKelas))

            if is_morph_callable:
                self.tingkat_rekursi += 1
                if self.tingkat_rekursi > self.batas_rekursi:
                    self.tingkat_rekursi -= 1
                    raise KesalahanRuntime(
                        node.token,
                        "Batas kedalaman rekursi tercapai."
                    )

            if isinstance(callee, MorphKelas):
                return await callee.panggil(self, node)

            if self.runtime and isinstance(callee, (Fungsi, FungsiAsink)):
                return await self.runtime.execute_function(callee, argumen)

            if isinstance(callee, (Fungsi, FungsiAsink)):
                coro = callee.panggil(self, argumen, node.token)
                if isinstance(callee, FungsiAsink):
                    return coro
                return await coro

            if isinstance(callee, KonstruktorVarian):
                return callee(argumen, node.token)
            if isinstance(callee, FungsiBawaan):
                try:
                    return callee(argumen)
                except (KesalahanTipe, KesalahanRuntime) as e:
                    e.token = node.token
                    raise e
            if isinstance(callee, FungsiBawaanAsink):
                 try:
                      return await callee(argumen)
                 except (KesalahanTipe, KesalahanRuntime) as e:
                      e.token = node.token
                      raise e
            if isinstance(callee, PythonObject):
                if not callable(callee.obj):
                    raise KesalahanTipe(node.token, "Objek Python ini tidak bisa dipanggil.")
                argumen_py = [self.ffi_bridge.morph_to_python(arg) for arg in argumen]
                hasil_py = self.ffi_bridge.safe_call(callee.obj, argumen_py, node.token)
                return self.ffi_bridge.python_to_morph(hasil_py)

            raise KesalahanTipe(node.token, "Hanya fungsi, kelas, atau objek FFI yang bisa dipanggil.")
        finally:
            if is_morph_callable:
                self.tingkat_rekursi -= 1

    async def kunjungi_Identitas(self, node: ast.Identitas):
        return self.lingkungan.dapatkan(node.token)

    async def kunjungi_Konstanta(self, node: ast.Konstanta):
        return node.nilai

    async def kunjungi_FoxUnary(self, node: ast.FoxUnary):
        kanan = await self._evaluasi(node.kanan)
        if node.op.tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kanan)
            return -kanan
        if node.op.tipe == TipeToken.TIDAK:
            return not self._apakah_benar(kanan)
        return None

    async def kunjungi_FoxBinary(self, node: ast.FoxBinary):
        op_tipe = node.op.tipe

        if op_tipe == TipeToken.DAN:
            kiri = await self._evaluasi(node.kiri)
            if not self._apakah_benar(kiri):
                return False
            return self._apakah_benar(await self._evaluasi(node.kanan))
        if op_tipe == TipeToken.ATAU:
            kiri = await self._evaluasi(node.kiri)
            if self._apakah_benar(kiri):
                return kiri
            return await self._evaluasi(node.kanan)

        kiri = await self._evaluasi(node.kiri)
        kanan = await self._evaluasi(node.kanan)

        if op_tipe == TipeToken.TAMBAH:
            if isinstance(kiri, (int, float)) and isinstance(kanan, (int, float)):
                return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str):
                return kiri + kanan
            raise KesalahanTipe(node.op, "Operan harus dua angka atau dua teks.")
        if op_tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri - kanan
        if op_tipe == TipeToken.KALI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri * kanan
        if op_tipe == TipeToken.BAGI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            if kanan == 0:
                raise KesalahanPembagianNol(node.op, "Tidak bisa membagi dengan nol.")
            hasil = kiri / kanan
            if hasil == int(hasil):
                return int(hasil)
            return hasil
        if op_tipe == TipeToken.MODULO:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri % kanan
        if op_tipe == TipeToken.PANGKAT:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri ** kanan
        if op_tipe in (TipeToken.LEBIH_DARI, TipeToken.KURANG_DARI, TipeToken.LEBIH_SAMA, TipeToken.KURANG_SAMA):
            if not ((isinstance(kiri, (int, float)) and isinstance(kanan, (int, float))) or
                    (isinstance(kiri, str) and isinstance(kanan, str))):
                raise KesalahanTipe(node.op, "Operan untuk perbandingan harus dua angka atau dua teks.")

            if op_tipe == TipeToken.LEBIH_DARI: return kiri > kanan
            if op_tipe == TipeToken.KURANG_DARI: return kiri < kanan
            if op_tipe == TipeToken.LEBIH_SAMA: return kiri >= kanan
            if op_tipe == TipeToken.KURANG_SAMA: return kiri <= kanan
        if op_tipe == TipeToken.SAMA_DENGAN:
            return kiri == kanan
        if op_tipe == TipeToken.TIDAK_SAMA:
            return kiri != kanan
        return None

    async def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        if self._apakah_benar(await self._evaluasi(node.kondisi)):
            await self._eksekusi_blok(node.blok_maka, Lingkungan(induk=self.lingkungan))
        else:
            for kondisi_lain, blok_lain in node.rantai_lain_jika:
                if self._apakah_benar(await self._evaluasi(kondisi_lain)):
                    await self._eksekusi_blok(blok_lain, Lingkungan(induk=self.lingkungan))
                    return
            if node.blok_lain is not None:
                await self._eksekusi_blok(node.blok_lain, Lingkungan(induk=self.lingkungan))

    async def kunjungi_Pilih(self, node: ast.Pilih):
        nilai_ekspresi = await self._evaluasi(node.ekspresi)
        kasus_cocok = False
        for kasus in node.kasus:
            # Normalisasi `kasus.nilai` menjadi list untuk menangani output dari kedua parser
            nilai_untuk_diperiksa = kasus.nilai if isinstance(kasus.nilai, list) else [kasus.nilai]

            for nilai_pembanding_node in nilai_untuk_diperiksa:
                nilai_pembanding = await self._evaluasi(nilai_pembanding_node)
                if nilai_ekspresi == nilai_pembanding:
                    await self._eksekusi_blok(kasus.badan, Lingkungan(induk=self.lingkungan))
                    kasus_cocok = True
                    break
            if kasus_cocok:
                break
        if not kasus_cocok and node.kasus_lainnya is not None:
            await self._eksekusi_blok(node.kasus_lainnya.badan, Lingkungan(induk=self.lingkungan))

    async def kunjungi_Jodohkan(self, node: ast.Jodohkan):
        nilai_ekspresi = await self._evaluasi(node.ekspresi)

        # --- Logika Pengecekan Exhaustiveness ---
        if isinstance(nilai_ekspresi, InstansiVarian):
            # Dapatkan definisi tipe dari instansi
            tipe_varian_obj = nilai_ekspresi.konstruktor
            # Cari objek TipeVarian di lingkungan saat ini
            lingkungan_saat_ini = self.lingkungan
            tipe_info = None
            while lingkungan_saat_ini:
                for v in lingkungan_saat_ini.nilai.values():
                    if isinstance(v, TipeVarian) and tipe_varian_obj.nama in v.konstruktor:
                        tipe_info = v
                        break
                if tipe_info:
                    break
                lingkungan_saat_ini = lingkungan_saat_ini.induk

            if tipe_info:
                semua_varian = set(tipe_info.konstruktor.keys())
                varian_tertangani = set()
                ada_wildcard = False

                for kasus in node.kasus:
                    if isinstance(kasus.pola, ast.PolaVarian):
                        varian_tertangani.add(kasus.pola.nama.nilai)
                    elif isinstance(kasus.pola, (ast.PolaWildcard, ast.PolaIkatanVariabel)):
                        ada_wildcard = True
                        break

                if not ada_wildcard:
                    varian_hilang = semua_varian - varian_tertangani
                    if varian_hilang:
                        nama_varian_hilang = ", ".join(sorted(list(varian_hilang)))
                        raise KesalahanPola(
                            node.ekspresi.token, # Token dari 'jodohkan'
                            f"Ekspresi 'jodohkan' tidak mencakup semua kemungkinan kasus. Kasus yang belum ditangani: {nama_varian_hilang}"
                        )
        # --- Akhir Logika Pengecekan ---

        for kasus in node.kasus:
            lingkungan_kasus = Lingkungan(induk=self.lingkungan)
            cocok, _ = await self._pola_cocok(kasus.pola, nilai_ekspresi, lingkungan_kasus)
            if cocok:
                # Jika ada 'jaga' (guard), evaluasi kondisinya
                if kasus.jaga:
                    nilai_jaga = await self._evaluasi_dalam_lingkungan(kasus.jaga, lingkungan_kasus)
                    # Jika kondisi jaga tidak benar, anggap tidak cocok dan lanjut ke kasus berikutnya
                    if not self._apakah_benar(nilai_jaga):
                        continue

                # Jika cocok dan jaga (jika ada) berhasil, eksekusi badan
                await self._eksekusi_blok(kasus.badan, lingkungan_kasus)
                return

    async def _evaluasi_dalam_lingkungan(self, ekspresi: ast.Xprs, lingkungan: Lingkungan):
        """Mengevaluasi ekspresi dalam lingkungan sementara."""
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan
        try:
            # Panggil _evaluasi, yang sudah memiliki error handling sendiri
            return await self._evaluasi(ekspresi)
        finally:
            # Pastikan lingkungan selalu dikembalikan ke keadaan semula
            self.lingkungan = lingkungan_sebelumnya

    async def _pola_cocok(self, pola: ast.Pola, nilai, lingkungan):
        if isinstance(pola, ast.PolaWildcard):
            return True, lingkungan
        if isinstance(pola, ast.PolaLiteral):
            nilai_pola = await self._evaluasi(pola.nilai)
            return nilai == nilai_pola, lingkungan
        if isinstance(pola, ast.PolaVarian):
            if not isinstance(nilai, InstansiVarian):
                return False, lingkungan
            if pola.nama.nilai != nilai.konstruktor.nama:
                return False, lingkungan
            if len(pola.daftar_ikatan) != len(nilai.argumen):
                raise KesalahanTipe(
                    pola.nama,
                    f"Pola '{pola.nama.nilai}' mengharapkan {len(pola.daftar_ikatan)} argumen, tapi varian memiliki {len(nilai.argumen)}."
                )
            for token_ikatan, nilai_argumen in zip(pola.daftar_ikatan, nilai.argumen):
                # Recursively match bindings, allowing for nested patterns in the future
                # For now, we assume simple variable or wildcard bindings
                if token_ikatan.nilai != '_':
                    lingkungan.definisi(token_ikatan.nilai, nilai_argumen)
            return True, lingkungan

        if isinstance(pola, ast.PolaIkatanVariabel):
            lingkungan.definisi(pola.token.nilai, nilai)
            return True, lingkungan

        if isinstance(pola, ast.PolaDaftar):
            if not isinstance(nilai, list):
                return False, lingkungan

            jumlah_pola_tetap = len(pola.daftar_pola)

            if pola.pola_sisa:
                # Logika untuk pola dengan sisa (...)
                if len(nilai) < jumlah_pola_tetap:
                    return False, lingkungan # Tidak cukup elemen untuk dicocokkan

                # Cocokkan bagian tetap
                for i in range(jumlah_pola_tetap):
                    cocok, _ = await self._pola_cocok(pola.daftar_pola[i], nilai[i], lingkungan)
                    if not cocok:
                        return False, lingkungan

                # Ikat sisa daftar ke variabel
                sisa_daftar = nilai[jumlah_pola_tetap:]
                lingkungan.definisi(pola.pola_sisa.nilai, sisa_daftar)
                return True, lingkungan
            else:
                # Logika untuk pola dengan jumlah elemen tetap
                if jumlah_pola_tetap != len(nilai):
                    return False, lingkungan

                for sub_pola, sub_nilai in zip(pola.daftar_pola, nilai):
                    cocok, _ = await self._pola_cocok(sub_pola, sub_nilai, lingkungan)
                    if not cocok:
                        return False, lingkungan # Jika ada yang tidak cocok, seluruh pola gagal
                return True, lingkungan

        return False, lingkungan

    async def _eksekusi_blok(self, blok_node: ast.Bagian, lingkungan_blok: Lingkungan):
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in blok_node.daftar_pernyataan:
                await self._eksekusi(pernyataan)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    def _ke_string(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, bool): return "benar" if obj else "salah"
        if isinstance(obj, str): return f'"{obj}"'
        if isinstance(obj, (Fungsi, MorphKelas, MorphInstance)):
            return str(obj)
        if isinstance(obj, list):
            return f"[{', '.join(self._ke_string(e) for e in obj)}]"
        if isinstance(obj, dict):
            pasangan = [f'{self._ke_string(k)}: {self._ke_string(v)}' for k, v in obj.items()]
            return f"{{{', '.join(pasangan)}}}"
        if isinstance(obj, InstansiVarian):
            if not obj.argumen:
                return obj.konstruktor.nama
            args_str = ', '.join(self._ke_string(arg) for arg in obj.argumen)
            return f"{obj.konstruktor.nama}({args_str})"
        return str(obj)

    def _apakah_benar(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _periksa_tipe_angka(self, operator, *operands):
        for operand in operands:
            if not isinstance(operand, (int, float)) or isinstance(operand, bool):
                raise KesalahanTipe(operator, "Operan harus berupa angka.")

def patch_ast_nodes():
    async def terima_async(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return await metode(self)
    ast.MRPH.terima_async = terima_async

    def terima_sync(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return metode(self)
    ast.MRPH.terima = terima_sync

patch_ast_nodes()
