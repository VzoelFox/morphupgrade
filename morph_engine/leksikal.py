# morph_engine/leksikal.py
from .token_morph import Token, TipeToken

# Memperbarui kamus kata kunci dengan operator logika
KATA_KUNCI = {
    "biar": TipeToken.BIAR,
    "tetap": TipeToken.TETAP,
    "tulis": TipeToken.TULIS,
    "ambil": TipeToken.AMBIL,
    "dari": TipeToken.DARI,
    "buka": TipeToken.BUKA,
    "tutup": TipeToken.TUTUP,
    "dan": TipeToken.DAN,
    "atau": TipeToken.ATAU,
    "tidak": TipeToken.TIDAK,
}

class LeksikalKesalahan(Exception):
    pass

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

    def intip(self):
        """Melihat karakter berikutnya tanpa memajukan posisi."""
        posisi_intip = self.posisi + 1
        if posisi_intip < len(self.teks):
            return self.teks[posisi_intip]
        return None

    def lewati_spasi(self):
        """Melewati semua karakter spasi atau tab."""
        while self.karakter_sekarang is not None and self.karakter_sekarang.isspace():
            self.maju()

    def lewati_komentar(self):
        """Melewati satu baris komentar (dimulai dengan #)."""
        while self.karakter_sekarang is not None and self.karakter_sekarang != '\n':
            self.maju()

    def baca_angka(self):
        """
        Membaca sebuah angka, bisa integer atau float.
        Memvalidasi format float agar sesuai spesifikasi (harus ada angka sebelum dan sesudah titik).
        """
        hasil_str = ""
        ada_titik = False
        while self.karakter_sekarang is not None and (self.karakter_sekarang.isdigit() or self.karakter_sekarang == '.'):
            if self.karakter_sekarang == '.':
                if ada_titik: break
                ada_titik = True
            hasil_str += self.karakter_sekarang
            self.maju()

        if ada_titik:
            if hasil_str.startswith('.') or hasil_str.endswith('.'):
                raise LeksikalKesalahan(f"Format angka float tidak valid: '{hasil_str}'")
            return Token(TipeToken.ANGKA, float(hasil_str))
        else:
            return Token(TipeToken.ANGKA, int(hasil_str))

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

            if self.karakter_sekarang.isdigit() or (self.karakter_sekarang == '.' and self.intip() and self.intip().isdigit()):
                daftar_token.append(self.baca_angka())
                continue

            if self.karakter_sekarang.isalpha() or self.karakter_sekarang == '_':
                pengenal = self.baca_pengenal()
                tipe_token = KATA_KUNCI.get(pengenal, TipeToken.PENGENAL)
                daftar_token.append(Token(tipe_token, pengenal))
                continue

            if self.karakter_sekarang == '"':
                nilai_teks = self.baca_teks()
                daftar_token.append(Token(TipeToken.TEKS, nilai_teks))
                continue

            # Handle operator dua karakter
            if self.karakter_sekarang == '=' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.SAMA_DENGAN_SAMA, '=='))
                continue

            if self.karakter_sekarang == '!' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.TIDAK_SAMA, '!='))
                continue

            if self.karakter_sekarang == '>' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.LEBIH_BESAR_SAMA, '>='))
                continue

            if self.karakter_sekarang == '<' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.LEBIH_KECIL_SAMA, '<='))
                continue

            # Handle operator satu karakter
            try:
                # Mencari TipeToken yang cocok dengan karakter sekarang
                tipe_token = TipeToken(self.karakter_sekarang)
                daftar_token.append(Token(tipe_token, self.karakter_sekarang))
                self.maju()
                continue
            except ValueError:
                # Jika tidak ada TipeToken yang cocok
                raise LeksikalKesalahan(f"Karakter tidak dikenal: '{self.karakter_sekarang}'")

        daftar_token.append(Token(TipeToken.ADS)) # Akhir Dari Segalanya
        return daftar_token
