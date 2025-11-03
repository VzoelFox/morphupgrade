# morph_engine/pengurai.py
from .token_morph import TipeToken
from .node_ast import (
    NodeProgram, NodeDeklarasiVariabel, NodePanggilFungsi,
    NodePengenal, NodeTeks
)

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

    def urai_pernyataan(self):
        """Menganalisis satu pernyataan (statement)."""
        if self.token_sekarang.tipe in (TipeToken.BIAR, TipeToken.TETAP):
            return self.urai_deklarasi_variabel()

        if self.token_sekarang.tipe == TipeToken.TULIS:
             return self.urai_panggil_fungsi()

        # Jika token tidak dikenali sebagai awal statement, kembalikan None
        return None


    def urai_deklarasi_variabel(self):
        """Menganalisis 'biar nama = nilai' atau 'tetap nama = nilai'."""
        jenis_deklarasi = self.token_sekarang
        self.maju()

        nama_variabel = NodePengenal(self.token_sekarang)
        self.maju() # Lewati pengenal

        if self.token_sekarang.tipe != TipeToken.SAMA_DENGAN:
            raise SyntaxError("Error Sintaks: Diharapkan ada '=' setelah nama variabel.")
        self.maju() # Lewati '='

        # Nilai bisa berupa teks atau pengenal
        if self.token_sekarang.tipe == TipeToken.TEKS:
            nilai = NodeTeks(self.token_sekarang)
            self.maju()
            return NodeDeklarasiVariabel(jenis_deklarasi, nama_variabel, nilai)
        else:
             raise SyntaxError("Error Sintaks: Diharapkan ada nilai (teks) setelah '='.")


    def urai_panggil_fungsi(self):
        """Menganalisis 'tulis("halo")' atau 'tulis(variabel)'."""
        nama_fungsi = self.token_sekarang # Token TULIS itu sendiri
        self.maju()

        if self.token_sekarang.tipe != TipeToken.BUKA_KURUNG:
            raise SyntaxError("Error Sintaks: Diharapkan ada '(' setelah nama fungsi.")
        self.maju()

        # Argumen bisa berupa teks atau pengenal (nama variabel)
        if self.token_sekarang.tipe == TipeToken.TEKS:
            argumen = NodeTeks(self.token_sekarang)
            self.maju()
        elif self.token_sekarang.tipe == TipeToken.PENGENAL:
            argumen = NodePengenal(self.token_sekarang)
            self.maju()
        else:
            raise SyntaxError("Error Sintaks: Diharapkan ada argumen (teks atau variabel) di dalam fungsi.")

        if self.token_sekarang.tipe != TipeToken.TUTUP_KURUNG:
            raise SyntaxError("Error Sintaks: Diharapkan ada ')' setelah argumen fungsi.")
        self.maju()

        # Menggunakan nilai dari token TULIS ('tulis') sebagai nama fungsi
        return NodePanggilFungsi(NodePengenal(nama_fungsi), argumen)


    def urai(self):
        """Membangun AST dari daftar token."""
        daftar_pernyataan = []
        while self.token_sekarang is not None and self.token_sekarang.tipe != TipeToken.ADS:
            pernyataan = self.urai_pernyataan()
            if pernyataan:
                daftar_pernyataan.append(pernyataan)
            else:
                self.maju()

        return NodeProgram(daftar_pernyataan)
