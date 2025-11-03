# morph_engine/pengurai.py
# Changelog:
# - PATCH-010: Menambahkan logika untuk membedakan antara deklarasi variabel
#              (dengan 'biar'/'tetap') dan assignment (tanpa keyword).
#              - Menambah `NodeAssignment` ke dalam alur parsing.
#              - Memperkenalkan `urai_assignment()` dan lookahead di `urai_pernyataan()`.
# - FIX-002: Membersihkan pembuatan NodeBoolean agar menggunakan token
#            langsung dari leksikal, yang sekarang sudah membawa nilai
#            boolean (True/False).

from .token_morph import TipeToken, Token
from .node_ast import (
    NodeProgram, NodeDeklarasiVariabel, NodePanggilFungsi,
    NodePengenal, NodeTeks, NodeAngka, NodeBoolean, NodeOperasiBiner, NodeOperasiUnary,
    NodeJika, NodeAssignment  # Diimpor untuk PATCH-010
)

class PenguraiKesalahan(Exception):
    def __init__(self, pesan, token, cuplikan=""):
        super().__init__(f"Kesalahan di baris {token.baris}, kolom {token.kolom}: {pesan}\n{cuplikan}")
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
        """Melihat token berikutnya tanpa memajukan posisi. Penting untuk lookahead."""
        if self.posisi + 1 >= len(self.daftar_token):
            return None
        return self.daftar_token[self.posisi + 1]

    def cocok(self, *daftar_tipe_token):
        if self.token_sekarang is None:
            return False
        return self.token_sekarang.tipe in daftar_tipe_token

    def buat_pesan_error(self, token_diharapkan):
        found_token = self.token_sekarang
        pesan = f"Diharapkan token '{token_diharapkan.name}', tapi ditemukan '{found_token.tipe.name}'."
        awal = max(0, self.posisi - 2)
        akhir = min(len(self.daftar_token), self.posisi + 2)
        cuplikan_list = [f"{'>> ' if i == self.posisi else '   '}{t.tipe.name} ('{t.nilai or ''}')" for i, t in enumerate(self.daftar_token[awal:akhir], awal)]
        cuplikan_str = "Konteks Token:\n" + "\n".join(cuplikan_list)
        return PenguraiKesalahan(pesan, found_token, cuplikan_str)

    def sinkronisasi(self):
        self.maju()
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            if self.token_sekarang.tipe == TipeToken.AKHIR_BARIS: return
            if self.token_sekarang.tipe in [TipeToken.BIAR, TipeToken.TETAP, TipeToken.TULIS]: return
            self.maju()

    def urai_pernyataan(self):
        if self.cocok(TipeToken.BIAR, TipeToken.TETAP):
            return self.urai_deklarasi_variabel()
        if self.cocok(TipeToken.TULIS):
            return self.urai_panggil_fungsi()
        if self.cocok(TipeToken.JIKA):
            return self.urai_jika()

        # PATCH-010: Logika lookahead untuk membedakan assignment dari ekspresi biasa
        if self.cocok(TipeToken.PENGENAL):
            token_berikutnya = self.lihat_token_berikutnya()
            if token_berikutnya and token_berikutnya.tipe == TipeToken.SAMA_DENGAN:
                return self.urai_assignment()

        return self.urai_ekspresi()

    def urai_assignment(self):
        """Mengurai pernyataan assignment: 'nama_variabel = nilai'."""
        nama_variabel = NodePengenal(self.token_sekarang)
        self.maju()  # Maju dari PENGENAL
        if not self.cocok(TipeToken.SAMA_DENGAN):
            raise self.buat_pesan_error(TipeToken.SAMA_DENGAN)
        self.maju()  # Maju dari SAMA_DENGAN
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
        nilai = self.urai_ekspresi()
        return NodeDeklarasiVariabel(jenis_deklarasi, nama_variabel, nilai)

    def urai_panggil_fungsi(self):
        nama_fungsi = self.token_sekarang
        self.maju()
        if not self.cocok(TipeToken.BUKA_KURUNG): raise self.buat_pesan_error(TipeToken.BUKA_KURUNG)
        self.maju()

        argumen = None
        if not self.cocok(TipeToken.TUTUP_KURUNG):
            argumen = self.urai_ekspresi()
        else:
            raise PenguraiKesalahan("Panggilan fungsi 'tulis' membutuhkan satu argumen.", self.token_sekarang)

        if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
        self.maju()
        return NodePanggilFungsi(NodePengenal(nama_fungsi), argumen)

    def urai_jika(self):
        self.maju()  # Lewati token 'jika'
        kondisi = self.urai_ekspresi()
        if not self.cocok(TipeToken.MAKA):
            raise self.buat_pesan_error(TipeToken.MAKA)
        self.maju() # Lewati token 'maka'

        # Lewati akhir baris opsional setelah 'maka'
        if self.cocok(TipeToken.AKHIR_BARIS):
            self.maju()

        blok = []
        while not self.cocok(TipeToken.AKHIR, TipeToken.ADS):
            pernyataan = self.urai_pernyataan()
            blok.append(pernyataan)
            # Membutuhkan pemisah antar pernyataan di dalam blok
            if self.cocok(TipeToken.AKHIR_BARIS):
                self.maju()
            else:
                # Jika bukan akhir blok dan bukan akhir baris, maka ada error
                if not self.cocok(TipeToken.AKHIR):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)


        if not self.cocok(TipeToken.AKHIR):
            raise self.buat_pesan_error(TipeToken.AKHIR)
        self.maju()  # Lewati token 'akhir'

        return NodeJika(kondisi, blok)

    def urai_primary(self):
        token = self.token_sekarang
        # FIXED: FIX-002 - Logika disederhanakan.
        # Karena leksikal sekarang memberikan nilai boolean (True/False) langsung
        # pada token BENAR/SALAH, kita tidak perlu lagi membuat token baru.
        # Cukup gunakan token yang ada.
        if self.cocok(TipeToken.BENAR, TipeToken.SALAH):
            self.maju()
            return NodeBoolean(token)
        if self.cocok(TipeToken.ANGKA): self.maju(); return NodeAngka(token)
        if self.cocok(TipeToken.TEKS): self.maju(); return NodeTeks(token)
        if self.cocok(TipeToken.PENGENAL):
            # Lookahead: Cek apakah ini pemanggilan fungsi (misal: panjang(x)) atau hanya variabel (x)
            if self.lihat_token_berikutnya() and self.lihat_token_berikutnya().tipe == TipeToken.BUKA_KURUNG:
                return self.urai_panggil_fungsi() # Gunakan kembali logika parsing pemanggilan fungsi
            else:
                self.maju()
                return NodePengenal(token)
        if self.cocok(TipeToken.BUKA_KURUNG):
            self.maju()
            node = self.urai_ekspresi()
            if not self.cocok(TipeToken.TUTUP_KURUNG): raise self.buat_pesan_error(TipeToken.TUTUP_KURUNG)
            self.maju()
            return node
        raise PenguraiKesalahan(f"Token tidak terduga saat parsing: '{token.tipe.name}'.", token)

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

    def urai(self):
        daftar_pernyataan = []
        maks_iterasi = len(self.daftar_token) * 2; iterasi = 0

        # Lewati semua AKHIR_BARIS di awal file
        while self.token_sekarang is not None and self.cocok(TipeToken.AKHIR_BARIS):
            self.maju()

        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            iterasi += 1
            if iterasi > maks_iterasi:
                self.daftar_kesalahan.append("Parser terjebak dalam loop tak terbatas."); break

            try:
                pernyataan = self.urai_pernyataan()
                if pernyataan:
                    daftar_pernyataan.append(pernyataan)

                # Setelah sebuah pernyataan, harus ada pemisah atau akhir dari segalanya.
                # Kasus 1: Akhir file, parsing selesai.
                if self.cocok(TipeToken.ADS):
                    break

                # Kasus 2: Harus ada setidaknya satu AKHIR_BARIS.
                if not self.cocok(TipeToken.AKHIR_BARIS):
                    raise self.buat_pesan_error(TipeToken.AKHIR_BARIS)

                # Lewati semua AKHIR_BARIS berikutnya (untuk baris kosong)
                while self.cocok(TipeToken.AKHIR_BARIS):
                    self.maju()

            except PenguraiKesalahan as e:
                self.daftar_kesalahan.append(str(e)); self.sinkronisasi()

        return NodeProgram(daftar_pernyataan)
