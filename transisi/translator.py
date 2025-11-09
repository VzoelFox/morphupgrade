# transisi/translator.py
# Interpreter untuk "Kelahiran Kembali MORPH"

import os
import json
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token
from .kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama,
    KesalahanIndeks, KesalahanKunci, KesalahanPembagianNol
)
from .lx import Leksikal
from .crusher import Pengurai
from .modules import ModuleLoader

# Exception khusus untuk menangani alur kontrol 'kembalikan'
class NilaiKembalian(Exception):
    def __init__(self, nilai):
        self.nilai = nilai

class FungsiBawaan:
    """Wrapper untuk fungsi Python yang diekspos sebagai fungsi built-in MORPH."""
    def __init__(self, panggil_logic):
        self.panggil_logic = panggil_logic

    def __call__(self, argumen):
        return self.panggil_logic(argumen)

    def __str__(self):
        return "<fungsi bawaan>"

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
        if nama in self.nilai:
            return self.nilai[nama]
        if self.induk is not None:
            return self.induk.dapatkan(token)
        raise KesalahanNama(token, f"Variabel '{nama}' belum didefinisikan.")

    def tetapkan(self, token, nilai):
        nama = token.nilai
        if nama in self.nilai:
            if nama in self.konstanta:
                raise KesalahanRuntime(
                    token,
                    f"Tidak bisa mengubah konstanta '{nama}'. Variabel ini dideklarasikan dengan 'tetap'."
                )
            self.nilai[nama] = nilai
            return

        if self.induk is not None:
            self.induk.tetapkan(token, nilai)
            return
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

# Kelas untuk representasi fungsi saat runtime
class Fungsi:
    def __init__(self, deklarasi: ast.FungsiDeklarasi, penutup: Lingkungan):
        self.deklarasi = deklarasi
        self.penutup = penutup # Lingkungan tempat fungsi didefinisikan

    def __str__(self):
        return f"<fungsi {self.deklarasi.nama.nilai}>"

    def panggil(self, interpreter, node_panggil: ast.PanggilFungsi):
        argumen = [interpreter._evaluasi(arg) for arg in node_panggil.argumen]

        # Buat lingkungan baru untuk eksekusi fungsi
        lingkungan_fungsi = Lingkungan(induk=self.penutup)

        # Validasi jumlah argumen
        if len(argumen) != len(self.deklarasi.parameter):
            raise KesalahanTipe(
                node_panggil.token, # Gunakan token dari node pemanggil
                f"Jumlah argumen tidak cocok. Diharapkan {len(self.deklarasi.parameter)}, diterima {len(argumen)}."
            )

        # Ikat argumen ke parameter di lingkungan baru
        for param, arg in zip(self.deklarasi.parameter, argumen):
            lingkungan_fungsi.definisi(param.nilai, arg)

        # Tambahkan ke call stack
        interpreter.call_stack.append(f"fungsi '{self.deklarasi.nama.nilai}' dipanggil dari baris {node_panggil.token.baris}")

        # Eksekusi badan fungsi
        try:
            interpreter._eksekusi_blok(self.deklarasi.badan, lingkungan_fungsi)
        except KesalahanRuntime as e:
            # Lampirkan jejak panggilan saat ini ke pengecualian sebelum stack di-unwind
            # Hanya lampirkan sekali di frame terdalam
            if not hasattr(e, 'morph_stack'):
                e.morph_stack = list(interpreter.call_stack)
            raise
        except NilaiKembalian as e:
            return e.nilai
        finally:
            # Pastikan selalu keluar dari stack
            interpreter.call_stack.pop()

        # Fungsi yang tidak memiliki pernyataan 'kembalikan' akan mengembalikan 'nil'
        return None


