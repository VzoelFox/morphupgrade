# morph_engine/pengurai.py
# Changelog:
# - PATCH-020B: Menambahkan logika parsing untuk fungsi `ambil()`.
# - PATCH-019C: Menambahkan logika parsing untuk array literal.
# - PATCH-016: Menambahkan logika parsing untuk deklarasi fungsi, pernyataan
#              kembalikan, dan literal nil.
# - PATCH-014: Mengimplementasikan mekanisme pemulihan kesalahan (error recovery).
# - PATCH-004B: Mengoptimalkan lookahead di `urai_pernyataan` untuk keterbacaan.
# - PATCH-010: Menambahkan logika untuk membedakan antara deklarasi variabel
#              (dengan 'biar'/'tetap') dan assignment (tanpa keyword).
# - FIX-002: Membersihkan pembuatan NodeBoolean agar menggunakan token
#            langsung dari leksikal.
# - PATCH-015A: Mendefinisikan RESERVED_KEYWORDS untuk validasi identifier.
# - PATCH-015B: Menambahkan `debug_mode` untuk logging kondisional.
# - PATCH-015C: Menambahkan helper `validasi_nama_variabel`.
# - PATCH-015D: Mengintegrasikan validasi identifier ke dalam parser.
# TODO: Tambahkan DARI, BUKA, TUTUP ke RESERVED_KEYWORDS saat fitur
#       terkait diimplementasikan.

from .token_morph import TipeToken, Token
from .node_ast import (
    NodeProgram, NodeDeklarasiVariabel, NodePanggilFungsi,
    NodeNama, NodeKonstanta, NodeOperasiBiner, NodeOperasiUnary,
    NodeJikaMaka, NodeAssignment, NodeFungsiDeklarasi, NodePernyataanKembalikan,
    NodeDaftar, NodeAmbil, NodeSelama, NodeKamus, NodeAksesMember, NodePilih,
    NodeKasusPilih, NodeKasusLainnya, NodeImpor, NodePinjam, NodeAksesTitik
)
from .error_utils import ErrorFormatter

# Kumpulan token yang tidak boleh digunakan sebagai nama variabel/identifier.
RESERVED_KEYWORDS = {
    TipeToken.BIAR, TipeToken.TETAP, TipeToken.JIKA,
    TipeToken.MAKA, TipeToken.AKHIR, TipeToken.BENAR,
    TipeToken.SALAH, TipeToken.DAN, TipeToken.ATAU,
    TipeToken.TIDAK, TipeToken.TULIS, TipeToken.FUNGSI,
    TipeToken.KEMBALIKAN, TipeToken.NIL, TipeToken.AMBIL,
    TipeToken.LAIN, TipeToken.SELAMA, TipeToken.PILIH,
    TipeToken.KETIKA, TipeToken.LAINNYA, TipeToken.PINJAM
}

class PenguraiKesalahan(Exception):
    def __init__(self, pesan, token, cuplikan=""):
        pesan_terformat = ErrorFormatter.format_pengurai_error(token, pesan, cuplikan)
        super().__init__(pesan_terformat)
        self.pesan = pesan
        self.token = token
        self.cuplikan = cuplikan

