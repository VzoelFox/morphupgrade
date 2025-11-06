# morph_engine/translator.py
# Changelog:
# - PATCH-020C: Menambahkan implementasi interpreter untuk `ambil()`.
# - PATCH-019F: Menambahkan batas waktu eksekusi yang dapat dikonfigurasi
#               melalui variabel lingkungan `MORPH_MAX_TIME` untuk mencegah
#               infinite loop.
# - PATCH-019E: Menyempurnakan pesan kesalahan dengan konteks tipe yang lebih
#               deskriptif dan dalam Bahasa Indonesia.
# - PATCH-019D: Menambahkan evaluasi untuk `NodeArray` untuk mendukung array literal.
# - PATCH-018: Implementasi closures (Fase 2B).
#              - Merombak manajemen environment dengan class `Lingkungan` dedicated.
#              - `Lingkungan` sekarang mendukung scope chaining (induk).
#              - `FungsiPengguna` menangkap environment saat didefinisikan (closure).
#              - Panggilan fungsi sekarang membuat environment eksekusi yang benar.
# - PATCH-017: Menambahkan dukungan rekursi dan penanganan stack overflow.
#              - Menambahkan `RECURSION_LIMIT` untuk mencegah rekursi tak terbatas.
#              - Melacak kedalaman rekursi di `kunjungi_PanggilFungsi`.
#              - Melemparkan `KesalahanRuntime` dengan pesan yang jelas saat limit terlampaui.
# - PATCH-016: Implementasi user-defined functions.
#              - Menambahkan objek runtime FungsiPengguna dan NilaiNil.
#              - Menangani deklarasi, pemanggilan, scope, dan nilai kembalian.
#              - Mengimplementasikan function hoisting.
# - PATCH-005: Sentralisasi validasi fungsi built-in via Registry Pattern.
# - PATCH-004A: Standardisasi pesan error runtime via helper `_buat_kesalahan`.
# - PATCH-012B: Implementasi fungsi bawaan `jumlah()`.
#              - Mendukung multi-argumen numerik (int/float).
#              - Validasi tipe argumen yang ketat.
#              - Mengembalikan 0 jika tanpa argumen.
# - PATCH-012A: Memperbaiki validasi argumen untuk fungsi `panjang`.
#              - Memastikan pesan error spesifik saat jumlah argumen salah.
# - PATCH-011: Membangun fondasi untuk manajemen scope.
#              - `tabel_simbol` diubah menjadi stack of dictionaries (`[{}]`).
#              - Logika pencarian, deklarasi, dan assignment diubah untuk mendukung scope.
#              - Menambahkan method `masuk_scope` dan `keluar_scope` untuk masa depan.
# - PATCH-009: Menambahkan pencegahan deklarasi variabel duplikat.
#              - Class `Simbol` sekarang menyimpan token deklarasi.
#              - `kunjungi_DeklarasiVariabel` melempar error jika variabel sudah ada.
# - PATCH-010: Menambahkan metode `kunjungi_Assignment` untuk menangani
#              logika assignment.
#              - Memisahkan logika deklarasi murni di `kunjungi_DeklarasiVariabel`.
#              - Memperbaiki pesan error untuk assignment ke var yang belum ada.
import os
import time
import importlib
from .absolute_sntx_morph import *
from .morph_t import TipeToken, Token
from .error_utils import ErrorFormatter
from .lx import Leksikal
from .crusher import Pengurai

# Batas rekursi kustom. Harus jauh di bawah batas rekursi Python,
# karena setiap pemanggilan fungsi Morph menggunakan beberapa frame stack Python.
RECURSION_LIMIT = int(os.getenv('MORPH_MAX_RECURSION', 150))
MAX_EXECUTION_TIME = int(os.getenv('MORPH_MAX_TIME', 30))

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2): return levenshtein_distance(s2, s1)
    if len(s2) == 0: return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions, deletions = previous_row[j + 1] + 1, current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class KesalahanRuntime(Exception):
    """
    Exception kustom untuk kesalahan saat runtime.
    Sekarang hanya menyimpan pesan yang sudah diformat dan node terkait.
    """
    def __init__(self, pesan, node):
        super().__init__(pesan)
        self.node = node

class KembalikanNilaiException(Exception):
    """
    Exception khusus yang digunakan untuk mengimplementasikan pernyataan 'kembalikan'.
    Ini bukan error, melainkan mekanisme kontrol alur.
    """
    def __init__(self, nilai):
        super().__init__("Ini bukan error, hanya sinyal pengembalian nilai.")
        self.nilai = nilai

class FungsiPengguna:
    def __init__(self, deklarasi_node, lingkungan_penutupan):
        self.deklarasi_node = deklarasi_node
        self.lingkungan_penutupan = lingkungan_penutupan

    def __str__(self):
        nama_fungsi = self.deklarasi_node.nama_fungsi.nilai
        return f"<fungsi {nama_fungsi}>"

