# morph_engine/pengurai.py
from .token_morph import TipeToken
from .node_ast import (
    NodeProgram, NodeDeklarasiVariabel, NodePanggilFungsi,
    NodePengenal, NodeTeks, NodeAngka, NodeOperasiBiner, NodeOperasiUnary
)

class PenguraiKesalahan(Exception):
    pass

class Pengurai:
    def __init__(self, daftar_token):
        self.daftar_token = daftar_token
        self.posisi = 0
        self.token_sekarang = self.daftar_token[self.posisi]

    def maju(self):
        """Memajukan posisi baca token."""
        self.posisi += 1
        if self.posisi < len(self.daftar_token):
            self.token_sekarang = self.daftar_token[self.posisi]
        else:
            self.token_sekarang = None # Sinyal akhir

    def cocok(self, *daftar_tipe_token):
        """Memeriksa apakah token sekarang cocok dengan salah satu tipe yang diberikan."""
        if self.token_sekarang is None:
            return False
        return self.token_sekarang.tipe in daftar_tipe_token

    def urai_pernyataan(self):
        """Menganalisis satu pernyataan (statement)."""
        if self.cocok(TipeToken.BIAR, TipeToken.TETAP):
            return self.urai_deklarasi_variabel()

        if self.cocok(TipeToken.TULIS):
             return self.urai_panggil_fungsi()

        # Jika tidak ada yang cocok, ini mungkin adalah ekspresi mandiri (jika bahasa mendukungnya)
        # Untuk saat ini kita anggap error atau lewati
        return self.urai_ekspresi()


    def urai_deklarasi_variabel(self):
        """Menganalisis 'biar nama = nilai' atau 'tetap nama = nilai'."""
        jenis_deklarasi = self.token_sekarang
        self.maju()

        if not self.cocok(TipeToken.PENGENAL):
            raise PenguraiKesalahan("Diharapkan nama variabel setelah 'biar' atau 'tetap'.")

        nama_variabel = NodePengenal(self.token_sekarang)
        self.maju()

        if not self.cocok(TipeToken.SAMA_DENGAN):
            raise PenguraiKesalahan("Diharapkan '=' setelah nama variabel.")
        self.maju()

        nilai = self.urai_ekspresi()
        return NodeDeklarasiVariabel(jenis_deklarasi, nama_variabel, nilai)


    def urai_panggil_fungsi(self):
        """Menganalisis 'tulis("halo")' atau 'tulis(variabel)'."""
        nama_fungsi = self.token_sekarang
        self.maju()

        if not self.cocok(TipeToken.BUKA_KURUNG):
            raise PenguraiKesalahan("Diharapkan '(' setelah nama fungsi.")
        self.maju()

        # Untuk saat ini, hanya mendukung satu argumen
        argumen = self.urai_ekspresi()

        if not self.cocok(TipeToken.TUTUP_KURUNG):
            raise PenguraiKesalahan("Diharapkan ')' setelah argumen fungsi.")
        self.maju()

        return NodePanggilFungsi(NodePengenal(nama_fungsi), argumen)

    # --- Logika Parsing Ekspresi ---

    def urai_primary(self):
        """Level terendah: literal, pengenal, atau ekspresi dalam kurung."""
        token = self.token_sekarang

        if self.cocok(TipeToken.ANGKA):
            self.maju()
            return NodeAngka(token)
        elif self.cocok(TipeToken.TEKS):
            self.maju()
            return NodeTeks(token)
        elif self.cocok(TipeToken.PENGENAL):
            self.maju()
            return NodePengenal(token)
        elif self.cocok(TipeToken.BUKA_KURUNG):
            self.maju()
            node = self.urai_ekspresi()
            if not self.cocok(TipeToken.TUTUP_KURUNG):
                raise PenguraiKesalahan("Diharapkan ')' setelah ekspresi.")
            self.maju()
            return node

        raise PenguraiKesalahan(f"Token tidak terduga saat parsing: {token}")

    def urai_unary(self):
        """Mengurai operator unary: '-' dan 'tidak'."""
        if self.cocok(TipeToken.KURANG, TipeToken.TIDAK):
            operator = self.token_sekarang
            self.maju()
            operand = self.urai_unary()
            return NodeOperasiUnary(operator, operand)
        return self.urai_primary()

    def urai_perkalian(self):
        """Mengurai operator dengan preseden perkalian: *, /, %."""
        node = self.urai_unary()
        while self.cocok(TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO):
            operator = self.token_sekarang
            self.maju()
            kanan = self.urai_unary()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_penjumlahan(self):
        """Mengurai operator dengan preseden penjumlahan: +, -."""
        node = self.urai_perkalian()
        while self.cocok(TipeToken.TAMBAH, TipeToken.KURANG):
            operator = self.token_sekarang
            self.maju()
            kanan = self.urai_perkalian()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_perbandingan(self):
        """Mengurai operator perbandingan."""
        node = self.urai_penjumlahan()
        while self.cocok(TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_KECIL, TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL_SAMA, TipeToken.LEBIH_BESAR_SAMA):
            operator = self.token_sekarang
            self.maju()
            kanan = self.urai_penjumlahan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_dan(self):
        """Mengurai operator logika 'dan'."""
        node = self.urai_perbandingan()
        while self.cocok(TipeToken.DAN):
            operator = self.token_sekarang
            self.maju()
            kanan = self.urai_perbandingan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_atau(self):
        """Mengurai operator logika 'atau'."""
        node = self.urai_dan()
        while self.cocok(TipeToken.ATAU):
            operator = self.token_sekarang
            self.maju()
            kanan = self.urai_dan()
            node = NodeOperasiBiner(kiri=node, operator=operator, kanan=kanan)
        return node

    def urai_ekspresi(self):
        """Entry point untuk parsing ekspresi, dimulai dari preseden terendah."""
        return self.urai_atau()

    def urai(self):
        """Membangun AST dari daftar token."""
        daftar_pernyataan = []
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            pernyataan = self.urai_pernyataan()
            if pernyataan:
                daftar_pernyataan.append(pernyataan)
            # Jika tidak ada pernyataan, mungkin baris kosong, kita maju saja
            elif self.token_sekarang.tipe == TipeToken.AKHIR_BARIS:
                 self.maju()
            else:
                 # Jika bukan pernyataan atau akhir baris, ini bisa jadi error
                 # Untuk sekarang kita maju saja untuk menghindari loop tak terbatas
                 self.maju()

        return NodeProgram(daftar_pernyataan)
