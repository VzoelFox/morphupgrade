# morph_engine/leksikal.py
from .token_morph import Token, TipeToken

KATA_KUNCI = {
    "biar": TipeToken.BIAR,
    "tetap": TipeToken.TETAP,
    "tulis": TipeToken.TULIS,
    "ambil": TipeToken.AMBIL,
    "dari": TipeToken.DARI,
    "buka": TipeToken.BUKA,
    "tutup": TipeToken.TUTUP,
}

class Leksikal:
    def __init__(self, teks):
        self.teks = teks
        self.posisi = 0
        self.karakter_sekarang = self.teks[self.posisi] if self.teks else None

    def maju(self):
        """Memajukan posisi baca dan memperbarui karakter_sekarang."""
        self.posisi += 1
        if self.posisi < len(self.teks):
            self.karakter_sekarang = self.teks[self.posisi]
        else:
            self.karakter_sekarang = None

    def lewati_spasi(self):
        """Melewati semua karakter spasi atau tab."""
        while self.karakter_sekarang is not None and self.karakter_sekarang.isspace():
            self.maju()

    def lewati_komentar(self):
        """Melewati satu baris komentar (dimulai dengan #)."""
        while self.karakter_sekarang is not None and self.karakter_sekarang != '\n':
            self.maju()

    def baca_pengenal(self):
        """Membaca sebuah pengenal atau kata kunci."""
        hasil = ""
        while self.karakter_sekarang is not None and (self.karakter_sekarang.isalnum() or self.karakter_sekarang == '_'):
            hasil += self.karakter_sekarang
            self.maju()
        return hasil

    def baca_teks(self):
        """Membaca sebuah literal teks di dalam tanda kutip."""
        self.maju() # Lewati " pembuka
        hasil = ""
        while self.karakter_sekarang is not None and self.karakter_sekarang != '"':
            hasil += self.karakter_sekarang
            self.maju()
        self.maju() # Lewati " penutup
        return hasil

    def buat_token(self):
        """Mengubah teks mentah menjadi daftar token."""
        daftar_token = []
        while self.karakter_sekarang is not None:
            if self.karakter_sekarang.isspace():
                self.lewati_spasi()
                continue

            if self.karakter_sekarang == '#':
                self.lewati_komentar()
                continue

            if self.karakter_sekarang.isalpha():
                pengenal = self.baca_pengenal()
                tipe_token = KATA_KUNCI.get(pengenal, TipeToken.PENGENAL)
                daftar_token.append(Token(tipe_token, pengenal))

            elif self.karakter_sekarang == '"':
                nilai_teks = self.baca_teks()
                daftar_token.append(Token(TipeToken.TEKS, nilai_teks))

            elif self.karakter_sekarang == '=':
                daftar_token.append(Token(TipeToken.SAMA_DENGAN, '='))
                self.maju()

            elif self.karakter_sekarang == '(':
                daftar_token.append(Token(TipeToken.BUKA_KURUNG, '('))
                self.maju()

            elif self.karakter_sekarang == ')':
                daftar_token.append(Token(TipeToken.TUTUP_KURUNG, ')'))
                self.maju()

            else:
                # Untuk saat ini, abaikan karakter yang tidak dikenal
                # print(f"Karakter tidak dikenal diabaikan: {self.karakter_sekarang}")
                self.maju()

        daftar_token.append(Token(TipeToken.ADS)) # Akhir Dari Segalanya
        return daftar_token