class NilaiNil:
    """Kelas singleton untuk merepresentasikan nilai 'nil'."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NilaiNil, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return "nil"

NIL_INSTANCE = NilaiNil()

class ObjekPinjaman:
    """Membungkus objek Python mentah untuk digunakan di dalam MORPH."""
    def __init__(self, objek_python):
        self.objek_python = objek_python

    def __str__(self):
        try:
            # Coba repr() untuk output yang seringkali lebih informatif
            repr_str = repr(self.objek_python)
            if len(repr_str) > 100:
                return f"<objek pinjaman: {type(self.objek_python).__name__}>"
            return f"<objek pinjaman: {repr_str}>"
        except Exception:
            # Fallback jika repr() gagal
            return f"<objek pinjaman: {type(self.objek_python).__name__}>"

class Lingkungan:
    """Mewakili satu scope dan menautkannya ke scope induk."""
    def __init__(self, induk=None):
        self.simbols = {}
        self.induk = induk

    def definisikan(self, nama, simbol):
        """Mendefinisikan variabel baru di scope saat ini."""
        self.simbols[nama] = simbol

    def dapatkan(self, nama):
        """Mencari simbol secara iteratif di scope ini dan semua scope induk."""
        lingkungan = self
        while lingkungan:
            if nama in lingkungan.simbols:
                return lingkungan.simbols[nama]
            lingkungan = lingkungan.induk
        return None

    def ada_di_scope_ini(self, nama):
        """Memeriksa apakah sebuah simbol ada di scope saat ini saja."""
        return nama in self.simbols

class Simbol:
    def __init__(self, nilai, tipe_deklarasi, token_deklarasi):
        self.nilai = nilai
        self.tipe_deklarasi = tipe_deklarasi
        self.token_deklarasi = token_deklarasi

class PengunjungNode:
    def kunjungi(self, node):
        if hasattr(self, 'start_time') and self.start_time and (time.time() - self.start_time) > MAX_EXECUTION_TIME:
            pesan = f"Sang waktu tak lagi berpihak, kidung kodemu terhenti setelah berkelana selama {MAX_EXECUTION_TIME} detik."
            raise self._buat_kesalahan(node, pesan)
        nama_metode = f'kunjungi_{type(node).__name__}'
        pengunjung = getattr(self, nama_metode, self.kunjungan_umum)
        return pengunjung(node)

    def kunjungan_umum(self, node):
        raise Exception(f'Tidak ada metode kunjungi_{type(node).__name__}')

REGISTRI_FUNGSI_BAWAAN = {
    'tulis': {
        'min_args': 0,
        'max_args': None,
        'tipe_args': None,
        'handler': lambda args: print(" ".join(map(lambda a: "nil" if isinstance(a, NilaiNil) else (str(a) if not isinstance(a, dict) else f"kamus({len(a)})"), args)))
    },
    'panjang': {
        'min_args': 1,
        'max_args': 1,
        'tipe_args': [str],
        'handler': lambda args: len(args[0])
    },
    'jumlah': {
        'min_args': 0,
        'max_args': None,
        'tipe_args': [(int, float)],
        'handler': lambda args: sum(args) if args else 0
    }
}

class Translator(PengunjungNode):
    def __init__(self, ast, file_path=None):
        self.ast = ast
        self.lingkungan = self._buat_lingkungan_global()
        self.recursion_depth = 0
        self.start_time = None
        self.file_path = file_path # Path dari file yang sedang dieksekusi
        self.modul_tercache = {} # Cache untuk modul yang sudah diimpor
        self.tumpukan_impor = set() # Untuk deteksi impor sirkular

    def _buat_lingkungan_global(self):
        lingkungan = Lingkungan()
        for nama_fungsi, aturan in REGISTRI_FUNGSI_BAWAAN.items():
            # Membungkus handler dalam objek FungsiBawaan atau yang serupa
            # Untuk saat ini, kita akan menyimpan handler mentah
            simbol = Simbol(aturan['handler'], TipeToken.FUNGSI, Token(TipeToken.FUNGSI, nama_fungsi))
            lingkungan.definisikan(nama_fungsi, simbol)
        return lingkungan

    def _infer_type(self, nilai):
        """Mengembalikan nama tipe user-friendly dalam Bahasa Indonesia"""
        if isinstance(nilai, NilaiNil): return "nil"
        if isinstance(nilai, bool): return "boolean"
        if isinstance(nilai, int): return "angka bulat"
        if isinstance(nilai, float): return "angka desimal"
        if isinstance(nilai, str): return "teks"
        if isinstance(nilai, list): return "array"
        if isinstance(nilai, dict): return "kamus"
        if isinstance(nilai, FungsiPengguna): return "fungsi"
        if isinstance(nilai, ObjekPinjaman): return f"objek pinjaman ({type(nilai.objek_python).__name__})"
        return "tidak dikenal"

    def _konversi_ke_python(self, nilai_morph):
        """Mengonversi nilai MORPH ke nilai Python yang setara secara rekursif."""
        if isinstance(nilai_morph, list):
            return [self._konversi_ke_python(item) for item in nilai_morph]
        if isinstance(nilai_morph, dict):
            return {self._konversi_ke_python(k): self._konversi_ke_python(v) for k, v in nilai_morph.items()}

        if isinstance(nilai_morph, (int, float, str, bool)):
            return nilai_morph
        if isinstance(nilai_morph, NilaiNil):
            return None
        if isinstance(nilai_morph, ObjekPinjaman):
            return nilai_morph.objek_python

        # FungsiPengguna dan tipe lainnya tidak dapat dikonversi
        pesan = f"Sebuah '{self._infer_type(nilai_morph)}' tak dapat menyeberangi jembatan ke dunia Python."
        raise TypeError(pesan)

    def _konversi_dari_python(self, nilai_python):
        """Mengonversi nilai Python ke nilai MORPH yang setara secara rekursif."""
        if isinstance(nilai_python, (int, float, str, bool)):
            return nilai_python
        if nilai_python is None:
            return NIL_INSTANCE

        # Hanya tipe primitif yang tidak dapat diubah yang dilewatkan secara langsung.
        # Semua yang lain (list, dict, tuple, set, objek) dibungkus.
        if isinstance(nilai_python, (int, float, str, bool)):
            return nilai_python

        return ObjekPinjaman(nilai_python)

    def _buat_kesalahan(self, node, pesan):
        """Helper terpusat untuk membuat instance KesalahanRuntime."""
        token = None
        # Mencoba mengekstrak token yang paling relevan dari node untuk info baris/kolom
        if hasattr(node, 'nama_variabel') and hasattr(node.nama_variabel, 'token'):
            token = node.nama_variabel.token
        elif hasattr(node, 'nama_fungsi') and hasattr(node.nama_fungsi, 'token'):
            token = node.nama_fungsi.token
        elif hasattr(node, 'op'):
            token = node.op
        elif hasattr(node, 'token'):
            token = node.token

        if token:
            pesan_lengkap = ErrorFormatter.format_runtime_error(token, pesan)
        else:
            pesan_lengkap = f"Kesalahan Runtime: {pesan}"

        return KesalahanRuntime(pesan_lengkap, node)

    def _cek_kebenaran(self, nilai):
        """Mengevaluasi nilai kebenaran sesuai aturan Morph."""
        if isinstance(nilai, bool):
            return nilai
        # Aturan 'strict boolean' bisa ditambahkan di sini jika diperlukan
        return bool(nilai)

    def _eksekusi_blok(self, daftar_pernyataan):
        """Membuat scope baru, mengeksekusi blok, dan mengembalikan ke scope lama."""
        lingkungan_blok = Lingkungan(induk=self.lingkungan)
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in daftar_pernyataan:
                self.kunjungi(pernyataan)
        except KembalikanNilaiException:
            # Jika ada 'kembalikan', kita harus meneruskannya ke atas
            raise
        finally:
            self.lingkungan = lingkungan_sebelumnya

    def _validasi_panggilan_fungsi(self, nama_fungsi, argumen, aturan, node):
        # Validasi jumlah argumen
        jumlah_arg = len(argumen)
        if aturan['min_args'] is not None and jumlah_arg < aturan['min_args']:
            pesan = f"Syair '{nama_fungsi}' berbisik, memanggil setidaknya {aturan['min_args']} jiwa, namun hanya {jumlah_arg} yang datang."
            raise self._buat_kesalahan(node, pesan)
        if aturan['max_args'] is not None and jumlah_arg > aturan['max_args']:
            pesan = f"Panggung '{nama_fungsi}' hanya cukup untuk {aturan['max_args']} penampil, tetapi {jumlah_arg} mencoba naik."
            raise self._buat_kesalahan(node, pesan)

        # Validasi tipe argumen
        if aturan['tipe_args']:
            # Jika tipe_args adalah list, berarti setiap argumen bisa punya tipe berbeda
            if isinstance(aturan['tipe_args'], list) and len(aturan['tipe_args']) == jumlah_arg:
                for i, (arg, tipe_diharapkan) in enumerate(zip(argumen, aturan['tipe_args'])):
                    if not isinstance(arg, tipe_diharapkan):
                        tipe_asli = self._infer_type(arg)
                        pesan = f"Pada panggilan '{nama_fungsi}', argumen ke-{i+1} seharusnya berwujud '{tipe_diharapkan.__name__}', bukan '{tipe_asli}'."
                        raise self._buat_kesalahan(node, pesan)
            # Jika tipe_args adalah tuple, berarti semua argumen harus salah satu dari tipe tsb
            elif isinstance(aturan['tipe_args'], list) and isinstance(aturan['tipe_args'][0], tuple):
                tipe_diharapkan = aturan['tipe_args'][0]
                for i, arg in enumerate(argumen):
                    if not isinstance(arg, tipe_diharapkan):
                        tipe_asli = self._infer_type(arg)
                        pesan = f"Dalam simfoni '{nama_fungsi}', argumen ke-{i+1} menyumbang nada sumbang berjenis '{tipe_asli}', padahal hanya harmoni angka yang dinanti."
                        raise self._buat_kesalahan(node, pesan)

    def kunjungi_Bagian(self, node):
        # Lintasan 1: Daftarkan semua fungsi (hoisting)
        for pernyataan in node.daftar_pernyataan:
            if isinstance(pernyataan, FungsiDeklarasi):
                self.kunjungi(pernyataan)

        # Lintasan 2: Eksekusi kode lainnya
        for pernyataan in node.daftar_pernyataan:
            if not isinstance(pernyataan, FungsiDeklarasi):
                self.kunjungi(pernyataan)

    def kunjungi_DeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai

        if self.lingkungan.ada_di_scope_ini(nama_var):
            simbol_lama = self.lingkungan.dapatkan(nama_var)
            pesan = f"Nama '{nama_var}' telah terukir dalam takdir di baris {simbol_lama.token_deklarasi.baris}, tak bisa ditulis ulang dalam bait yang sama."
            raise self._buat_kesalahan(node, pesan)

        nilai_var = self.kunjungi(node.nilai)
        tipe_deklarasi = node.jenis_deklarasi.tipe
        token_deklarasi = node.nama_variabel.token
        simbol = Simbol(nilai_var, tipe_deklarasi, token_deklarasi)
        self.lingkungan.definisikan(nama_var, simbol)

    def kunjungi_Assignment(self, node):
        nilai_kanan = self.kunjungi(node.nilai)
        nilai_kanan_python = self._konversi_ke_python(nilai_kanan)

        # Cek apakah ini assignment ke member objek pinjaman
        if isinstance(node.nama_variabel, (Akses, AksesTitik)):
            akses_node = node.nama_variabel
            sumber = self.kunjungi(akses_node.sumber)

            if isinstance(sumber, ObjekPinjaman):
                objek_python = sumber.objek_python
                try:
                    if isinstance(akses_node, AksesTitik):
                        nama_properti = akses_node.properti.nilai
                        setattr(objek_python, nama_properti, nilai_kanan_python)
                    else: # Akses
                        kunci = self.kunjungi(akses_node.kunci)
                        kunci_python = self._konversi_ke_python(kunci)
                        objek_python[kunci_python] = nilai_kanan_python
                    return
                except Exception as e:
                    pesan = f"Dunia pinjaman menolak perubahan ini. Bisikan dari seberang: {e}"
                    raise self._buat_kesalahan(akses_node, pesan)

        # Cek apakah ini adalah assignment ke member kamus/array
        if isinstance(node.nama_variabel, Akses):
            akses_node = node.nama_variabel
            sumber = self.kunjungi(akses_node.sumber)
            kunci = self.kunjungi(akses_node.kunci)
            nilai_baru = self.kunjungi(node.nilai)

            if isinstance(sumber, dict):
                if not isinstance(kunci, (str, int, float, bool)):
                    pesan = f"Kunci untuk membuka peti harta karun (kamus) haruslah sederhana, bukan sebuah '{self._infer_type(kunci)}'."
                    raise self._buat_kesalahan(akses_node.kunci, pesan)
                sumber[kunci] = nilai_baru
                return
            elif isinstance(sumber, list):
                if not isinstance(kunci, int):
                    pesan = f"Untuk meniti barisan (array), langkahmu haruslah berupa 'angka bulat', bukan '{self._infer_type(kunci)}'."
                    raise self._buat_kesalahan(akses_node.kunci, pesan)
                if 0 <= kunci < len(sumber):
                    sumber[kunci] = nilai_baru
                else:
                    pesan = f"Langkahmu terlalu jauh. Jejak {kunci} tak ditemukan dalam barisan sepanjang {len(sumber)}."
                    raise self._buat_kesalahan(akses_node.kunci, pesan)
                return
            else:
                pesan = f"'{self._infer_type(sumber)}' adalah benda padat, tak bisa diukir isinya."
                raise self._buat_kesalahan(akses_node.sumber, pesan)

        # Logika assignment variabel biasa
        nama_var = node.nama_variabel.nilai
        simbol = self.lingkungan.dapatkan(nama_var)

        if simbol is None:
            semua_simbol_terlihat = set()
            lingkungan_cek = self.lingkungan
            while lingkungan_cek:
                semua_simbol_terlihat.update(lingkungan_cek.simbols.keys())
                lingkungan_cek = lingkungan_cek.induk

            saran_terdekat = None
            jarak_terkecil = 3
            for nama_simbol in semua_simbol_terlihat:
                jarak = levenshtein_distance(nama_var, nama_simbol)
                if jarak < jarak_terkecil:
                    jarak_terkecil, saran_terdekat = jarak, nama_simbol

            pesan = f"Penyair mencari '{nama_var}', namun takdirnya belum tertulis. Coba bisikkan 'biar {nama_var} = ...' untuk memberinya makna."
            if saran_terdekat:
                pesan += f"\nAtau mungkin, yang kau cari adalah sang bintang '{saran_terdekat}'?"
            raise self._buat_kesalahan(node, pesan)

        if simbol.tipe_deklarasi == TipeToken.TETAP:
            pesan = f"'{nama_var}' adalah bintang tetap di angkasa, cahayanya tak dapat diubah."
            raise self._buat_kesalahan(node, pesan)

        nilai_var = self.kunjungi(node.nilai)
        simbol.nilai = nilai_var

    def kunjungi_PanggilFungsi(self, node):
        self.recursion_depth += 1
        try:
            # 1. Periksa batas rekursi SEGERA
            if self.recursion_depth > RECURSION_LIMIT:
                nama_fungsi_str = getattr(node.nama_fungsi, 'nilai', '<fungsi dinamis>')
                pesan = f"Fungsi '{nama_fungsi_str}' terjebak dalam pusaran rekursi yang tak berujung. Batasan kedalaman {RECURSION_LIMIT} telah terlampaui."
                raise self._buat_kesalahan(node, pesan)

            # 2. Evaluasi node pemanggil untuk mendapatkan objek fungsi
            #    Ini menangani kasus seperti `fungsi()` dan `modul["fungsi"]()`
            pemanggil = self.kunjungi(node.nama_fungsi)

            # 3. Evaluasi semua argumen terlebih dahulu
            argumen = [self.kunjungi(arg) for arg in node.daftar_argumen]

            # Periksa apakah itu fungsi bawaan (berdasarkan nama)
            if isinstance(node.nama_fungsi, Identitas):
                 nama_fungsi_str = node.nama_fungsi.nilai
                 simbol = self.lingkungan.dapatkan(nama_fungsi_str)
                 if simbol and callable(simbol.nilai) and not isinstance(simbol.nilai, FungsiPengguna):
                     aturan = REGISTRI_FUNGSI_BAWAAN[nama_fungsi_str]
                     self._validasi_panggilan_fungsi(nama_fungsi_str, argumen, aturan, node)
                     return simbol.nilai(argumen)

            # 4. Periksa apakah pemanggil adalah FungsiPengguna
            if isinstance(pemanggil, ObjekPinjaman):
                fungsi_python = pemanggil.objek_python
                if not callable(fungsi_python):
                    pesan = "Benda pinjaman ini membisu, tak bisa menyanyikan lagu yang kau minta."
                    raise self._buat_kesalahan(node, pesan)

                try:
                    argumen_python = [self._konversi_ke_python(arg) for arg in argumen]
                    hasil_python = fungsi_python(*argumen_python)
                    return self._konversi_dari_python(hasil_python)
                except Exception as e:
                    # Menangkap semua kesalahan dari sisi Python dan melaporkannya
                    pesan = f"Dunia pinjaman bergejolak. Bisikan dari seberang: {e}"
                    raise self._buat_kesalahan(node, pesan)

            elif isinstance(pemanggil, FungsiPengguna):
                fungsi_obj = pemanggil
                nama_fungsi = fungsi_obj.deklarasi_node.nama_fungsi.nilai
                deklarasi = fungsi_obj.deklarasi_node

                # 5. Validasi jumlah argumen (arity check)
                if len(argumen) != len(deklarasi.parameter):
                    pesan = f"Syair '{nama_fungsi}' memanggil {len(deklarasi.parameter)} jiwa, namun {len(argumen)} yang menjawab."
                    raise self._buat_kesalahan(node, pesan)
            else:
                nama_pemanggil_str = self._infer_type(pemanggil)
                pesan = f"Hanya syair dan mantra yang bisa dirapalkan, bukan sebuah '{nama_pemanggil_str}'."
                raise self._buat_kesalahan(node, pesan)

            # 6. Siapkan scope baru dan eksekusi fungsi
            # Ini adalah dasar dari closure: scope baru ditautkan ke
            # lingkungan penutupan fungsi, bukan lingkungan pemanggil.
            lingkungan_eksekusi = Lingkungan(induk=fungsi_obj.lingkungan_penutupan)

            # Ikat nilai argumen ke nama parameter di scope baru
            for param_node, arg_nilai in zip(deklarasi.parameter, argumen):
                nama_param = param_node.nilai
                simbol_param = Simbol(arg_nilai, TipeToken.BIAR, param_node.token)
                lingkungan_eksekusi.definisikan(nama_param, simbol_param)

            # Simpan lingkungan saat ini dan beralih ke lingkungan eksekusi fungsi
            lingkungan_sebelumnya = self.lingkungan
            self.lingkungan = lingkungan_eksekusi

            try:
                # Eksekusi badan fungsi menggunakan helper untuk manajemen scope
                self._eksekusi_blok(deklarasi.badan)
            except KembalikanNilaiException as e:
                return e.nilai  # Nilai kembalian yang diharapkan
            finally:
                # Pastikan lingkungan selalu dipulihkan
                self.lingkungan = lingkungan_sebelumnya

            # Kembalikan 'nil' secara implisit jika tidak ada 'kembalikan' yang dieksekusi
            return NIL_INSTANCE

        finally:
            # Pastikan depth counter selalu di-decrement, tidak peduli apa yang terjadi
            self.recursion_depth -= 1

    def kunjungi_Identitas(self, node):
        nama_var = node.nilai
        simbol = self.lingkungan.dapatkan(nama_var)
        if simbol is None:
            semua_simbol_terlihat = set()
            lingkungan_cek = self.lingkungan
            while lingkungan_cek:
                semua_simbol_terlihat.update(lingkungan_cek.simbols.keys())
                lingkungan_cek = lingkungan_cek.induk

            saran_terdekat = None
            jarak_terkecil = 3
            for nama_simbol in semua_simbol_terlihat:
                jarak = levenshtein_distance(nama_var, nama_simbol)
                if jarak < jarak_terkecil:
                    jarak_terkecil, saran_terdekat = jarak, nama_simbol

            pesan = f"Penyair mencari makna '{nama_var}', namun tak ditemukannya dalam bait ini."
            if saran_terdekat:
                pesan += f"\nAtau mungkin, yang kau cari adalah sang bintang '{saran_terdekat}'?"
            raise self._buat_kesalahan(node, pesan)
        return simbol.nilai

    def kunjungi_Konstanta(self, node):
        return node.nilai

    def kunjungi_Daftar(self, node):
        return [self.kunjungi(elem) for elem in node.elemen]

    def kunjungi_Ambil(self, node):
        """Menangani logika untuk mengimpor modul MORPH."""
        path_modul_relatif = self.kunjungi(node.path_modul)

        if not self.file_path:
            pesan = "Penyair tak tahu arah pulang, tak bisa memanggil lembaran baru tanpa tahu di mana ia berdiri."
            raise self._buat_kesalahan(node, pesan)

        # Selesaikan path absolut dari modul
        base_dir = os.path.dirname(os.path.abspath(self.file_path))
        path_modul_absolut = os.path.abspath(os.path.join(base_dir, path_modul_relatif))

        # 1. Deteksi Impor Sirkular
        if path_modul_absolut in self.tumpukan_impor:
            pesan = f"Sebuah lingkaran sihir terdeteksi. Lembaran '{path_modul_relatif}' mencoba memanggil dirinya sendiri dalam sebuah gema tak berujung."
            raise self._buat_kesalahan(node, pesan)

        # 2. Gunakan Cache jika tersedia
        if path_modul_absolut in self.modul_tercache:
            lingkungan_modul = self.modul_tercache[path_modul_absolut]
        else:
            # 3. Muat dan eksekusi modul
            try:
                with open(path_modul_absolut, 'r', encoding='utf-8') as f:
                    kode_modul = f.read()
            except FileNotFoundError:
                pesan = f"Di cakrawala '{path_modul_relatif}', lembaran yang kau cari tak nampak."
                raise self._buat_kesalahan(node, pesan)

            self.tumpukan_impor.add(path_modul_absolut)

            # Buat instance baru untuk menginterpretasikan modul secara terisolasi
            leksikal_modul = Leksikal(kode_modul)
            token_modul = leksikal_modul.buat_token()
            pengurai_modul = Pengurai(token_modul)
            ast_modul = pengurai_modul.urai()

            penerjemah_modul = Translator(ast_modul, file_path=path_modul_absolut)
            # Bagikan cache agar semua impor menggunakan cache yang sama
            penerjemah_modul.modul_tercache = self.modul_tercache
            penerjemah_modul.interpretasi()

            lingkungan_modul = penerjemah_modul.lingkungan
            self.modul_tercache[path_modul_absolut] = lingkungan_modul

            self.tumpukan_impor.remove(path_modul_absolut)

        # 4. Gabungkan simbol ke lingkungan saat ini
        if node.alias: # Kasus: ambil_semua "modul" sebagai m
            # Buat objek sederhana (kamus) untuk namespace
            namespace_obj = {}
            for nama, simbol in lingkungan_modul.simbols.items():
                namespace_obj[nama] = simbol.nilai

            simbol_alias = Simbol(namespace_obj, TipeToken.TETAP, node.alias.token)
            self.lingkungan.definisikan(node.alias.nilai, simbol_alias)

        elif node.daftar_nama: # Kasus: ambil_sebagian a, b dari "modul"
            for nama_node in node.daftar_nama:
                nama_simbol = nama_node.nilai
                simbol = lingkungan_modul.dapatkan(nama_simbol)
                if not simbol:
                    pesan = f"Dari lembaran '{path_modul_relatif}', nama '{nama_simbol}' tak ditemukan dalam daftar mantra."
                    raise self._buat_kesalahan(nama_node, pesan)
                self.lingkungan.definisikan(nama_simbol, simbol)

        else: # Kasus: ambil_semua "modul"
            for nama, simbol in lingkungan_modul.simbols.items():
                if self.lingkungan.ada_di_scope_ini(nama):
                    # Untuk saat ini, lewati konflik untuk mencegah penimpaan yang tidak disengaja
                    continue
                self.lingkungan.definisikan(nama, simbol)

        return NIL_INSTANCE

    def kunjungi_Pinjam(self, node):
        """Memuat modul Python dari path dan menyimpannya sebagai ObjekPinjaman."""
        path_modul_relatif = self.kunjungi(node.path_modul)
        nama_alias = node.alias.nilai

        if not self.file_path:
            pesan = "Penyair tak tahu arah pulang, tak bisa meminjam pusaka dari dunia seberang."
            raise self._buat_kesalahan(node, pesan)

        base_dir = os.path.dirname(os.path.abspath(self.file_path))
        path_modul_absolut = os.path.abspath(os.path.join(base_dir, path_modul_relatif))

        try:
            # Menggunakan importlib untuk memuat modul Python dari path
            nama_modul = os.path.splitext(os.path.basename(path_modul_absolut))[0]
            spec = importlib.util.spec_from_file_location(nama_modul, path_modul_absolut)
            if spec is None:
                raise FileNotFoundError

            modul_python = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul_python)

            # Bungkus modul yang dimuat ke dalam ObjekPinjaman
            objek_pinjaman = ObjekPinjaman(modul_python)
            simbol = Simbol(objek_pinjaman, TipeToken.TETAP, node.alias.token)
            self.lingkungan.definisikan(nama_alias, simbol)

        except FileNotFoundError:
            pesan = f"Pusaka dari '{path_modul_relatif}' tak ditemukan dalam perjalanan ke dunia seberang."
            raise self._buat_kesalahan(node, pesan)
        except Exception as e:
            # Menangkap kesalahan saat memuat atau mengeksekusi modul Python
            pesan = f"Gerbang ke dunia pinjaman '{path_modul_relatif}' terkunci rapat. Bisikan dari seberang: {e}"
            raise self._buat_kesalahan(node, pesan)

        return NIL_INSTANCE

    def kunjungi_Kamus(self, node):
        """Evaluasi literal kamus menjadi Python dict."""
        kamus_hasil = {}
        for node_kunci, node_nilai in node.pasangan:
            kunci = self.kunjungi(node_kunci)
            # Validasi bahwa kunci adalah tipe yang dapat di-hash
            if not isinstance(kunci, (str, int, float, bool)):
                pesan = f"Kunci untuk membuka peti harta karun (kamus) haruslah sederhana, bukan sebuah '{self._infer_type(kunci)}'."
                raise self._buat_kesalahan(node_kunci, pesan)
            nilai = self.kunjungi(node_nilai)
            kamus_hasil[kunci] = nilai
        return kamus_hasil

    def kunjungi_ambil(self, node):
        """Menangani fungsi bawaan ambil() untuk input pengguna."""
        prompt_text = ""
        if node.prompt_node:
            prompt_text = self.kunjungi(node.prompt_node)
            if not isinstance(prompt_text, str):
                tipe_prompt = self._infer_type(prompt_text)
                pesan = f"Bisikan untuk 'ambil' haruslah berupa 'teks', bukan '{tipe_prompt}'."
                raise self._buat_kesalahan(node.prompt_node, pesan)

        try:
            user_input = input(prompt_text)
            return user_input
        except EOFError:
            return "" # Sesuai spesifikasi, kembalikan string kosong saat EOF

    def kunjungi_Akses(self, node):
        """Mengevaluasi akses member pada kamus atau array."""
        sumber = self.kunjungi(node.sumber)
        kunci = self.kunjungi(node.kunci)

        if isinstance(sumber, ObjekPinjaman):
            # Coba lakukan __getitem__ pada objek Python yang dibungkus
            try:
                hasil_python = sumber.objek_python[self._konversi_ke_python(kunci)]
                return self._konversi_dari_python(hasil_python)
            except Exception as e:
                pesan = f"Benda pinjaman ini tak mau dibuka kuncinya. Bisikan dari seberang: {e}"
                raise self._buat_kesalahan(node, pesan)

        if isinstance(sumber, dict):
            # Akses kamus
            if not isinstance(kunci, (str, int, float, bool)):
                pesan = f"Kunci untuk membuka peti harta karun (kamus) haruslah sederhana, bukan sebuah '{self._infer_type(kunci)}'."
                raise self._buat_kesalahan(node.kunci, pesan)
            return sumber.get(kunci, NIL_INSTANCE)
        elif isinstance(sumber, list):
            # Akses array
            if not isinstance(kunci, int):
                pesan = f"Untuk meniti barisan (array), langkahmu haruslah berupa 'angka bulat', bukan '{self._infer_type(kunci)}'."
                raise self._buat_kesalahan(node.kunci, pesan)
            if 0 <= kunci < len(sumber):
                return sumber[kunci]
            else:
                # Sesuai konvensi, akses di luar batas mengembalikan nil
                return NIL_INSTANCE
        else:
            pesan = f"'{self._infer_type(sumber)}' adalah benda padat, tak bisa dibuka isinya dengan kunci '[...]'."
            raise self._buat_kesalahan(node.sumber, pesan)

    def kunjungi_AksesTitik(self, node):
        """Mengevaluasi akses properti dengan notasi titik pada ObjekPinjaman."""
        sumber = self.kunjungi(node.sumber)
        nama_properti = node.properti.nilai

        if not isinstance(sumber, ObjekPinjaman):
            pesan = f"Hanya pusaka pinjaman yang bisa dibisiki dengan '.', bukan sebuah '{self._infer_type(sumber)}'."
            raise self._buat_kesalahan(node.sumber, pesan)

        try:
            properti_python = getattr(sumber.objek_python, nama_properti)
            return self._konversi_dari_python(properti_python)
        except AttributeError:
            pesan = f"Dari balik selubung pinjaman, nama '{nama_properti}' tak ditemukan."
            raise self._buat_kesalahan(node.properti, pesan)

    def kunjungi_FungsiDeklarasi(self, node):
        nama_fungsi = node.nama_fungsi.nilai

        # 1. Buat Simbol placeholder dan segera definisikan.
        simbol_placeholder = Simbol(None, TipeToken.FUNGSI, node.nama_fungsi.token)
        self.lingkungan.definisikan(nama_fungsi, simbol_placeholder)

        # 2. Buat objek fungsi, yang sekarang menangkap lingkungan dengan placeholder-nya sendiri.
        fungsi_obj = FungsiPengguna(node, self.lingkungan)

        # 3. Sekarang perbarui nilai simbol dengan objek fungsi yang sebenarnya.
        simbol_placeholder.nilai = fungsi_obj

    def kunjungi_PernyataanKembalikan(self, node):
        # Evaluasi nilai yang akan dikembalikan.
        # Jika tidak ada nilai (misal: 'kembalikan'), gunakan NIL_INSTANCE.
        nilai = self.kunjungi(node.nilai_kembalian) if node.nilai_kembalian else NIL_INSTANCE

        # Lemparkan exception untuk menghentikan eksekusi dan mengirim sinyal nilai kembali.
        raise KembalikanNilaiException(nilai)

    def kunjungi_Jika_Maka(self, node):
        # Evaluasi kondisi 'jika' utama
        kondisi_utama = self.kunjungi(node.kondisi)
        if self._cek_kebenaran(kondisi_utama):
            return self._eksekusi_blok(node.blok_maka)

        # Evaluasi rantai 'lain jika'
        for kondisi_lain, blok_lain in node.rantai_lain_jika:
            if self._cek_kebenaran(self.kunjungi(kondisi_lain)):
                return self._eksekusi_blok(blok_lain)

        # Eksekusi blok 'lain' jika ada
        if node.blok_lain:
            return self._eksekusi_blok(node.blok_lain)

    def kunjungi_Selama(self, node):
        """Mengeksekusi loop 'selama'."""
        while self._cek_kebenaran(self.kunjungi(node.kondisi)):
            self._eksekusi_blok(node.badan)

    def kunjungi_Pilih(self, node):
        """Mengeksekusi blok 'pilih' dengan mencocokkan ekspresi."""
        nilai_ekspresi = self.kunjungi(node.ekspresi)

        for kasus in node.kasus:
            nilai_pola = self.kunjungi(kasus.pola)
            if nilai_ekspresi == nilai_pola:
                self._eksekusi_blok(kasus.badan)
                return # Hanya satu kasus yang dieksekusi

        if node.kasus_lainnya:
            self._eksekusi_blok(node.kasus_lainnya.badan)

    def kunjungi_PilihKasus(self, node):
        # Logika ditangani oleh kunjungi_Pilih
        pass

    def kunjungi_KasusLainnya(self, node):
        # Logika ditangani oleh kunjungi_Pilih
        pass

    def kunjungi_FoxUnary(self, node):
        operand = self.kunjungi(node.operand)
        operator = node.op.tipe
        if operator == TipeToken.KURANG:
            if not isinstance(operand, (int, float)):
                tipe_operand_str = self._infer_type(operand)
                pesan = f"Tanda '{node.op.nilai}' hanya bisa menaungi angka, bukan sang '{tipe_operand_str}'."
                raise self._buat_kesalahan(node, pesan)
            return -operand
        elif operator == TipeToken.TIDAK:
            return not bool(operand)
        pesan = f"Sebuah '{operator}' misterius mencoba beraksi sendiri, namun takdirnya belum tertulis."
        raise self._buat_kesalahan(node, pesan)

    def kunjungi_FoxBinary(self, node):
        kiri, kanan, op = self.kunjungi(node.kiri), self.kunjungi(node.kanan), node.op.tipe
        tipe_kiri_str, tipe_kanan_str = self._infer_type(kiri), self._infer_type(kanan)

        # Helper untuk memeriksa apakah suatu nilai adalah numerik murni (bukan boolean)
        is_kiri_numeric = isinstance(kiri, (int, float)) and not isinstance(kiri, bool)
        is_kanan_numeric = isinstance(kanan, (int, float)) and not isinstance(kanan, bool)

        if op == TipeToken.TAMBAH:
            if is_kiri_numeric and is_kanan_numeric: return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str): return kiri + kanan
            pesan = f"Dua dunia tak dapat menyatu. '{tipe_kiri_str}' dan '{tipe_kanan_str}' tak bisa dijumlahkan dalam harmoni."
            raise self._buat_kesalahan(node, pesan)

        if op in (TipeToken.KURANG, TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO, TipeToken.PANGKAT):
            if not (is_kiri_numeric and is_kanan_numeric):
                pesan = f"Hanya angka yang bisa menari dalam tarian '{node.op.nilai}', bukan sang '{tipe_kiri_str}' dan '{tipe_kanan_str}'."
                raise self._buat_kesalahan(node, pesan)

            if op == TipeToken.KURANG: return kiri - kanan
            if op == TipeToken.KALI: return kiri * kanan
            if op == TipeToken.BAGI:
                if kanan == 0: raise self._buat_kesalahan(node, "Semesta tak terhingga saat dibagi dengan kehampaan (nol).")
                return kiri / kanan
            if op == TipeToken.MODULO:
                if kanan == 0: raise self._buat_kesalahan(node, "Sisa pembagian dengan kehampaan (nol) adalah sebuah misteri.")
                return kiri % kanan
            if op == TipeToken.PANGKAT: return kiri ** kanan

        if op in (TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL, TipeToken.LEBIH_BESAR_SAMA, TipeToken.LEBIH_KECIL_SAMA):
            try:
                if op == TipeToken.SAMA_DENGAN_SAMA: return kiri == kanan
                if op == TipeToken.TIDAK_SAMA: return kiri != kanan
                if op == TipeToken.LEBIH_BESAR: return kiri > kanan
                if op == TipeToken.LEBIH_KECIL: return kiri < kanan
                if op == TipeToken.LEBIH_BESAR_SAMA: return kiri >= kanan
                if op == TipeToken.LEBIH_KECIL_SAMA: return kiri <= kanan
            except TypeError:
                pesan = f"Tak bisa membandingkan apel dan jeruk. '{tipe_kiri_str}' dan '{tipe_kanan_str}' tak bisa ditimbang bersama."
                raise self._buat_kesalahan(node, pesan)

        if op == TipeToken.DAN: return bool(kiri) and bool(kanan)
        if op == TipeToken.ATAU: return bool(kiri) or bool(kanan)

        pesan = f"Sebuah '{op.nilai}' misterius mencoba menyatukan dua jiwa, namun takdirnya belum tertulis."
        raise self._buat_kesalahan(node, pesan)

    def interpretasi(self):
        # FIX-BLOCKER-2: Memastikan `time.time` dipanggil sebagai fungsi.
        # Laporan analis menyebutkan `time.time` tanpa `()`, yang akan menyebabkan
        # timer tidak berfungsi. Kode ini mengonfirmasi implementasi yang benar.
        self.start_time = time.time()
        return self.kunjungi(self.ast)
