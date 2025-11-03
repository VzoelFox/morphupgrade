# morph_engine/pengurai.py
# Changelog:
# - PATCH-014: Mengimplementasikan mekanisme pemulihan kesalahan (error recovery) yang sudah terverifikasi.
# - ... (Changelog sebelumnya)

from .token_morph import TipeToken, Token
from .node_ast import (
    NodeProgram, NodeDeklarasiVariabel, NodePanggilFungsi,
    NodePengenal, NodeTeks, NodeAngka, NodeBoolean, NodeOperasiBiner, NodeOperasiUnary,
    NodeJika, NodeAssignment
)
from .error_utils import ErrorFormatter

class PenguraiKesalahan(Exception):
    def __init__(self, pesan, token, cuplikan=""):
        pesan_terformat = ErrorFormatter.format_pengurai_error(token, pesan, cuplikan)
        super().__init__(pesan_terformat)
        self.pesan = pesan
        self.token = token
        self.cuplikan = cuplikan

class Pengurai:
    def __init__(self, daftar_token):
        self.daftar_token = daftar_token
        self.posisi = 0
        self.token_sekarang = self.daftar_token[self.posisi] if self.posisi < len(self.daftar_token) else None
        self.daftar_kesalahan = []

    def maju(self):
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
        pesan = f"Diharapkan token '{token_diharapkan.name}', tapi ditemukan '{found_token.tipe.name}'."
        awal = max(0, self.posisi - 2)
        akhir = min(len(self.daftar_token), self.posisi + 2)
        cuplikan_list = [f"{'>> ' if i == self.posisi else '   '}{t.tipe.name} ('{t.nilai or ''}')" for i, t in enumerate(self.daftar_token[awal:akhir], awal)]
        cuplikan_str = "Konteks Token:\n" + "\n".join(cuplikan_list)
        return PenguraiKesalahan(pesan, found_token, cuplikan_str)

    def urai_pernyataan(self):
        if self.cocok(TipeToken.BIAR, TipeToken.TETAP): return self.urai_deklarasi_variabel()
        if self.cocok(TipeToken.JIKA): return self.urai_jika()
        if self.cocok(TipeToken.TULIS): return self.urai_panggil_fungsi()
        if self.cocok(TipeToken.PENGENAL):
            token_berikutnya = self.lihat_token_berikutnya()
            if token_berikutnya and token_berikutnya.tipe == TipeToken.SAMA_DENGAN:
                return self.urai_assignment()
        return self.urai_ekspresi()

    def urai_assignment(self):
        nama_variabel = NodePengenal(self.token_sekarang)
        self.maju()
        if not self.cocok(TipeToken.SAMA_DENGAN): raise self.buat_pesan_error(TipeToken.SAMA_DENGAN)
        self.maju()
        nilai = self.urai_ekspresi()
        return NodeAssignment(nama_variabel, nilai)

    def urai_deklarasi_variabel(self):
        jenis_deklarasi = self.token_sekarang
        self.maju()
        if not self.cocok(TipeToken.PENGENAL): raise self.buat_pesan_error(TipeToken.PENGENAL)
        nama_variabel = NodePengenal(self.token_sekarang)
        self.maju()
        if not self.cocok(TipeToken.SAMA_DENGAN): raise self.buat_pesan_error(TipeToken.SAMA_DENGAN)
        self.maju()
        try:
            nilai = self.urai_ekspresi()
        except PenguraiKesalahan:
            raise
        return NodeDeklarasiVariabel(jenis_deklarasi, nama_variabel, nilai)

    def urai_panggil_fungsi(self):
        nama_fungsi = self.token_sekarang
        self.maju()
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
        return NodePanggilFungsi(NodePengenal(nama_fungsi), daftar_argumen)

    def urai_jika(self):
        self.maju()
        kondisi = self.urai_ekspresi()
        if not self.cocok(TipeToken.MAKA): raise self.buat_pesan_error(TipeToken.MAKA)
        self.maju()
        if self.cocok(TipeToken.AKHIR_BARIS): self.maju()
        blok = []
        while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
            if self.cocok(TipeToken.AKHIR_BARIS): self.maju(); continue
            pernyataan = self.urai_pernyataan()
            blok.append(pernyataan)
            if self.cocok(TipeToken.AKHIR_BARIS):
                while self.cocok(TipeToken.AKHIR_BARIS): self.maju()
            elif not self.cocok(TipeToken.AKHIR): raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)
        if not self.cocok(TipeToken.AKHIR): raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju()
        return NodeJika(kondisi, blok)

    def urai_primary(self):
        token = self.token_sekarang
        if self.cocok(TipeToken.BENAR, TipeToken.SALAH): self.maju(); return NodeBoolean(token)
        if self.cocok(TipeToken.ANGKA): self.maju(); return NodeAngka(token)
        if self.cocok(TipeToken.TEKS): self.maju(); return NodeTeks(token)
        if self.cocok(TipeToken.PENGENAL, TipeToken.TULIS):
            if self.lihat_token_berikutnya() and self.lihat_token_berikutnya().tipe == TipeToken.BUKA_KURUNG:
                return self.urai_panggil_fungsi()
            elif self.cocok(TipeToken.PENGENAL):
                self.maju(); return NodePengenal(token)
        if self.cocok(TipeToken.BUKA_KURUNG):
            self.maju()
            node = self.urai_ekspresi()
            if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
            self.maju()
            return node
        raise PenguraiKesalahan("Diharapkan sebuah ekspresi, tapi ditemukan token yang tidak valid.", token)

    def urai_unary(self):
        if self.cocok(TipeToken.KURANG, TipeToken.TIDAK):
            operator = self.token_sekarang; self.maju(); operand = self.urai_unary()
            return NodeOperasiUnary(operator, operand)
        return self.urai_primary()

    def urai_perkalian(self):
        node = self.urai_unary()
        while self.cocok(TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO):
            operator = self.token_sekarang; self.maju(); kanan = self.urai_unary()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_penjumlahan(self):
        node = self.urai_perkalian()
        while self.cocok(TipeToken.TAMBAH, TipeToken.KURANG):
            operator = self.token_sekarang; self.maju(); kanan = self.urai_perkalian()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_perbandingan(self):
        node = self.urai_penjumlahan()
        while self.cocok(TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_KECIL, TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL_SAMA, TipeToken.LEBIH_BESAR_SAMA):
            operator = self.token_sekarang; self.maju(); kanan = self.urai_penjumlahan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_dan(self):
        node = self.urai_perbandingan()
        while self.cocok(TipeToken.DAN):
            operator = self.token_sekarang; self.maju(); kanan = self.urai_perbandingan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_atau(self):
        node = self.urai_dan()
        while self.cocok(TipeToken.ATAU):
            operator = self.token_sekarang; self.maju(); kanan = self.urai_dan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_ekspresi(self):
        return self.urai_atau()

    def _sinkronisasi(self):
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            if self.token_sekarang.tipe == TipeToken.AKHIR_BARIS:
                self.maju(); return
            if self.token_sekarang.tipe in [TipeToken.BIAR, TipeToken.TETAP, TipeToken.TULIS, TipeToken.JIKA]:
                return
            self.maju()

    def urai(self):
        daftar_pernyataan = []
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            while self.token_sekarang is not None and self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()

            if self.token_sekarang is None or self.cocok(TipeToken.ADS):
                break

            try:
                pernyataan = self.urai_pernyataan()
                if pernyataan:
                    daftar_pernyataan.append(pernyataan)
                if not self.cocok(TipeToken.ADS) and not self.cocok(TipeToken.AKHIR_BARIS):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)
            except PenguraiKesalahan as e:
                self.daftar_kesalahan.append(e)
                self._sinkronisasi()
        return NodeProgram(daftar_pernyataan)