class Pengurai:
    def __init__(self, daftar_token, debug_mode=False):
        self.daftar_token = daftar_token
        self.posisi = 0
        self.token_sekarang = self.daftar_token[self.posisi] if self.posisi < len(self.daftar_token) else None
        self.daftar_kesalahan = []
        self.debug_mode = debug_mode
        self.di_dalam_fungsi = False

    def _debug(self, msg):
        if self.debug_mode:
            import sys
            print(f"[PARSER-DEBUG] {msg}", file=sys.stderr)

    def maju(self):
        self._debug(f"Maju dari: {self.token_sekarang}")
        self.posisi += 1
        if self.posisi < len(self.daftar_token):
            self.token_sekarang = self.daftar_token[self.posisi]
        else:
            self.token_sekarang = None

    def lihat_token_berikutnya(self):
        if self.posisi + 1 >= len(self.daftar_token): return None
        return self.daftar_token[self.posisi + 1]

    def cocok(self, *daftar_tipe_token):
        if self.token_sekarang is None: return False
        return self.token_sekarang.tipe in daftar_tipe_token

    def buat_pesan_error(self, token_diharapkan):
        found_token = self.token_sekarang
        pesan = f"Penyair mengharapkan bisikan '{token_diharapkan.name}', namun yang terdengar adalah gema '{found_token.tipe.name}'."
        awal = max(0, self.posisi - 2)
        akhir = min(len(self.daftar_token), self.posisi + 2)
        cuplikan_list = [f"{'>> ' if i == self.posisi else '   '}{t.tipe.name} ('{t.nilai or ''}')" for i, t in enumerate(self.daftar_token[awal:akhir], awal)]
        cuplikan_str = "\nDi antara bait-bait ini, sang takdir berbelok:\n" + "\n".join(cuplikan_list)
        return PenguraiKesalahan(pesan, found_token, cuplikan_str)

    def validasi_nama_variabel(self, token):
        """Memvalidasi bahwa sebuah token dapat digunakan sebagai identifier."""
        if token.tipe in RESERVED_KEYWORDS:
            pesan = (
                f"Kata sakral '{token.nilai}' tak boleh dinodai sebagai nama biasa.\n"
                f"Saran: Mungkin '{token.nilai}_sang_pujangga' atau 'makna_{token.nilai}' lebih pantas?"
            )
            raise PenguraiKesalahan(pesan, token)
        if token.tipe != TipeToken.PENGENAL:
            raise self.buat_pesan_error(TipeToken.PENGENAL)

    def urai_pernyataan(self):
        if self.cocok(TipeToken.AMBIL_SEMUA, TipeToken.AMBIL_SEBAGIAN): return self.urai_impor()
        if self.cocok(TipeToken.PINJAM): return self.urai_pinjam()
        if self.cocok(TipeToken.FUNGSI): return self.urai_deklarasi_fungsi()
        if self.cocok(TipeToken.KEMBALIKAN): return self.urai_pernyataan_kembalikan()
        if self.cocok(TipeToken.BIAR, TipeToken.TETAP): return self.urai_deklarasi_variabel()
        if self.cocok(TipeToken.JIKA): return self.urai_jika()
        if self.cocok(TipeToken.PILIH): return self.urai_pilih()
        if self.cocok(TipeToken.SELAMA): return self.urai_selama()
        if self.cocok(TipeToken.TULIS): return self.urai_panggil_fungsi()
        if self.cocok(TipeToken.AMBIL): return self.urai_ambil()

        # Pendekatan baru: urai sebagai ekspresi, lalu cek apakah itu assignment
        node_kiri = self.urai_ekspresi()

        if self.cocok(TipeToken.SAMA_DENGAN):
            self.maju() # Lewati '='
            # Memvalidasi bahwa sisi kiri adalah target assignment yang valid
            if not isinstance(node_kiri, (NodeNama, NodeAksesMember, NodeAksesTitik)):
                pesan = "Hanya bejana nama yang bisa diisi makna baru, bukan sebuah ekspresi yang telah tercipta."
                raise PenguraiKesalahan(
                    pesan,
                    # Coba dapatkan token yang relevan dari node
                    getattr(node_kiri, 'token', self.token_sekarang)
                )

            nilai_kanan = self.urai_ekspresi()
            return NodeAssignment(node_kiri, nilai_kanan)

        # Jika bukan assignment, node itu sendiri adalah pernyataannya (misal: pemanggilan fungsi)
        return node_kiri

    def urai_deklarasi_fungsi(self):
        self.maju() # Lewati token 'fungsi'
        nama_fungsi = NodeNama(self.token_sekarang)
        self.validasi_nama_variabel(self.token_sekarang)
        self.maju()

        if not self.cocok(TipeToken.BUKA_KURUNG): raise self.buat_pesan_error(TipeToken.BUKA_KURUNG)
        self.maju()

        parameter = []
        if not self.cocok(TipeToken.TUTUP_KURUNG):
            self.validasi_nama_variabel(self.token_sekarang)
            parameter.append(NodeNama(self.token_sekarang))
            self.maju()
            while self.cocok(TipeToken.KOMA):
                self.maju()
                self.validasi_nama_variabel(self.token_sekarang)
                parameter.append(NodeNama(self.token_sekarang))
                self.maju()

        if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
        self.maju()

        if not self.cocok(TipeToken.MAKA): raise self.buat_pesan_error(TipeToken.MAKA)
        self.maju()
        if self.cocok(TipeToken.AKHIR_BARIS): self.maju()

        status_sebelumnya = self.di_dalam_fungsi
        self.di_dalam_fungsi = True
        try:
            badan = []
            while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
                if self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()
                    continue
                pernyataan = self.urai_pernyataan()
                badan.append(pernyataan)
                if self.cocok(TipeToken.AKHIR_BARIS):
                    while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
                elif not self.cocok(TipeToken.AKHIR): raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)
        finally:
            self.di_dalam_fungsi = status_sebelumnya

        if not self.cocok(TipeToken.AKHIR): raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju()

        return NodeFungsiDeklarasi(nama_fungsi, parameter, badan)

    def urai_pernyataan_kembalikan(self):
        token_kembalikan = self.token_sekarang
        if not self.di_dalam_fungsi:
            pesan = "Bisikan 'kembalikan' hanya bermakna di dalam sebuah syair (fungsi)."
            raise PenguraiKesalahan(pesan, token_kembalikan)

        self.maju() # Lewati token 'kembalikan'
        nilai_kembalian = None
        if not self.cocok(TipeToken.AKHIR_BARIS, TipeToken.AKHIR, TipeToken.ADS):
            nilai_kembalian = self.urai_ekspresi()
        return NodePernyataanKembalikan(nilai_kembalian)

    def urai_impor(self):
        """
        Mengurai pernyataan 'ambil_semua' dan 'ambil_sebagian'.
        Sintaks yang didukung:
        - ambil_semua "path/modul.fox"
        - ambil_semua "path/modul.fox" sebagai alias
        - ambil_sebagian nama1, nama2 dari "path/modul.fox"
        """
        jenis_impor = self.token_sekarang
        self.maju() # Lewati AMBIL_SEMUA atau AMBIL_SEBAGIAN

        if jenis_impor.tipe == TipeToken.AMBIL_SEMUA:
            if not self.cocok(TipeToken.TEKS):
                pesan = "Setelah 'ambil_semua', penyair harus membisikkan nama lembaran dalam tanda kutip."
                raise PenguraiKesalahan(pesan, self.token_sekarang)
            path_modul = NodeKonstanta(self.token_sekarang, self.token_sekarang.nilai)
            self.maju()

            alias = None
            if self.cocok(TipeToken.SEBAGAI):
                self.maju() # Lewati 'sebagai'
                self.validasi_nama_variabel(self.token_sekarang)
                alias = NodeNama(self.token_sekarang)
                self.maju()

            return NodeImpor(jenis_impor, path_modul, alias=alias)

        elif jenis_impor.tipe == TipeToken.AMBIL_SEBAGIAN:
            daftar_nama = []
            while self.cocok(TipeToken.PENGENAL):
                self.validasi_nama_variabel(self.token_sekarang)
                daftar_nama.append(NodeNama(self.token_sekarang))
                self.maju()
                if not self.cocok(TipeToken.KOMA):
                    break
                self.maju() # Lewati KOMA

            if not daftar_nama:
                pesan = "Setelah 'ambil_sebagian', sebutkan setidaknya satu nama pusaka yang ingin kau pinjam."
                raise PenguraiKesalahan(pesan, self.token_sekarang)

            if not self.cocok(TipeToken.DARI):
                raise self.buat_pesan_error(TipeToken.DARI)
            self.maju() # Lewati 'dari'

            if not self.cocok(TipeToken.TEKS):
                pesan = "Setelah 'dari', penyair harus membisikkan nama lembaran dalam tanda kutip."
                raise PenguraiKesalahan(pesan, self.token_sekarang)
            path_modul = NodeKonstanta(self.token_sekarang, self.token_sekarang.nilai)
            self.maju()

            return NodeImpor(jenis_impor, path_modul, daftar_nama=daftar_nama)

        # Seharusnya tidak pernah sampai di sini jika dipanggil dari urai_pernyataan
        raise PenguraiKesalahan("Panggilan untuk mengambil lembaran ini terdengar sumbang.", jenis_impor)

    def urai_pinjam(self):
        """Mengurai pernyataan 'pinjam "path.py" sebagai alias'."""
        self.maju() # Lewati PINJAM

        if not self.cocok(TipeToken.TEKS):
            pesan = "Setelah 'pinjam', bisikkan nama pusaka dari dunia seberang dalam tanda kutip."
            raise PenguraiKesalahan(pesan, self.token_sekarang)
        path_modul = NodeKonstanta(self.token_sekarang, self.token_sekarang.nilai)
        self.maju()

        if not self.cocok(TipeToken.SEBAGAI):
            pesan = "Setiap pusaka pinjaman harus diberi nama samaran dengan 'sebagai'."
            raise PenguraiKesalahan(pesan, self.token_sekarang)
        self.maju() # Lewati 'sebagai'

        self.validasi_nama_variabel(self.token_sekarang)
        alias = NodeNama(self.token_sekarang)
        self.maju()

        return NodePinjam(path_modul, alias)

    def urai_deklarasi_variabel(self):
        jenis_deklarasi = self.token_sekarang; self.maju()
        self.validasi_nama_variabel(self.token_sekarang)
        nama_variabel = NodeNama(self.token_sekarang); self.maju()
        if not self.cocok(TipeToken.SAMA_DENGAN): raise self.buat_pesan_error(TipeToken.SAMA_DENGAN)
        self.maju()
        try:
            nilai = self.urai_ekspresi()
        except PenguraiKesalahan:
            raise
        return NodeDeklarasiVariabel(jenis_deklarasi, nama_variabel, nilai)

    def urai_panggil_fungsi(self):
        nama_fungsi = self.token_sekarang; self.maju()
        if not self.cocok(TipeToken.BUKA_KURUNG): raise self.buat_pesan_error(TipeToken.BUKA_KURUNG)
        self.maju()
        daftar_argumen = []
        if not self.cocok(TipeToken.TUTUP_KURUNG):
            daftar_argumen.append(self.urai_ekspresi())
            while self.cocok(TipeToken.KOMA):
                self.maju()
                daftar_argumen.append(self.urai_ekspresi())
        if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
        self.maju()
        return NodePanggilFungsi(NodeNama(nama_fungsi), daftar_argumen)

    def urai_ambil(self):
        """Mengurai pemanggilan fungsi 'ambil()' atau 'ambil(ekspresi)'."""
        self.maju()  # Lewati token AMBIL
        if not self.cocok(TipeToken.BUKA_KURUNG):
            raise self.buat_pesan_error(TipeToken.BUKA_KURUNG)
        self.maju()

        prompt_node = None
        if not self.cocok(TipeToken.TUTUP_KURUNG):
            prompt_node = self.urai_ekspresi()

        # Setelah mengurai satu argumen, jika ada koma, itu adalah kesalahan.
        if self.cocok(TipeToken.KOMA):
            pesan = "Fungsi 'ambil' hanya bisa menerima satu bisikan saja."
            raise PenguraiKesalahan(pesan, self.token_sekarang)

        if not self.cocok(TipeToken.TUTUP_KURUNG):
            raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
        self.maju() # Konsumsi ')'
        return NodeAmbil(prompt_node)

    def urai_jika(self):
        self.maju() # Lewati 'jika'
        kondisi = self.urai_ekspresi()
        if not self.cocok(TipeToken.MAKA): raise self.buat_pesan_error(TipeToken.MAKA)
        self.maju() # Lewati 'maka'
        if self.cocok(TipeToken.AKHIR_BARIS): self.maju()

        blok_maka = []
        while not self.cocok(TipeToken.AKHIR, TipeToken.LAIN, TipeToken.ADS):
            if self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()
                continue
            pernyataan = self.urai_pernyataan()
            blok_maka.append(pernyataan)
            if self.cocok(TipeToken.AKHIR_BARIS):
                while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
            elif not self.cocok(TipeToken.AKHIR, TipeToken.LAIN):
                raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)

        rantai_lain_jika = []
        while self.cocok(TipeToken.LAIN) and self.lihat_token_berikutnya() and self.lihat_token_berikutnya().tipe == TipeToken.JIKA:
            self.maju() # Lewati 'lain'
            self.maju() # Lewati 'jika'
            kondisi_lain_jika = self.urai_ekspresi()
            if not self.cocok(TipeToken.MAKA): raise self.buat_pesan_error(TipeToken.MAKA)
            self.maju() # Lewati 'maka'
            if self.cocok(TipeToken.AKHIR_BARIS): self.maju()

            blok_lain_jika = []
            while not self.cocok(TipeToken.AKHIR, TipeToken.LAIN, TipeToken.ADS):
                if self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()
                    continue
                pernyataan = self.urai_pernyataan()
                blok_lain_jika.append(pernyataan)
                if self.cocok(TipeToken.AKHIR_BARIS):
                    while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
                elif not self.cocok(TipeToken.AKHIR, TipeToken.LAIN):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)
            rantai_lain_jika.append((kondisi_lain_jika, blok_lain_jika))

        blok_lain = None
        if self.cocok(TipeToken.LAIN):
            self.maju() # Lewati 'lain'
            if self.cocok(TipeToken.AKHIR_BARIS): self.maju()
            blok_lain = []
            while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
                if self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()
                    continue
                pernyataan = self.urai_pernyataan()
                blok_lain.append(pernyataan)
                if self.cocok(TipeToken.AKHIR_BARIS):
                    while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
                elif not self.cocok(TipeToken.AKHIR):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)

        if not self.cocok(TipeToken.AKHIR): raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju()
        return NodeJikaMaka(kondisi, blok_maka, rantai_lain_jika, blok_lain)

    def urai_selama(self):
        """Mengurai perulangan 'selama kondisi maka ... akhir'."""
        self.maju() # Lewati 'selama'
        kondisi = self.urai_ekspresi()
        if not self.cocok(TipeToken.MAKA):
            raise self.buat_pesan_error(TipeToken.MAKA)
        self.maju() # Lewati 'maka'
        if self.cocok(TipeToken.AKHIR_BARIS):
            self.maju()

        badan = []
        while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
            if self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()
                continue
            pernyataan = self.urai_pernyataan()
            badan.append(pernyataan)
            if self.cocok(TipeToken.AKHIR_BARIS):
                while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
            elif not self.cocok(TipeToken.AKHIR):
                raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)

        if not self.cocok(TipeToken.AKHIR):
            raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju() # Lewati 'akhir'
        return NodeSelama(kondisi, badan)

    def urai_pilih(self):
        """Mengurai pernyataan 'pilih ekspresi ketika ... lainnya ... akhir'."""
        self.maju() # Lewati 'pilih'
        ekspresi = self.urai_ekspresi()
        if self.cocok(TipeToken.AKHIR_BARIS):
            self.maju()

        kasus = []
        kasus_lainnya = None

        while self.cocok(TipeToken.KETIKA):
            self.maju() # Lewati 'ketika'
            pola = self.urai_ekspresi()
            if not self.cocok(TipeToken.MAKA):
                raise self.buat_pesan_error(TipeToken.MAKA)
            self.maju() # Lewati 'maka'
            if self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()

            badan = []
            while not self.cocok(TipeToken.AKHIR, TipeToken.KETIKA, TipeToken.LAINNYA, TipeToken.ADS):
                if self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()
                    continue
                pernyataan = self.urai_pernyataan()
                badan.append(pernyataan)
                if self.cocok(TipeToken.AKHIR_BARIS):
                    while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
                elif not self.cocok(TipeToken.AKHIR, TipeToken.KETIKA, TipeToken.LAINNYA):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)

            kasus.append(NodeKasusPilih(pola, badan))

        if self.cocok(TipeToken.LAINNYA):
            self.maju() # Lewati 'lainnya'
            if not self.cocok(TipeToken.MAKA):
                raise self.buat_pesan_error(TipeToken.MAKA)
            self.maju() # Lewati 'maka'
            if self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()

            badan_lainnya = []
            while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
                if self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()
                    continue
                pernyataan = self.urai_pernyataan()
                badan_lainnya.append(pernyataan)
                if self.cocok(TipeToken.AKHIR_BARIS):
                    while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
                elif not self.cocok(TipeToken.AKHIR):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)
            kasus_lainnya = NodeKasusLainnya(badan_lainnya)

        if not self.cocok(TipeToken.AKHIR):
            raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju() # Lewati 'akhir'
        return NodePilih(ekspresi, kasus, kasus_lainnya)

    def urai_array(self):
        """Parse array literal: [elem1, elem2, ...]"""
        self.maju()  # Lewati '['
        elemen = []
        if not self.cocok(TipeToken.KURUNG_SIKU_TUTUP):
            elemen.append(self.urai_ekspresi())
            while self.cocok(TipeToken.KOMA):
                self.maju()
                elemen.append(self.urai_ekspresi())
        if not self.cocok(TipeToken.KURUNG_SIKU_TUTUP):
            raise self.buat_pesan_error(TipeToken.KURUNG_SIKU_TUTUP)
        self.maju() # Lewati ']'
        return NodeDaftar(elemen)

    def urai_kamus(self):
        """Mengurai literal kamus: '{kunci1: nilai1, kunci2: nilai2, ...}'."""
        self.maju() # Lewati '{'
        pasangan = []
        if not self.cocok(TipeToken.KURUNG_KURAWAL_KANAN):
            while True:
                # Kunci harus berupa Teks atau Angka untuk MVP
                if not self.cocok(TipeToken.TEKS, TipeToken.ANGKA, TipeToken.PENGENAL):
                    pesan = "Kunci untuk membuka peti harta karun (kamus) haruslah sederhana: sebuah teks, angka, atau nama."
                    raise PenguraiKesalahan(pesan, self.token_sekarang)
                kunci = self.urai_primary()
                if not self.cocok(TipeToken.TITIK_DUA):
                    raise self.buat_pesan_error(TipeToken.TITIK_DUA)
                self.maju() # Lewati ':'
                nilai = self.urai_ekspresi()
                pasangan.append((kunci, nilai))
                if not self.cocok(TipeToken.KOMA):
                    break
                self.maju() # Lewati ','

        if not self.cocok(TipeToken.KURUNG_KURAWAL_KANAN):
            raise self.buat_pesan_error(TipeToken.KURUNG_KURAWAL_KANAN)
        self.maju() # Lewati '}'
        return NodeKamus(pasangan)

    def urai_primary(self):
        token = self.token_sekarang
        if self.cocok(TipeToken.NIL, TipeToken.BENAR, TipeToken.SALAH, TipeToken.ANGKA, TipeToken.TEKS):
            node = NodeKonstanta(token, token.nilai)
            self.maju()
            return node
        if self.cocok(TipeToken.KURUNG_SIKU_BUKA): return self.urai_array()
        if self.cocok(TipeToken.KURUNG_KURAWAL_KIRI): return self.urai_kamus()
        if self.cocok(TipeToken.AMBIL):
            return self.urai_ambil()
        if self.cocok(TipeToken.PENGENAL, TipeToken.TULIS):
            if self.lihat_token_berikutnya() and self.lihat_token_berikutnya().tipe == TipeToken.BUKA_KURUNG:
                return self.urai_panggil_fungsi()
            elif self.cocok(TipeToken.PENGENAL):
                self.maju()
                return NodeNama(token)
        if self.cocok(TipeToken.BUKA_KURUNG):
            self.maju()
            node = self.urai_ekspresi()
            if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
            self.maju()
            return node
        pesan = "Penyair kehilangan alur cerita. Sebuah ekspresi dinanti, namun keheningan yang ditemui."
        raise PenguraiKesalahan(pesan, token)

    def urai_unary(self):
        if self.cocok(TipeToken.KURANG, TipeToken.TIDAK):
            op = self.token_sekarang
            self.maju()
            operand = self.urai_unary()
            return NodeOperasiUnary(op=op, operand=operand)
        return self.urai_panggilan_dan_akses()

    def urai_panggilan_dan_akses(self):
        """Mengurai pemanggilan fungsi, akses array/kamus, dan akses titik."""
        node = self.urai_primary()
        while self.cocok(TipeToken.BUKA_KURUNG, TipeToken.KURUNG_SIKU_BUKA, TipeToken.TITIK):
            if self.cocok(TipeToken.BUKA_KURUNG):
                # Ini adalah pemanggilan fungsi
                self.maju() # Lewati '('
                daftar_argumen = []
                if not self.cocok(TipeToken.TUTUP_KURUNG):
                    daftar_argumen.append(self.urai_ekspresi())
                    while self.cocok(TipeToken.KOMA):
                        self.maju()
                        daftar_argumen.append(self.urai_ekspresi())
                if not self.cocok(TipeToken.TUTUP_KURUNG):
                    raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
                self.maju()
                # `node` menjadi `nama_fungsi`
                node = NodePanggilFungsi(node, daftar_argumen)
            elif self.cocok(TipeToken.KURUNG_SIKU_BUKA):
                # Ini adalah akses member
                self.maju() # Lewati '['
                kunci = self.urai_ekspresi()
                if not self.cocok(TipeToken.KURUNG_SIKU_TUTUP):
                    raise self.buat_pesan_error(TipeToken.KURUNG_SIKU_TUTUP)
                self.maju() # Lewati ']'
                node = NodeAksesMember(node, kunci)
            elif self.cocok(TipeToken.TITIK):
                # Ini adalah akses titik
                self.maju() # Lewati '.'
                if not self.cocok(TipeToken.PENGENAL):
                    pesan = "Setelah titik, penyair harus membisikkan sebuah nama."
                    raise PenguraiKesalahan(pesan, self.token_sekarang)
                properti = NodeNama(self.token_sekarang)
                self.maju()
                node = NodeAksesTitik(node, properti)
        return node

    def urai_pangkat(self):
        node = self.urai_unary()
        if self.cocok(TipeToken.PANGKAT):
            op = self.token_sekarang
            self.maju()
            # Panggil urai_pangkat secara rekursif untuk sisi kanan (right-associativity)
            kanan = self.urai_pangkat()
            return NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_perkalian(self):
        node = self.urai_pangkat()
        while self.cocok(TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO):
            op = self.token_sekarang
            self.maju()
            kanan = self.urai_pangkat()
            node = NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_penjumlahan(self):
        node = self.urai_perkalian()
        while self.cocok(TipeToken.TAMBAH, TipeToken.KURANG):
            op = self.token_sekarang
            self.maju()
            kanan = self.urai_perkalian()
            node = NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_perbandingan(self):
        node = self.urai_penjumlahan()
        while self.cocok(TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_KECIL, TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL_SAMA, TipeToken.LEBIH_BESAR_SAMA):
            op = self.token_sekarang
            self.maju()
            kanan = self.urai_penjumlahan()
            node = NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_dan(self):
        node = self.urai_perbandingan()
        while self.cocok(TipeToken.DAN):
            op = self.token_sekarang
            self.maju()
            kanan = self.urai_perbandingan()
            node = NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_atau(self):
        node = self.urai_dan()
        while self.cocok(TipeToken.ATAU):
            op = self.token_sekarang
            self.maju()
            kanan = self.urai_dan()
            node = NodeOperasiBiner(kiri=node, op=op, kanan=kanan)
        return node

    def urai_ekspresi(self):
        return self.urai_atau()

    def _sinkronisasi(self):
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            if self.token_sekarang.tipe == TipeToken.AKHIR_BARIS:
                self.maju(); return
            if self.token_sekarang.tipe in [TipeToken.BIAR, TipeToken.TETAP, TipeToken.TULIS, TipeToken.JIKA, TipeToken.FUNGSI]:
                return
            self.maju()

    def urai(self):
        daftar_pernyataan = []
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            while self.token_sekarang is not None and self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()
            if self.token_sekarang is None or self.cocok(TipeToken.ADS):
                break

            # Jika lexer menghasilkan token yang tidak dikenal, catat sebagai kesalahan
            if self.cocok(TipeToken.TIDAK_DIKENAL):
                pesan = f"Sebuah simbol asing '{self.token_sekarang.nilai}' muncul, tak dikenal dalam kamus semesta ini."
                kesalahan = PenguraiKesalahan(pesan, self.token_sekarang)
                self.daftar_kesalahan.append(kesalahan)
                self.maju() # Konsumsi token buruk dan lanjutkan
                continue

            try:
                pernyataan = self.urai_pernyataan()
                if pernyataan:
                    daftar_pernyataan.append(pernyataan)

                # Setelah sebuah pernyataan, kita harapkan akhir baris atau akhir file.
                # Ini membantu menangkap kesalahan seperti 'biar x = 5 10'
                if not self.cocok(TipeToken.ADS, TipeToken.AKHIR_BARIS, TipeToken.AKHIR, TipeToken.LAIN):
                    self.daftar_kesalahan.append(self.buat_pesan_error(TipeToken.AKHIR_BARIS))
                    self._sinkronisasi()

            except PenguraiKesalahan as e:
                self.daftar_kesalahan.append(e)
                self._sinkronisasi()

        if self.daftar_kesalahan:
            pesan_header = (
                "Dalam kidung kodemu, beberapa nada sumbang terdengar. "
                "Berikut adalah gema kesalahan yang tertangkap:\n\n"
            )
            pesan_gabungan = "\n".join(str(err) for err in self.daftar_kesalahan)
            pesan_lengkap = pesan_header + pesan_gabungan

            # Melempar satu kesalahan gabungan di akhir
            # Menggunakan token dari kesalahan pertama untuk info lokasi umum
            raise PenguraiKesalahan(pesan_lengkap, self.daftar_kesalahan[0].token)

        return NodeProgram(daftar_pernyataan)
