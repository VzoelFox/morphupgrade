# morph_engine/lx.py

# Changelog:
# - PATCH-021: (Kelahiran Kembali) Mengganti nama file ini dari leksikal.py
#              dan memperbarui impor agar sesuai dengan filosofi baru.
# - PATCH-016: Menambahkan keyword 'fungsi', 'kembalikan', dan 'nil' ke dalam leksikal.
# - PATCH-003: Memperketat validasi angka untuk menolak format seperti '.123' dan '123.'.
# - FIX-001: Menambahkan pembuatan token AKHIR_BARIS agar parser dapat
#            memisahkan statement multi-baris dengan benar.
# - FIX-002: Memastikan token BENAR/SALAH memiliki nilai boolean asli
#            (True/False), bukan string.
# TODO: Standarisasi pesan LeksikalKesalahan di sprint mendatang.

from .morph_t import Token, TipeToken
from .error_utils import ErrorFormatter

# Memperbarui kamus kata kunci dengan operator logika
KATA_KUNCI = {
    "biar": TipeToken.BIAR,
    "tetap": TipeToken.TETAP,
    "tulis": TipeToken.TULIS,
    "ambil": TipeToken.AMBIL,
    "ambil_semua": TipeToken.AMBIL_SEMUA,
    "ambil_sebagian": TipeToken.AMBIL_SEBAGIAN,
    "dari": TipeToken.DARI,
    "sebagai": TipeToken.SEBAGAI,
    "pinjam": TipeToken.PINJAM,
    "buka": TipeToken.BUKA,
    "tutup": TipeToken.TUTUP,
    "dan": TipeToken.DAN,
    "atau": TipeToken.ATAU,
    "tidak": TipeToken.TIDAK,
    "benar": TipeToken.BENAR,
    "salah": TipeToken.SALAH,
    "jika": TipeToken.JIKA,
    "maka": TipeToken.MAKA,
    "akhir": TipeToken.AKHIR,
    "lain": TipeToken.LAIN,
    "fungsi": TipeToken.FUNGSI,
    "kembalikan": TipeToken.KEMBALIKAN,
    "nil": TipeToken.NIL,
    "selama": TipeToken.SELAMA,
    "pilih": TipeToken.PILIH,
    "ketika": TipeToken.KETIKA,
    "lainnya": TipeToken.LAINNYA,
}

class LeksikalKesalahan(Exception):
    def __init__(self, pesan, baris, kolom):
        pesan_terformat = ErrorFormatter.format_leksikal_error(baris, kolom, pesan)
        super().__init__(pesan_terformat)
        self.baris = baris
        self.kolom = kolom

