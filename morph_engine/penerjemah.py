# morph_engine/penerjemah.py
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
#              - Melacak kedalaman rekursi di `kunjungi_NodePanggilFungsi`.
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
#              - `kunjungi_NodeDeklarasiVariabel` melempar error jika variabel sudah ada.
# - PATCH-010: Menambahkan metode `kunjungi_NodeAssignment` untuk menangani
#              logika assignment.
#              - Memisahkan logika deklarasi murni di `kunjungi_NodeDeklarasiVariabel`.
#              - Memperbaiki pesan error untuk assignment ke var yang belum ada.
import os
import time
from .node_ast import *
from .token_morph import TipeToken
from .error_utils import ErrorFormatter

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
            raise self._buat_kesalahan(
                node,
                f"Eksekusi program melebihi batas waktu maksimal ({MAX_EXECUTION_TIME} detik)."
            )
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

class Penerjemah(PengunjungNode):
    def __init__(self, ast):
        self.ast = ast
        self.lingkungan = Lingkungan()
        self.registri_fungsi = REGISTRI_FUNGSI_BAWAAN
        self.recursion_depth = 0
        self.start_time = None

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
        return "tidak dikenal"

    def _buat_kesalahan(self, node, pesan):
        """Helper terpusat untuk membuat instance KesalahanRuntime."""
        token = None
        # Mencoba mengekstrak token yang paling relevan dari node untuk info baris/kolom
        if hasattr(node, 'nama_variabel') and hasattr(node.nama_variabel, 'token'):
            token = node.nama_variabel.token
        elif hasattr(node, 'nama_fungsi') and hasattr(node.nama_fungsi, 'token'):
            token = node.nama_fungsi.token
        elif hasattr(node, 'operator'):
            token = node.operator
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
            raise self._buat_kesalahan(node, f"Fungsi '{nama_fungsi}' membutuhkan minimal {aturan['min_args']} argumen, tetapi menerima {jumlah_arg}.")
        if aturan['max_args'] is not None and jumlah_arg > aturan['max_args']:
            raise self._buat_kesalahan(node, f"Fungsi '{nama_fungsi}' membutuhkan maksimal {aturan['max_args']} argumen, tetapi menerima {jumlah_arg}.")

        # Validasi tipe argumen
        if aturan['tipe_args']:
            # Jika tipe_args adalah list, berarti setiap argumen bisa punya tipe berbeda
            if isinstance(aturan['tipe_args'], list) and len(aturan['tipe_args']) == jumlah_arg:
                for i, (arg, tipe_diharapkan) in enumerate(zip(argumen, aturan['tipe_args'])):
                    if not isinstance(arg, tipe_diharapkan):
                        raise self._buat_kesalahan(node, f"Argumen ke-{i+1} untuk fungsi '{nama_fungsi}' harus bertipe '{tipe_diharapkan.__name__}', bukan '{type(arg).__name__}'.")
            # Jika tipe_args adalah tuple, berarti semua argumen harus salah satu dari tipe tsb
            elif isinstance(aturan['tipe_args'], list) and isinstance(aturan['tipe_args'][0], tuple):
                tipe_diharapkan = aturan['tipe_args'][0]
                for i, arg in enumerate(argumen):
                    if not isinstance(arg, tipe_diharapkan):
                        raise self._buat_kesalahan(node, f"Semua argumen untuk fungsi '{nama_fungsi}' harus bertipe numerik (int/float), tapi argumen ke-{i+1} adalah '{type(arg).__name__}'.")

    def kunjungi_NodeProgram(self, node):
        # Lintasan 1: Daftarkan semua fungsi (hoisting)
        for pernyataan in node.daftar_pernyataan:
            if isinstance(pernyataan, NodeFungsiDeklarasi):
                self.kunjungi(pernyataan)

        # Lintasan 2: Eksekusi kode lainnya
        for pernyataan in node.daftar_pernyataan:
            if not isinstance(pernyataan, NodeFungsiDeklarasi):
                self.kunjungi(pernyataan)

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai

        if self.lingkungan.ada_di_scope_ini(nama_var):
            simbol_lama = self.lingkungan.dapatkan(nama_var)
            raise self._buat_kesalahan(
                node,
                f"Variabel '{nama_var}' sudah dideklarasikan di scope ini pada baris {simbol_lama.token_deklarasi.baris}."
            )

        nilai_var = self.kunjungi(node.nilai)
        tipe_deklarasi = node.jenis_deklarasi.tipe
        token_deklarasi = node.nama_variabel.token
        simbol = Simbol(nilai_var, tipe_deklarasi, token_deklarasi)
        self.lingkungan.definisikan(nama_var, simbol)

    def kunjungi_NodeAssignment(self, node):
        # Cek apakah ini adalah assignment ke member kamus/array
        if isinstance(node.nama_variabel, NodeAksesMember):
            akses_node = node.nama_variabel
            sumber = self.kunjungi(akses_node.sumber)
            kunci = self.kunjungi(akses_node.kunci)
            nilai_baru = self.kunjungi(node.nilai)

            if isinstance(sumber, dict):
                if not isinstance(kunci, (str, int, float, bool)):
                     raise self._buat_kesalahan(
                        akses_node.kunci,
                        f"Kunci kamus harus berupa tipe primitif, bukan '{self._infer_type(kunci)}'."
                    )
                sumber[kunci] = nilai_baru
                return
            elif isinstance(sumber, list):
                if not isinstance(kunci, int):
                    raise self._buat_kesalahan(
                        akses_node.kunci,
                        f"Indeks array harus berupa 'angka bulat', bukan '{self._infer_type(kunci)}'."
                    )
                if 0 <= kunci < len(sumber):
                    sumber[kunci] = nilai_baru
                else:
                    raise self._buat_kesalahan(
                        akses_node.kunci,
                        f"Indeks array {kunci} di luar batas untuk array dengan panjang {len(sumber)}."
                    )
                return
            else:
                raise self._buat_kesalahan(
                    akses_node.sumber,
                    f"Tidak dapat melakukan assignment ke member dari tipe '{self._infer_type(sumber)}'."
                )

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

            pesan = f"Variabel '{nama_var}' belum dideklarasikan. Gunakan 'biar {nama_var} = ...' untuk deklarasi baru."
            if saran_terdekat:
                pesan += f" Mungkin maksud Anda '{saran_terdekat}'?"
            raise self._buat_kesalahan(node, pesan)

        if simbol.tipe_deklarasi == TipeToken.TETAP:
            raise self._buat_kesalahan(node, f"Variabel tetap '{nama_var}' tidak dapat diubah nilainya.")

        nilai_var = self.kunjungi(node.nilai)
        simbol.nilai = nilai_var

    def kunjungi_NodePanggilFungsi(self, node):
        self.recursion_depth += 1
        try:
            # 1. Periksa batas rekursi SEGERA
            if self.recursion_depth > RECURSION_LIMIT:
                pesan = f"Fungsi '{node.nama_fungsi.nilai}' terjebak dalam pusaran rekursi yang tak berujung. Batasan kedalaman {RECURSION_LIMIT} telah terlampaui."
                raise self._buat_kesalahan(node, pesan)

            nama_fungsi = node.nama_fungsi.nilai

            # 2. Evaluasi semua argumen terlebih dahulu
            argumen = [self.kunjungi(arg) for arg in node.daftar_argumen]

            # 3. Periksa apakah itu fungsi bawaan
            if nama_fungsi in self.registri_fungsi:
                aturan = self.registri_fungsi[nama_fungsi]
                self._validasi_panggilan_fungsi(nama_fungsi, argumen, aturan, node)
                return aturan['handler'](argumen)

            # 4. Jika bukan, cari fungsi yang ditentukan pengguna
            simbol_fungsi = self.lingkungan.dapatkan(nama_fungsi)
            if not (simbol_fungsi and isinstance(simbol_fungsi.nilai, FungsiPengguna)):
                raise self._buat_kesalahan(node, f"'{nama_fungsi}' bukan fungsi yang bisa dipanggil.")

            fungsi_obj = simbol_fungsi.nilai
            deklarasi = fungsi_obj.deklarasi_node

            # 5. Validasi jumlah argumen (arity check)
            if len(argumen) != len(deklarasi.parameter):
                pesan = f"Fungsi '{nama_fungsi}' mengharapkan {len(deklarasi.parameter)} argumen, tetapi menerima {len(argumen)}."
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

    def kunjungi_NodePengenal(self, node):
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

            pesan = f"Variabel '{nama_var}' tidak didefinisikan."
            if saran_terdekat:
                pesan += f" Mungkin maksud Anda '{saran_terdekat}'?"
            raise self._buat_kesalahan(node, pesan)
        return simbol.nilai

    def kunjungi_NodeTeks(self, node): return node.nilai
    def kunjungi_NodeAngka(self, node): return node.nilai
    def kunjungi_NodeBoolean(self, node): return node.nilai
    def kunjungi_NodeNil(self, node): return NIL_INSTANCE

    def kunjungi_NodeArray(self, node):
        """Evaluasi array literal menjadi Python list"""
        return [self.kunjungi(elem) for elem in node.elemen]

    def kunjungi_NodeKamus(self, node):
        """Evaluasi literal kamus menjadi Python dict."""
        kamus_hasil = {}
        for node_kunci, node_nilai in node.pasangan:
            kunci = self.kunjungi(node_kunci)
            # Validasi bahwa kunci adalah tipe yang dapat di-hash
            if not isinstance(kunci, (str, int, float, bool)):
                 raise self._buat_kesalahan(
                    node_kunci,
                    f"Kunci kamus harus berupa tipe primitif (teks, angka, boolean), bukan '{self._infer_type(kunci)}'."
                )
            nilai = self.kunjungi(node_nilai)
            kamus_hasil[kunci] = nilai
        return kamus_hasil

    def kunjungi_NodeAmbil(self, node):
        """Menangani fungsi bawaan ambil() untuk input pengguna."""
        prompt_text = ""
        if node.prompt_node:
            prompt_text = self.kunjungi(node.prompt_node)
            if not isinstance(prompt_text, str):
                tipe_prompt = self._infer_type(prompt_text)
                raise self._buat_kesalahan(
                    node.prompt_node,
                    f"Prompt untuk fungsi 'ambil' harus berupa 'teks', bukan '{tipe_prompt}'."
                )

        try:
            user_input = input(prompt_text)
            return user_input
        except EOFError:
            return "" # Sesuai spesifikasi, kembalikan string kosong saat EOF

    def kunjungi_NodeAksesMember(self, node):
        """Mengevaluasi akses member pada kamus atau array."""
        sumber = self.kunjungi(node.sumber)
        kunci = self.kunjungi(node.kunci)

        if isinstance(sumber, dict):
            # Akses kamus
            if not isinstance(kunci, (str, int, float, bool)):
                raise self._buat_kesalahan(
                    node.kunci,
                    f"Kunci kamus harus berupa tipe primitif, bukan '{self._infer_type(kunci)}'."
                )
            return sumber.get(kunci, NIL_INSTANCE)
        elif isinstance(sumber, list):
            # Akses array
            if not isinstance(kunci, int):
                raise self._buat_kesalahan(
                    node.kunci,
                    f"Indeks array harus berupa 'angka bulat', bukan '{self._infer_type(kunci)}'."
                )
            if 0 <= kunci < len(sumber):
                return sumber[kunci]
            else:
                # Sesuai konvensi, akses di luar batas mengembalikan nil
                return NIL_INSTANCE
        else:
            raise self._buat_kesalahan(
                node.sumber,
                f"Tipe '{self._infer_type(sumber)}' tidak mendukung akses member dengan '[...]'."
            )

    def kunjungi_NodeFungsiDeklarasi(self, node):
        nama_fungsi = node.nama_fungsi.nilai

        # 1. Buat Simbol placeholder dan segera definisikan.
        simbol_placeholder = Simbol(None, TipeToken.FUNGSI, node.nama_fungsi.token)
        self.lingkungan.definisikan(nama_fungsi, simbol_placeholder)

        # 2. Buat objek fungsi, yang sekarang menangkap lingkungan dengan placeholder-nya sendiri.
        fungsi_obj = FungsiPengguna(node, self.lingkungan)

        # 3. Sekarang perbarui nilai simbol dengan objek fungsi yang sebenarnya.
        simbol_placeholder.nilai = fungsi_obj

    def kunjungi_NodePernyataanKembalikan(self, node):
        # Evaluasi nilai yang akan dikembalikan.
        # Jika tidak ada nilai (misal: 'kembalikan'), gunakan NIL_INSTANCE.
        nilai = self.kunjungi(node.nilai_kembalian) if node.nilai_kembalian else NIL_INSTANCE

        # Lemparkan exception untuk menghentikan eksekusi dan mengirim sinyal nilai kembali.
        raise KembalikanNilaiException(nilai)

    def kunjungi_NodeJikaMaka(self, node):
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

    def kunjungi_NodeSelama(self, node):
        """Mengeksekusi loop 'selama'."""
        while self._cek_kebenaran(self.kunjungi(node.kondisi)):
            self._eksekusi_blok(node.badan)

    def kunjungi_NodePilih(self, node):
        """Mengeksekusi blok 'pilih' dengan mencocokkan ekspresi."""
        nilai_ekspresi = self.kunjungi(node.ekspresi)

        for kasus in node.kasus:
            nilai_pola = self.kunjungi(kasus.pola)
            if nilai_ekspresi == nilai_pola:
                self._eksekusi_blok(kasus.badan)
                return # Hanya satu kasus yang dieksekusi

        if node.kasus_lainnya:
            self._eksekusi_blok(node.kasus_lainnya.badan)

    # Metode berikut ini sebenarnya tidak dipanggil secara langsung,
    # karena logikanya ditangani di dalam kunjungi_NodePilih,
    # tetapi menambahkannya adalah praktik yang baik untuk kelengkapan.
    def kunjungi_NodeKasusPilih(self, node):
        # Logika ditangani oleh kunjungi_NodePilih
        pass

    def kunjungi_NodeKasusLainnya(self, node):
        # Logika ditangani oleh kunjungi_NodePilih
        pass

    def kunjungi_NodeOperasiUnary(self, node):
        operand = self.kunjungi(node.operand)
        operator = node.operator.tipe
        if operator == TipeToken.KURANG:
            if not isinstance(operand, (int, float)):
                tipe_operand_str = self._infer_type(operand)
                raise self._buat_kesalahan(node, f"Operator '-' hanya dapat digunakan pada 'angka bulat' atau 'angka desimal', bukan '{tipe_operand_str}'.")
            return -operand
        elif operator == TipeToken.TIDAK:
            return not bool(operand)
        raise self._buat_kesalahan(node, f"Operator unary '{operator}' tidak didukung.")

    def kunjungi_NodeOperasiBiner(self, node):
        kiri, kanan, op = self.kunjungi(node.kiri), self.kunjungi(node.kanan), node.operator.tipe
        tipe_kiri_str, tipe_kanan_str = self._infer_type(kiri), self._infer_type(kanan)

        # Helper untuk memeriksa apakah suatu nilai adalah numerik murni (bukan boolean)
        is_kiri_numeric = isinstance(kiri, (int, float)) and not isinstance(kiri, bool)
        is_kanan_numeric = isinstance(kanan, (int, float)) and not isinstance(kanan, bool)

        if op == TipeToken.TAMBAH:
            if is_kiri_numeric and is_kanan_numeric: return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str): return kiri + kanan
            raise self._buat_kesalahan(node, f"Operasi '+' tidak dapat digunakan antara '{tipe_kiri_str}' dan '{tipe_kanan_str}'.")

        if op in (TipeToken.KURANG, TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO, TipeToken.PANGKAT):
            if not (is_kiri_numeric and is_kanan_numeric):
                raise self._buat_kesalahan(node, f"Operasi aritmatika '{node.operator.nilai}' hanya dapat digunakan pada tipe angka, bukan antara '{tipe_kiri_str}' dan '{tipe_kanan_str}'.")

            if op == TipeToken.KURANG: return kiri - kanan
            if op == TipeToken.KALI: return kiri * kanan
            if op == TipeToken.BAGI:
                if kanan == 0: raise self._buat_kesalahan(node, "Tidak bisa membagi dengan nol.")
                return kiri / kanan
            if op == TipeToken.MODULO:
                if kanan == 0: raise self._buat_kesalahan(node, "Tidak bisa modulo dengan nol.")
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
                raise self._buat_kesalahan(node, f"Operasi perbandingan '{node.operator.nilai}' tidak dapat digunakan antara '{tipe_kiri_str}' dan '{tipe_kanan_str}'.")

        if op == TipeToken.DAN: return bool(kiri) and bool(kanan)
        if op == TipeToken.ATAU: return bool(kiri) or bool(kanan)
        raise self._buat_kesalahan(node, f"Operator biner '{op.nilai}' tidak didukung.")

    def interpretasi(self):
        # FIX-BLOCKER-2: Memastikan `time.time` dipanggil sebagai fungsi.
        # Laporan analis menyebutkan `time.time` tanpa `()`, yang akan menyebabkan
        # timer tidak berfungsi. Kode ini mengonfirmasi implementasi yang benar.
        self.start_time = time.time()
        return self.kunjungi(self.ast)
