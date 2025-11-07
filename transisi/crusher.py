# transisi/crusher.py
# Parser untuk "Kelahiran Kembali MORPH"

from .morph_t import Token, TipeToken
from . import absolute_sntx_morph as ast

class PenguraiKesalahan(Exception):
    pass

class Pengurai:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.saat_ini = 0
        self.daftar_kesalahan = []

    def urai(self) -> ast.Bagian | None:
        """Mulai proses parsing."""
        daftar_pernyataan = []
        while not self._di_akhir():
            try:
                pernyataan = self._deklarasi()
                if pernyataan:
                    daftar_pernyataan.append(pernyataan)
            except PenguraiKesalahan as e:
                self._sinkronisasi()

        if self.daftar_kesalahan:
            # Di dunia nyata, kita mungkin ingin melemparkan exception gabungan di sini
            # Untuk sekarang, kita kembalikan None jika ada kesalahan
            return None

        return ast.Bagian(daftar_pernyataan)

    # --- Aturan Tata Bahasa (Grammar Rules) ---

    def _deklarasi(self):
        if self._cocok(TipeToken.BIAR, TipeToken.TETAP):
            return self._deklarasi_variabel()
        return self._pernyataan()

    def _deklarasi_variabel(self):
        jenis_deklarasi = self._sebelumnya()
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel.")

        nilai = None
        if self._cocok(TipeToken.SAMADENGAN):
            nilai = self._ekspresi()

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah deklarasi variabel.")
        return ast.DeklarasiVariabel(jenis_deklarasi, nama, nilai)

    def _pernyataan(self):
        if self._cocok(TipeToken.TULIS):
            return self._pernyataan_tulis()
        if self._cocok(TipeToken.KURAWAL_BUKA):
            return ast.Bagian(self._blok())
        # Tambahkan aturan pernyataan lain di sini (jika, selama, dll.)
        return self._pernyataan_ekspresi()

    def _pernyataan_tulis(self):
        self._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah 'tulis'.")
        argumen = []
        if not self._periksa(TipeToken.KURUNG_TUTUP):
            argumen.append(self._ekspresi())
            while self._cocok(TipeToken.KOMA):
                argumen.append(self._ekspresi())
        self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah argumen.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'tulis'.")
        return ast.Tulis(argumen)

    def _blok(self):
        daftar_pernyataan = []
        while not self._periksa(TipeToken.KURAWAL_TUTUP) and not self._di_akhir():
            daftar_pernyataan.append(self._deklarasi())
        self._konsumsi(TipeToken.KURAWAL_TUTUP, "Dibutuhkan '}' untuk menutup blok.")
        return daftar_pernyataan

    def _pernyataan_ekspresi(self):
        expr = self._ekspresi()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah ekspresi.")
        return ast.PernyataanEkspresi(expr)

    def _ekspresi(self):
        return self._penugasan()

    def _penugasan(self):
        expr = self._logika_atau()

        if self._cocok(TipeToken.SAMADENGAN):
            equals = self._sebelumnya()
            nilai = self._penugasan()

            if isinstance(expr, ast.Identitas):
                nama = expr.token
                # Ini seharusnya menjadi `ubah`, tapi untuk PoC kita pakai assignment biasa
                return ast.Assignment(nama, nilai)

            self._kesalahan(equals, "Target penugasan tidak valid.")

        return expr

    # --- Hierarki Precedensi Operator ---
    def _buat_parser_biner(self, metode_lebih_tinggi, *tipe_token):
        def parser():
            expr = metode_lebih_tinggi()
            while self._cocok(*tipe_token):
                operator = self._sebelumnya()
                kanan = metode_lebih_tinggi()
                expr = ast.FoxBinary(expr, operator, kanan)
            return expr
        return parser

    _logika_atau = _buat_parser_biner(lambda self: self._logika_dan(), TipeToken.ATAU)
    _logika_dan = _buat_parser_biner(lambda self: self._perbandingan(), TipeToken.DAN)
    _perbandingan = _buat_parser_biner(lambda self: self._penjumlahan(), TipeToken.SAMA_DENGAN, TipeToken.TIDAK_SAMA, TipeToken.KURANG_DARI, TipeToken.KURANG_SAMA, TipeToken.LEBIH_DARI, TipeToken.LEBIH_SAMA)
    _penjumlahan = _buat_parser_biner(lambda self: self._perkalian(), TipeToken.TAMBAH, TipeToken.KURANG)
    _perkalian = _buat_parser_biner(lambda self: self._unary(), TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO)

    def _unary(self):
        if self._cocok(TipeToken.TIDAK, TipeToken.KURANG):
            operator = self._sebelumnya()
            kanan = self._unary()
            return ast.FoxUnary(operator, kanan)
        return self._primary()

    def _primary(self):
        if self._cocok(TipeToken.SALAH): return ast.Konstanta(self._sebelumnya())
        if self._cocok(TipeToken.BENAR): return ast.Konstanta(self._sebelumnya())
        if self._cocok(TipeToken.NIL): return ast.Konstanta(self._sebelumnya())
        if self._cocok(TipeToken.ANGKA, TipeToken.TEKS):
            return ast.Konstanta(self._sebelumnya())
        if self._cocok(TipeToken.NAMA):
            return ast.Identitas(self._sebelumnya())
        if self._cocok(TipeToken.KURUNG_BUKA):
            expr = self._ekspresi()
            self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah ekspresi.")
            return expr # Seharusnya ada NodeGrouping, tapi untuk simpel kita kembalikan ekspresinya langsung

        raise self._kesalahan(self._intip(), "Ekspresi tidak terduga.")

    # --- Helper Methods ---

    def _konsumsi(self, tipe, pesan):
        if self._periksa(tipe):
            return self._maju()
        raise self._kesalahan(self._intip(), pesan)

    def _konsumsi_akhir_baris(self, pesan):
        if self._cocok(TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA):
            return
        # Jika token berikutnya adalah penutup blok atau akhir file, anggap valid
        if self._periksa(TipeToken.AKHIR) or self._periksa(TipeToken.KURAWAL_TUTUP) or self._di_akhir():
             return
        raise self._kesalahan(self._intip(), pesan)

    def _cocok(self, *tipe_tokens):
        for tipe in tipe_tokens:
            if self._periksa(tipe):
                self._maju()
                return True
        return False

    def _periksa(self, tipe):
        if self._di_akhir():
            return False
        return self._intip().tipe == tipe

    def _maju(self):
        if not self._di_akhir():
            self.saat_ini += 1
        return self._sebelumnya()

    def _di_akhir(self):
        return self._intip().tipe == TipeToken.ADS

    def _intip(self):
        return self.tokens[self.saat_ini]

    def _sebelumnya(self):
        return self.tokens[self.saat_ini - 1]

    def _kesalahan(self, token: Token, pesan: str):
        # Simpan tuple (token, pesan) untuk formatter
        self.daftar_kesalahan.append((token, pesan))
        return PenguraiKesalahan()

    def _sinkronisasi(self):
        """Error recovery: maju sampai menemukan awal pernyataan berikutnya."""
        self._maju()
        while not self._di_akhir():
            if self._sebelumnya().tipe in (TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA):
                return

            # Kata kunci yang kemungkinan memulai pernyataan baru
            if self._intip().tipe in [
                TipeToken.FUNGSI,
                TipeToken.BIAR,
                TipeToken.TETAP,
                TipeToken.JIKA,
                TipeToken.SELAMA,
                TipeToken.KEMBALIKAN,
                TipeToken.TULIS
            ]:
                return

            self._maju()