class Leksikal:
    def __init__(self, teks):
        self.teks = teks
        self.posisi = 0
        self.baris = 1
        self.kolom = 1
        self.karakter_sekarang = self.teks[self.posisi] if self.teks else None

    def maju(self):
        """Memajukan posisi baca dan memperbarui karakter_sekarang."""
        if self.karakter_sekarang == '\n':
            self.baris += 1
            self.kolom = 1
        else:
            self.kolom += 1

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
        """Melewati semua karakter spasi atau tab, berhenti di newline."""
        while self.karakter_sekarang is not None and self.karakter_sekarang.isspace() and self.karakter_sekarang != '\n':
            self.maju()

    def lewati_komentar(self):
        """Melewati satu baris komentar (dimulai dengan #)."""
        while self.karakter_sekarang is not None and self.karakter_sekarang != '\n':
            self.maju()

    def baca_angka(self):
        """
        Membaca sebuah angka, bisa integer atau float.
        Memvalidasi format float agar sesuai spesifikasi (harus ada angka sebelum dan sesudah titik).
        Mencegah multi-dot (misal: 1.2.3).
        """
        hasil_str = ""
        ada_titik = False
        baris_awal, kolom_awal = self.baris, self.kolom

        while self.karakter_sekarang is not None and (self.karakter_sekarang.isdigit() or self.karakter_sekarang == '.'):
            if self.karakter_sekarang == '.':
                if ada_titik:
                    # Sudah ada titik sebelumnya, ini adalah format tidak valid (multi-dot)
                    raise LeksikalKesalahan(
                        "Format angka float tidak valid: multiple titik desimal tidak diperbolehkan",
                        baris_awal, kolom_awal
                    )
                ada_titik = True
            hasil_str += self.karakter_sekarang
            self.maju()

        # Validasi setelah selesai membaca
        if ada_titik:
            if not hasil_str.replace('.', '', 1).isdigit():
                 raise LeksikalKesalahan(
                    f"Token angka tidak valid: '{hasil_str}'",
                    baris_awal, kolom_awal
                )
            if hasil_str.startswith('.') or hasil_str.endswith('.'):
                raise LeksikalKesalahan(
                    "Format angka float tidak valid: harus ada digit sebelum dan sesudah titik desimal",
                    baris_awal, kolom_awal
                )
            return Token(TipeToken.ANGKA, float(hasil_str), baris_awal, kolom_awal)
        else:
            return Token(TipeToken.ANGKA, int(hasil_str), baris_awal, kolom_awal)

    def baca_pengenal(self):
        """Membaca sebuah pengenal atau kata kunci."""
        hasil = ""
        baris_awal, kolom_awal = self.baris, self.kolom
        while self.karakter_sekarang is not None and (self.karakter_sekarang.isalnum() or self.karakter_sekarang == '_'):
            hasil += self.karakter_sekarang
            self.maju()
        tipe_token = KATA_KUNCI.get(hasil, TipeToken.PENGENAL)

        # FIXED: FIX-002 - Memberikan nilai boolean pada token BENAR/SALAH.
        # Ini memastikan token membawa nilai semantik yang benar, bukan hanya string.
        nilai_hasil = True if hasil == 'benar' else (False if hasil == 'salah' else hasil)

        return Token(tipe_token, nilai_hasil, baris_awal, kolom_awal)

    def baca_teks(self):
        """
        Membaca sebuah literal teks di dalam tanda kutip.
        Mendukung escape sequence: \\", \\\\, dan \\n.
        Memvalidasi string yang tidak ditutup sebelum EOF.
        """
        baris_awal, kolom_awal = self.baris, self.kolom
        self.maju() # Lewati " pembuka
        hasil = ""
        while self.karakter_sekarang is not None and self.karakter_sekarang != '"':
            if self.karakter_sekarang == '\\':
                self.maju() # Lewati backslash
                if self.karakter_sekarang == '"':
                    hasil += '"'
                elif self.karakter_sekarang == '\\':
                    hasil += '\\'
                elif self.karakter_sekarang == 'n':
                    hasil += '\n'
                else:
                    # Escape sequence tidak dikenal, bisa dianggap sebagai literal backslash + karakter
                    hasil += '\\' + self.karakter_sekarang
            else:
                hasil += self.karakter_sekarang
            self.maju()

        if self.karakter_sekarang is None:
            # String tidak ditutup, kembalikan sebagai token TIDAK_DIKENAL
            return Token(TipeToken.TIDAK_DIKENAL, f'"{hasil}', baris_awal, kolom_awal)

        self.maju() # Lewati " penutup
        return Token(TipeToken.TEKS, hasil, baris_awal, kolom_awal)

    def buat_token(self):
        """Mengubah teks mentah menjadi daftar token."""
        daftar_token = []
        while self.karakter_sekarang is not None:
            baris_awal, kolom_awal = self.baris, self.kolom
            # FIXED: FIX-001 - Menambahkan pembuatan token AKHIR_BARIS.
            # Cek untuk newline harus mendahului cek isspace() umum
            # agar newline tidak dilewati begitu saja.
            if self.karakter_sekarang == '\n':
                token = Token(TipeToken.AKHIR_BARIS, '\n', baris_awal, kolom_awal)
                daftar_token.append(token)
                self.maju()
                continue

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
                daftar_token.append(self.baca_pengenal())
                continue

            if self.karakter_sekarang == '"':
                daftar_token.append(self.baca_teks())
                continue

            # Handle operator dua karakter
            if self.karakter_sekarang == '=' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.SAMA_DENGAN_SAMA, '==', baris_awal, kolom_awal))
                continue

            if self.karakter_sekarang == '!' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.TIDAK_SAMA, '!=', baris_awal, kolom_awal))
                continue

            if self.karakter_sekarang == '>' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.LEBIH_BESAR_SAMA, '>=', baris_awal, kolom_awal))
                continue

            if self.karakter_sekarang == '<' and self.intip() == '=':
                self.maju()
                self.maju()
                daftar_token.append(Token(TipeToken.LEBIH_KECIL_SAMA, '<=', baris_awal, kolom_awal))
                continue

            # Handle koma secara eksplisit
            if self.karakter_sekarang == ',':
                token = Token(TipeToken.KOMA, ',', baris_awal, kolom_awal)
                daftar_token.append(token)
                self.maju()
                continue

            # Handle operator satu karakter
            try:
                # Mencari TipeToken yang cocok dengan karakter sekarang
                tipe_token = TipeToken(self.karakter_sekarang)
                token = Token(tipe_token, self.karakter_sekarang, baris_awal, kolom_awal)
                daftar_token.append(token)
                self.maju()
                continue
            except ValueError:
                # Jika karakter tidak cocok dengan operator atau simbol yang dikenal,
                # buat token TIDAK_DIKENAL dan lanjutkan.
                token = Token(
                    TipeToken.TIDAK_DIKENAL,
                    self.karakter_sekarang,
                    baris_awal,
                    kolom_awal
                )
                daftar_token.append(token)
                self.maju()
                continue

        daftar_token.append(Token(TipeToken.ADS, baris=self.baris, kolom=self.kolom)) # Akhir Dari Segalanya
        return daftar_token
