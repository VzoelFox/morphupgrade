# transisi/lx.py
# Lexer untuk "Kelahiran Kembali MORPH"

from .morph_t import Token, TipeToken, KATA_KUNCI

class Leksikal:
    def __init__(self, sumber: str, nama_file: str = "<sumber>"):
        self.sumber = sumber
        self.nama_file = nama_file
        self.tokens = []
        self.awal = 0
        self.saat_ini = 0
        self.baris = 1
        self.kolom = 1
        self.daftar_kesalahan = []
        # Properti baru untuk melacak posisi awal token secara akurat
        self.baris_awal_token = 1
        self.kolom_awal_token = 1

    def buat_token(self):
        """Memindai seluruh kode sumber dan menghasilkan daftar token."""
        while not self._di_akhir():
            self.awal = self.saat_ini
            # Simpan posisi awal sebelum memindai token baru
            self.baris_awal_token = self.baris
            self.kolom_awal_token = self.kolom
            self._pindai_token()

        self.tokens.append(Token(TipeToken.ADS, b'\0', self.baris, self.kolom))
        return self.tokens, self.daftar_kesalahan

    def _di_akhir(self):
        return self.saat_ini >= len(self.sumber)

    def _maju(self):
        """Mengkonsumsi satu karakter dan mengembalikannya."""
        char = self.sumber[self.saat_ini]
        self.saat_ini += 1
        if char == '\n':
            self.baris += 1
            self.kolom = 1
        else:
            self.kolom += 1
        return char

    def _cocok(self, diharapkan):
        """Memeriksa apakah karakter saat ini cocok dengan yang diharapkan."""
        if self._di_akhir():
            return False
        if self.sumber[self.saat_ini] != diharapkan:
            return False
        self.saat_ini += 1
        self.kolom += 1
        return True

    def _intip(self):
        """Melihat karakter saat ini tanpa mengkonsumsinya."""
        if self._di_akhir():
            return '\0'
        return self.sumber[self.saat_ini]

    def _intip_berikutnya(self):
        """Melihat karakter setelah karakter saat ini."""
        if self.saat_ini + 1 >= len(self.sumber):
            return '\0'
        return self.sumber[self.saat_ini + 1]

    def _tambah_token(self, tipe, nilai_literal=None):
        if nilai_literal is None:
            teks = self.sumber[self.awal:self.saat_ini]
            nilai_literal = teks

        # Gunakan posisi awal yang sudah disimpan di loop `buat_token`
        self.tokens.append(Token(tipe, nilai_literal, self.baris_awal_token, self.kolom_awal_token))


    def _catat_kesalahan(self, pesan):
        # Simpan objek kesalahan yang lebih terstruktur
        info_kesalahan = {
            "pesan": pesan,
            "baris": self.baris,
            "kolom": self.kolom,
            "file": self.nama_file
        }
        self.daftar_kesalahan.append(info_kesalahan)

    def _pindai_token(self):
        char = self._maju()

        if char in ' \r\t':
            # Abaikan whitespace
            return
        elif char == '\n':
            self._tambah_token(TipeToken.AKHIR_BARIS)
        elif char == '(': self._tambah_token(TipeToken.KURUNG_BUKA)
        elif char == ')': self._tambah_token(TipeToken.KURUNG_TUTUP)
        elif char == '{': self._tambah_token(TipeToken.KURAWAL_BUKA)
        elif char == '}': self._tambah_token(TipeToken.KURAWAL_TUTUP)
        elif char == '[': self._tambah_token(TipeToken.SIKU_BUKA)
        elif char == ']': self._tambah_token(TipeToken.SIKU_TUTUP)
        elif char == '|': self._tambah_token(TipeToken.GARIS_PEMISAH)
        elif char == ',': self._tambah_token(TipeToken.KOMA)
        elif char == '.': self._tambah_token(TipeToken.TITIK)
        elif char == ';': self._tambah_token(TipeToken.TITIK_KOMA)
        elif char == ':': self._tambah_token(TipeToken.TITIK_DUA)
        elif char == '-': self._tambah_token(TipeToken.KURANG)
        elif char == '+': self._tambah_token(TipeToken.TAMBAH)
        elif char == '*': self._tambah_token(TipeToken.KALI)
        elif char == '/':
            if self._cocok('/'):
                # Komentar, abaikan sampai akhir baris
                while self._intip() != '\n' and not self._di_akhir():
                    self._maju()
            else:
                self._tambah_token(TipeToken.BAGI)
        elif char == '^': self._tambah_token(TipeToken.PANGKAT)
        elif char == '%': self._tambah_token(TipeToken.MODULO)
        elif char == '!':
            self._tambah_token(TipeToken.TIDAK_SAMA if self._cocok('=') else TipeToken.TIDAK)
        elif char == '=':
            self._tambah_token(TipeToken.SAMA_DENGAN if self._cocok('=') else TipeToken.SAMADENGAN)
        elif char == '<':
            self._tambah_token(TipeToken.KURANG_SAMA if self._cocok('=') else TipeToken.KURANG_DARI)
        elif char == '>':
            self._tambah_token(TipeToken.LEBIH_SAMA if self._cocok('=') else TipeToken.LEBIH_DARI)
        elif char == '#':
            # Komentar, abaikan sampai akhir baris
            while self._intip() != '\n' and not self._di_akhir():
                self._maju()
        elif char == '"':
            self._teks()
        elif self._is_digit(char):
            self._angka()
        elif self._is_alpha(char):
            self._nama()
        else:
            self._catat_kesalahan(f"Karakter '{char}' tidak dikenal.")
            self._tambah_token(TipeToken.TIDAK_DIKENAL)

    def _teks(self):
        nilai_karakter = []
        while self._intip() != '"' and not self._di_akhir():
            # Cek newline di dalam string untuk akurasi baris di token berikutnya
            if self._intip() == '\n':
                self._maju()
                nilai_karakter.append('\n')
                continue

            karakter = self._maju()
            if karakter == '\\':
                if self._di_akhir():
                    self._catat_kesalahan("Teks tidak ditutup setelah escape character '\\'.")
                    break

                karakter_berikutnya = self._maju()
                peta_escape = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}

                # Jika karakter berikutnya tidak ada di peta, anggap literal (contoh: \a)
                nilai_karakter.append(peta_escape.get(karakter_berikutnya, f"\\{karakter_berikutnya}"))
            else:
                nilai_karakter.append(karakter)

        if self._di_akhir():
            self._catat_kesalahan("Teks tidak ditutup.")
            return

        # Konsumsi tanda kutip penutup
        self._maju()

        nilai_final = "".join(nilai_karakter)
        self._tambah_token(TipeToken.TEKS, nilai_final)


    def _angka(self):
        while self._is_digit(self._intip()):
            self._maju()

        if self._intip() == '.' and self._is_digit(self._intip_berikutnya()):
            self._maju() # Konsumsi '.'
            while self._is_digit(self._intip()):
                self._maju()

        nilai_str = self.sumber[self.awal:self.saat_ini]
        try:
            nilai = float(nilai_str)
            if nilai.is_integer():
                nilai = int(nilai)
            self._tambah_token(TipeToken.ANGKA, nilai)
        except ValueError:
            self._catat_kesalahan(f"Format angka tidak valid: {nilai_str}")
            self._tambah_token(TipeToken.TIDAK_DIKENAL, nilai_str)

    def _nama(self):
        while self._is_alpha_numeric(self._intip()):
            self._maju()

        teks = self.sumber[self.awal:self.saat_ini]
        tipe = KATA_KUNCI.get(teks)

        if tipe is None:
            tipe = TipeToken.NAMA

        # Handle boolean and nil literals
        if tipe == TipeToken.BENAR:
            self._tambah_token(tipe, True)
        elif tipe == TipeToken.SALAH:
            self._tambah_token(tipe, False)
        elif tipe == TipeToken.NIL:
            self._tambah_token(tipe, None)
        else:
            self._tambah_token(tipe)

    def _is_digit(self, char):
        return '0' <= char <= '9'

    def _is_alpha(self, char):
        return ('a' <= char <= 'z') or ('A' <= char <= 'Z') or char == '_'

    def _is_alpha_numeric(self, char):
        return self._is_alpha(char) or self._is_digit(char)