class Penerjemah:
    """Visitor yang mengekusi AST."""
    def __init__(self, formatter):
        self.lingkungan_global = Lingkungan()
        self.lingkungan = self.lingkungan_global
        self.formatter = formatter
        self.call_stack = []
        self.current_file = None
        self.module_loader = ModuleLoader(self)

        # Daftarkan fungsi built-in
        self.lingkungan_global.definisi("baca_vzoel", FungsiBawaan(self._fungsi_baca_vzoel))

    def _fungsi_baca_vzoel(self, argumen):
        if len(argumen) != 1:
            raise KesalahanTipe(None, f"Fungsi 'baca_vzoel' memerlukan 1 argumen (path file), tetapi menerima {len(argumen)}.")

        path_file = argumen[0]
        if not isinstance(path_file, str):
            raise KesalahanTipe(None, f"Argumen untuk 'baca_vzoel' harus berupa teks (string) path file.")

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


    def terjemahkan(self, program: ast.Bagian, current_file: str | None = None):
        self.current_file = current_file
        # Reset lingkungan ke global setiap kali terjemahan baru dimulai
        self.lingkungan = self.lingkungan_global
        daftar_kesalahan = []
        try:
            for pernyataan in program.daftar_pernyataan:
                self._eksekusi(pernyataan)
        except KesalahanRuntime as e:
            stack_untuk_dilaporkan = getattr(e, 'morph_stack', self.call_stack)
            daftar_kesalahan.append(self.formatter.format_runtime(e, stack_untuk_dilaporkan))
        return daftar_kesalahan

    def _eksekusi(self, pernyataan: ast.St):
        return pernyataan.terima(self)

    def _evaluasi(self, ekspresi: ast.Xprs):
        return ekspresi.terima(self)

    # --- Visitor untuk Pernyataan (Statements) ---

    def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            self._eksekusi(pernyataan)

    def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        self._evaluasi(node.ekspresi)

    def kunjungi_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        nilai = None
        if node.nilai is not None:
            nilai = self._evaluasi(node.nilai)

        adalah_konstan = (node.jenis_deklarasi.tipe == TipeToken.TETAP)
        self.lingkungan.definisi(node.nama.nilai, nilai, adalah_konstan)

    def kunjungi_Tulis(self, node: ast.Tulis):
        output = []
        for arg in node.argumen:
            nilai = self._evaluasi(arg)
            output.append(self._ke_string(nilai))
        print(' '.join(output))

    def kunjungi_Assignment(self, node: ast.Assignment):
        nilai = self._evaluasi(node.nilai)
        target_node = node.nama

        # Jika target adalah akses indeks/kunci, tangani secara khusus
        if isinstance(target_node, ast.Akses):
            objek = self._evaluasi(target_node.objek)
            kunci = self._evaluasi(target_node.kunci)

            # Assignment untuk Daftar (list)
            if isinstance(objek, list):
                if not isinstance(kunci, int):
                    raise KesalahanTipe(target_node.kunci.token, "Indeks daftar harus berupa angka.")
                if 0 <= kunci < len(objek):
                    objek[kunci] = nilai
                    return nilai
                else:
                    raise KesalahanIndeks(target_node.objek.token, "Indeks di luar jangkauan.")

            # Assignment untuk Kamus (dictionary)
            if isinstance(objek, dict):
                if not isinstance(kunci, str):
                    raise KesalahanKunci(target_node.kunci.token, "Kunci kamus harus berupa teks.")
                objek[kunci] = nilai
                return nilai

            raise KesalahanTipe(target_node.objek.token, "Target assignment tidak valid. Hanya daftar dan kamus yang bisa diubah elemennya.")

        # Jika target adalah variabel biasa
        self.lingkungan.tetapkan(target_node, nilai)
        return nilai

    def kunjungi_TipeDeklarasi(self, node: ast.TipeDeklarasi):
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

    def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        fungsi = Fungsi(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)

    def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        nilai = None
        if node.nilai is not None:
            nilai = self._evaluasi(node.nilai)
        raise NilaiKembalian(nilai)

    def kunjungi_Selama(self, node: ast.Selama):
        while self._apakah_benar(self._evaluasi(node.kondisi)):
            self._eksekusi_blok(node.badan, Lingkungan(induk=self.lingkungan))

    def kunjungi_AmbilSemua(self, node: ast.AmbilSemua):
        exports = self.module_loader.load_module(node.path_file, self.current_file)

        if node.alias:
            # Varian: ambil_semua "..." sebagai mat
            # Buat kamus (dict) dari hasil ekspor
            self.lingkungan.definisi(node.alias.nilai, exports)
        else:
            # Varian: ambil_semua "..."
            # Masukkan semua simbol ke lingkungan saat ini
            for nama, nilai in exports.items():
                self.lingkungan.definisi(nama, nilai)

    def kunjungi_AmbilSebagian(self, node: ast.AmbilSebagian):
        exports = self.module_loader.load_module(node.path_file, self.current_file)

        for simbol_token in node.daftar_simbol:
            nama = simbol_token.nilai
            if nama not in exports:
                raise KesalahanNama(
                    simbol_token,
                    f"Simbol '{nama}' tidak ditemukan di modul '{node.path_file.nilai}'."
                )
            self.lingkungan.definisi(nama, exports[nama])

    # --- Metode Internal untuk Modul ---

    def _jalankan_modul(self, module_path: str):
        """Mengeksekusi file modul dan mengembalikan simbol-simbol yang diekspor."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except IOError:
            raise KesalahanRuntime(None, f"Tidak bisa membaca file modul: {module_path}")

        # Simpan state interpreter saat ini
        lingkungan_sebelumnya = self.lingkungan
        file_sebelumnya = self.current_file

        # Buat lingkungan terisolasi untuk modul
        lingkungan_modul = Lingkungan(induk=None)
        self.lingkungan = lingkungan_modul
        self.current_file = module_path

        try:
            # Proses Lexer & Parser untuk modul
            leksikal = Leksikal(source, f"modul '{os.path.basename(module_path)}'")
            tokens, daftar_kesalahan_lexer = leksikal.buat_token()
            if daftar_kesalahan_lexer:
                # Ambil kesalahan pertama untuk dilaporkan
                kesalahan = daftar_kesalahan_lexer[0]
                pesan_error = kesalahan.get("pesan", "Error tidak diketahui")
                # Buat token dummy untuk memberikan konteks ke formatter
                token_dummy = Token(
                    tipe=TipeToken.TIDAK_DIKENAL,
                    nilai=module_path,
                    baris=kesalahan.get("baris", 1),
                    kolom=kesalahan.get("kolom", 1)
                )
                raise KesalahanRuntime(token_dummy, f"Kesalahan leksikal di modul '{os.path.basename(module_path)}': {pesan_error}")

            parser = Pengurai(tokens)
            ast_modul = parser.urai()
            if parser.daftar_kesalahan:
                # Ambil kesalahan pertama untuk dilaporkan
                token_kesalahan, pesan = parser.daftar_kesalahan[0]
                raise KesalahanRuntime(token_kesalahan, f"Kesalahan sintaks di modul '{os.path.basename(module_path)}': {pesan}")

            # Eksekusi semua pernyataan di modul
            for pernyataan in ast_modul.daftar_pernyataan:
                self._eksekusi(pernyataan)

            # Kumpulkan hasil ekspor (simbol non-privat)
            exports = {}
            for nama, nilai in self.lingkungan.nilai.items():
                if not nama.startswith('_'):
                    exports[nama] = nilai

            return exports

        finally:
            # Kembalikan state interpreter ke kondisi semula
            self.lingkungan = lingkungan_sebelumnya
            self.current_file = file_sebelumnya


    # --- Visitor untuk Ekspresi (Expressions) ---

    def kunjungi_Kamus(self, node: ast.Kamus):
        kamus = {}
        for kunci_node, nilai_node in node.pasangan:
            kunci = self._evaluasi(kunci_node)
            if not isinstance(kunci, str):
                # Sesuai spesifikasi, kunci harus string untuk saat ini
                raise KesalahanKunci(kunci_node.token, "Kunci kamus harus berupa teks.")
            nilai = self._evaluasi(nilai_node)
            kamus[kunci] = nilai
        return kamus

    def kunjungi_Daftar(self, node: ast.Daftar):
        return [self._evaluasi(elem) for elem in node.elemen]

    def kunjungi_Akses(self, node: ast.Akses):
        objek = self._evaluasi(node.objek)
        kunci = self._evaluasi(node.kunci)

        # Akses untuk Daftar (list) dan Teks (string)
        if isinstance(objek, (list, str)):
            if not isinstance(kunci, int):
                raise KesalahanTipe(node.kunci.token, "Indeks untuk daftar atau teks harus berupa angka.")

            if 0 <= kunci < len(objek):
                return objek[kunci]
            else:
                raise KesalahanIndeks(node.kunci.token, "Indeks di luar jangkauan.")

        # Akses untuk Kamus (dictionary)
        if isinstance(objek, dict):
            if not isinstance(kunci, str):
                raise KesalahanKunci(node.kunci.token, "Kunci kamus harus berupa teks.")
            return objek.get(kunci, None) # Mengembalikan nil jika kunci tidak ada

        raise KesalahanTipe(node.objek.token, "Objek tidak dapat diakses menggunakan '[]'. Hanya berlaku untuk daftar, teks, dan kamus.")

    def kunjungi_Ambil(self, node: ast.Ambil):
        prompt_str = ""
        if node.prompt:
            prompt_evaluasi = self._evaluasi(node.prompt)
            prompt_str = self._ke_string(prompt_evaluasi)

        try:
            return input(prompt_str)
        except EOFError:
            return None # Kembalikan nil jika input diakhiri (misal: Ctrl+D)

    def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi):
        callee = self._evaluasi(node.callee)
        argumen = [self._evaluasi(arg) for arg in node.argumen]

        if isinstance(callee, Fungsi):
            # Ini adalah pemanggilan fungsi biasa
            # Fungsi.panggil() mengharapkan node, bukan argumen yang sudah dievaluasi
            return callee.panggil(self, node)

        if isinstance(callee, KonstruktorVarian):
            # Ini adalah instansiasi varian
            return callee(argumen, node.token)

        if isinstance(callee, FungsiBawaan):
            try:
                return callee(argumen)
            except KesalahanTipe as e:
                # Fungsi bawaan tidak punya token, jadi kita pinjam dari node pemanggil
                e.token = node.token
                raise e
            except KesalahanRuntime as e:
                e.token = node.token
                raise e

        raise KesalahanTipe(node.token, "Hanya fungsi atau konstruktor varian yang bisa dipanggil.")

    def kunjungi_Identitas(self, node: ast.Identitas):
        return self.lingkungan.dapatkan(node.token)

    def kunjungi_Konstanta(self, node: ast.Konstanta):
        return node.nilai

    def kunjungi_FoxUnary(self, node: ast.FoxUnary):
        kanan = self._evaluasi(node.kanan)

        if node.op.tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kanan)
            return -kanan
        if node.op.tipe == TipeToken.TIDAK:
            return not self._apakah_benar(kanan)

        return None # Harusnya tidak pernah terjadi

    def kunjungi_FoxBinary(self, node: ast.FoxBinary):
        op_tipe = node.op.tipe

        # Handle short-circuit operators FIRST
        if op_tipe == TipeToken.DAN:
            kiri = self._evaluasi(node.kiri)
            if not self._apakah_benar(kiri):
                return False  # Short-circuit!
            return self._apakah_benar(self._evaluasi(node.kanan))

        if op_tipe == TipeToken.ATAU:
            kiri = self._evaluasi(node.kiri)
            if self._apakah_benar(kiri):
                return kiri  # Short-circuit, return truthy value!
            return self._evaluasi(node.kanan)

        # Untuk operator lain, evaluasi kedua sisi dulu
        kiri = self._evaluasi(node.kiri)
        kanan = self._evaluasi(node.kanan)

        # Operasi Aritmatika
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

        # Operasi Perbandingan
        if op_tipe == TipeToken.LEBIH_DARI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri > kanan
        if op_tipe == TipeToken.KURANG_DARI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri < kanan
        if op_tipe == TipeToken.LEBIH_SAMA:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri >= kanan
        if op_tipe == TipeToken.KURANG_SAMA:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri <= kanan

        # Operasi Kesetaraan
        if op_tipe == TipeToken.SAMA_DENGAN:
            return kiri == kanan
        if op_tipe == TipeToken.TIDAK_SAMA:
            return kiri != kanan

        return None # Harusnya tidak pernah terjadi

    def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        if self._apakah_benar(self._evaluasi(node.kondisi)):
            self._eksekusi_blok(node.blok_maka, Lingkungan(induk=self.lingkungan))
        else:
            for kondisi_lain, blok_lain in node.rantai_lain_jika:
                if self._apakah_benar(self._evaluasi(kondisi_lain)):
                    self._eksekusi_blok(blok_lain, Lingkungan(induk=self.lingkungan))
                    return

            if node.blok_lain is not None:
                self._eksekusi_blok(node.blok_lain, Lingkungan(induk=self.lingkungan))

    def kunjungi_Pilih(self, node: ast.Pilih):
        nilai_ekspresi = self._evaluasi(node.ekspresi)

        kasus_cocok = False
        for kasus in node.kasus:
            nilai_kasus = self._evaluasi(kasus.nilai)
            if nilai_ekspresi == nilai_kasus:
                self._eksekusi_blok(kasus.badan, Lingkungan(induk=self.lingkungan))
                kasus_cocok = True
                break

        if not kasus_cocok and node.kasus_lainnya is not None:
            self._eksekusi_blok(node.kasus_lainnya.badan, Lingkungan(induk=self.lingkungan))

    def kunjungi_Jodohkan(self, node: ast.Jodohkan):
        nilai_ekspresi = self._evaluasi(node.ekspresi)

        for kasus in node.kasus:
            # Setiap kasus mendapatkan lingkungan baru untuk binding variabel
            lingkungan_kasus = Lingkungan(induk=self.lingkungan)
            cocok, _ = self._pola_cocok(kasus.pola, nilai_ekspresi, lingkungan_kasus)
            if cocok:
                self._eksekusi_blok(kasus.badan, lingkungan_kasus)
                return # Hanya satu kasus yang dieksekusi

    def _pola_cocok(self, pola: ast.Pola, nilai, lingkungan):
        if isinstance(pola, ast.PolaWildcard):
            return True, lingkungan

        if isinstance(pola, ast.PolaLiteral):
            nilai_pola = self._evaluasi(pola.nilai)
            return nilai == nilai_pola, lingkungan

        if isinstance(pola, ast.PolaVarian):
            # Periksa apakah nilai adalah instansi varian
            if not isinstance(nilai, InstansiVarian):
                return False, lingkungan

            # Periksa apakah nama konstruktor cocok
            if pola.nama.nilai != nilai.konstruktor.nama:
                return False, lingkungan

            # Periksa aritas (jumlah argumen/ikatan)
            if len(pola.daftar_ikatan) != len(nilai.argumen):
                raise KesalahanTipe(
                    pola.nama,
                    f"Pola '{pola.nama.nilai}' mengharapkan {len(pola.daftar_ikatan)} argumen, tapi varian memiliki {len(nilai.argumen)}."
                )

            # Lakukan binding
            for token_ikatan, nilai_argumen in zip(pola.daftar_ikatan, nilai.argumen):
                # Jangan bind wildcard '_'
                if token_ikatan.nilai != '_':
                    lingkungan.definisi(token_ikatan.nilai, nilai_argumen)

            return True, lingkungan

        return False, lingkungan

    def _eksekusi_blok(self, blok_node: ast.Bagian, lingkungan_blok: Lingkungan):
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in blok_node.daftar_pernyataan:
                self._eksekusi(pernyataan)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    # --- Helper Methods ---

    def _ke_string(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, bool): return "benar" if obj else "salah"
        if isinstance(obj, str): return f'"{obj}"' # Selalu apit string dengan kutip
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
        """Mendefinisikan 'truthiness' di MORPH."""
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _periksa_tipe_angka(self, operator, *operands):
        for operand in operands:
            # Boolean tidak dianggap sebagai angka dalam MORPH
            if not isinstance(operand, (int, float)) or isinstance(operand, bool):
                raise KesalahanTipe(operator, "Operan harus berupa angka.")

# --- Monkey-patching Visitor ke AST Nodes ---
# Ini adalah cara simpel untuk mengimplementasikan visitor pattern
# tanpa mengubah kelas-kelas AST itu sendiri.

def patch_ast_nodes():
    def terima(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            # Fallback untuk node yang belum diimplementasikan secara eksplisit
            # Ini akan mencegah crash tetapi tidak akan melakukan apa-apa
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return metode(self)

    ast.MRPH.terima = terima

patch_ast_nodes()
