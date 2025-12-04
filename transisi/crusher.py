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
            if self._cocok(TipeToken.AKHIR_BARIS):
                continue

            pernyataan = self._deklarasi()
            if pernyataan:
                daftar_pernyataan.append(pernyataan)

        if self.daftar_kesalahan:
            return None

        return ast.Bagian(daftar_pernyataan)

    def _deklarasi(self):
        if self._cocok(TipeToken.PINJAM):
            return self._pernyataan_pinjam()
        if self._cocok(TipeToken.KELAS):
            return self._deklarasi_kelas()
        if self._cocok(TipeToken.AMBIL_SEMUA):
            return self._pernyataan_ambil_semua()
        # Refactor: Cek 'DARI' dulu untuk sintaks baru
        if self._cocok(TipeToken.DARI):
            # Bisa jadi 'dari ... ambil sebagian ...'
            return self._pernyataan_dari_ambil()

        if self._cocok(TipeToken.WARNAI):
            return self._pernyataan_warnai()

        # Backward compatibility (Opsional, tapi kita hapus sesuai instruksi refactor)
        if self._cocok(TipeToken.AMBIL_SEBAGIAN):
            return self._pernyataan_ambil_sebagian()
        if self._cocok(TipeToken.TIPE):
            return self._deklarasi_tipe()
        if self._cocok(TipeToken.ASINK):
            return self._deklarasi_fungsi_asink()
        if self._cocok(TipeToken.FUNGSI):
            return self._deklarasi_fungsi("fungsi")
        if self._cocok(TipeToken.BIAR, TipeToken.TETAP):
            return self._deklarasi_variabel()
        return self._pernyataan()

    def _deklarasi_kelas(self):
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama setelah 'kelas'.")

        superkelas = None
        if self._cocok(TipeToken.WARISI):
            nama_super = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama superkelas setelah 'warisi'.")
            superkelas = ast.Identitas(nama_super)

        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah nama kelas.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        metode = []
        while not self._periksa(TipeToken.AKHIR) and not self._di_akhir():
            if self._cocok(TipeToken.AKHIR_BARIS):
                continue

            if self._cocok(TipeToken.ASINK):
                metode.append(self._deklarasi_fungsi_asink())
            elif self._cocok(TipeToken.FUNGSI):
                metode.append(self._deklarasi_fungsi("metode"))
            else:
                self._kesalahan(self._intip(), "Hanya deklarasi 'fungsi' atau 'asink fungsi' yang diizinkan di dalam 'kelas'.")
                # Lakukan 'maju' untuk menghindari infinite loop jika ada token yang tidak valid
                self._maju()

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup 'kelas'.")
        return ast.Kelas(nama, superkelas, metode)

    def _deklarasi_fungsi_asink(self):
        self._konsumsi(TipeToken.FUNGSI, "Dibutuhkan 'fungsi' setelah 'asink'.")
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama setelah 'asink fungsi'.")
        self._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah nama fungsi.")
        parameter = []
        if not self._periksa(TipeToken.KURUNG_TUTUP):
            token_param = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE), "Dibutuhkan nama parameter.")
            parameter.append(Token(TipeToken.NAMA, token_param.nilai, token_param.baris, token_param.kolom))
            while self._cocok(TipeToken.KOMA):
                token_param = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE), "Dibutuhkan nama parameter.")
                parameter.append(Token(TipeToken.NAMA, token_param.nilai, token_param.baris, token_param.kolom))
        self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah parameter.")

        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' sebelum badan fungsi.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup fungsi.")
        return ast.FungsiAsinkDeklarasi(nama, parameter, ast.Bagian(badan))

    def _deklarasi_fungsi(self, jenis: str):
        # Izinkan nama fungsi berupa Keyword Operator (misal: tambah, kurang)
        # Ini memungkinkan override operator atau fungsi bernama 'tambah'

        # Kita cek apakah token berikutnya adalah NAMA atau salah satu Operator
        token_nama = self._intip()
        if token_nama.tipe in [
            TipeToken.NAMA,
            TipeToken.TAMBAH, TipeToken.KURANG, TipeToken.KALI, TipeToken.BAGI,
            TipeToken.MODULO, TipeToken.PANGKAT,
            TipeToken.TULIS, TipeToken.AMBIL, TipeToken.MAKA, TipeToken.DARI
            # Tambahkan token lain yang valid sebagai nama fungsi jika perlu
        ]:
            nama = self._maju()
            # Normalisasi menjadi token NAMA agar Compiler tidak bingung
            nama = Token(TipeToken.NAMA, nama.nilai, nama.baris, nama.kolom)
        else:
            # Fallback ke _konsumsi untuk error reporting standar jika bukan yang diharapkan
            nama = self._konsumsi(TipeToken.NAMA, f"Dibutuhkan nama setelah '{jenis}'.")

        self._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah nama fungsi.")
        parameter = []
        if not self._periksa(TipeToken.KURUNG_TUTUP):
            token_param = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE), "Dibutuhkan nama parameter.")
            parameter.append(Token(TipeToken.NAMA, token_param.nilai, token_param.baris, token_param.kolom))
            while self._cocok(TipeToken.KOMA):
                token_param = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE), "Dibutuhkan nama parameter.")
                parameter.append(Token(TipeToken.NAMA, token_param.nilai, token_param.baris, token_param.kolom))
        self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah parameter.")

        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' sebelum badan fungsi.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup fungsi.")
        return ast.FungsiDeklarasi(nama, parameter, ast.Bagian(badan))

    def _deklarasi_tipe(self):
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama tipe setelah kata kunci 'tipe'.")
        self._konsumsi(TipeToken.SAMADENGAN, "Dibutuhkan '=' setelah nama tipe.")

        daftar_varian = []
        # Parse varian pertama
        nama_varian = self._konsumsi(TipeToken.NAMA, "Dibutuhkan setidaknya satu nama varian setelah '='.")
        parameter_varian = []
        if self._cocok(TipeToken.KURUNG_BUKA):
            if not self._periksa(TipeToken.KURUNG_TUTUP):
                parameter_varian.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama parameter untuk varian."))
                while self._cocok(TipeToken.KOMA):
                    parameter_varian.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama parameter untuk varian."))
            self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah parameter varian.")
        daftar_varian.append(ast.Varian(nama_varian, parameter_varian))

        # Parse varian berikutnya (jika ada)
        while self._cocok(TipeToken.GARIS_PEMISAH):
            nama_varian = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama varian setelah '|'.")
            parameter_varian = []
            if self._cocok(TipeToken.KURUNG_BUKA):
                if not self._periksa(TipeToken.KURUNG_TUTUP):
                    parameter_varian.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama parameter untuk varian."))
                    while self._cocok(TipeToken.KOMA):
                        parameter_varian.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama parameter untuk varian."))
                self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah parameter varian.")
            daftar_varian.append(ast.Varian(nama_varian, parameter_varian))

        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah deklarasi tipe.")
        return ast.TipeDeklarasi(nama, daftar_varian)

    def _deklarasi_variabel(self):
        jenis_deklarasi = self._sebelumnya()
        # Izinkan keyword tertentu sebagai nama variabel (TIPE, JENIS, AMBIL)
        token_nama = self._intip()
        if token_nama.tipe in [TipeToken.NAMA, TipeToken.TIPE, TipeToken.JENIS, TipeToken.AMBIL]:
             nama = self._maju()
             # Normalisasi token menjadi NAMA agar konsisten
             nama = Token(TipeToken.NAMA, nama.nilai, nama.baris, nama.kolom)
        else:
             nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel.")

        nilai = None
        if self._cocok(TipeToken.SAMADENGAN):
            nilai = self._ekspresi()

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah deklarasi variabel.")
        return ast.DeklarasiVariabel(jenis_deklarasi, nama, nilai)

    def _pernyataan(self):
        if self._cocok(TipeToken.LEMPARKAN):
            return self._pernyataan_lemparkan()
        if self._cocok(TipeToken.COBA):
            return self._pernyataan_coba()
        if self._cocok(TipeToken.JODOHKAN):
            return self._pernyataan_jodohkan()
        if self._cocok(TipeToken.PILIH):
            return self._pernyataan_pilih()
        if self._cocok(TipeToken.JIKA):
            return self._pernyataan_jika()
        if self._cocok(TipeToken.SELAMA):
            return self._pernyataan_selama()
        if self._cocok(TipeToken.UBAH):
            return self._pernyataan_assignment()
        if self._cocok(TipeToken.TULIS):
            return self._pernyataan_tulis()
        if self._cocok(TipeToken.KEMBALI, TipeToken.KEMBALIKAN):
            return self._pernyataan_kembalikan()
        if self._cocok(TipeToken.BERHENTI):
            return self._pernyataan_berhenti()
        if self._cocok(TipeToken.LANJUTKAN):
            return self._pernyataan_lanjutkan()
        if self._cocok(TipeToken.KURAWAL_BUKA):
            return ast.Bagian(self._blok())
        return self._pernyataan_ekspresi()

    def _pernyataan_lemparkan(self):
        ekspresi = self._ekspresi()
        jenis = None

        # Dukungan sugar syntax: lemparkan "Pesan" jenis "Tipe"
        if self._cocok(TipeToken.JENIS):
            jenis = self._ekspresi()

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah 'lemparkan'.")
        return ast.Lemparkan(ekspresi, jenis)

    def _pernyataan_coba(self):
        # 'coba' sudah dikonsumsi
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'coba'.")

        blok_coba = self._blok_pernyataan_hingga(TipeToken.TANGKAP, TipeToken.AKHIRNYA, TipeToken.AKHIR)

        daftar_tangkap = []
        while self._cocok(TipeToken.TANGKAP):
            nama_error = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel error setelah 'tangkap'.")

            kondisi_jaga = None
            # Dukungan guard: tangkap e jika e.jenis == "..."
            if self._cocok(TipeToken.JIKA):
                kondisi_jaga = self._ekspresi()

            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah deklarasi 'tangkap'.")
            badan_tangkap = self._blok_pernyataan_hingga(TipeToken.TANGKAP, TipeToken.AKHIRNYA, TipeToken.AKHIR)
            daftar_tangkap.append(ast.Tangkap(nama_error, kondisi_jaga, ast.Bagian(badan_tangkap)))

        blok_akhirnya = None
        if self._cocok(TipeToken.AKHIRNYA):
            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'akhirnya'.")
            badan_akhirnya = self._blok_pernyataan_hingga(TipeToken.AKHIR)
            blok_akhirnya = ast.Bagian(badan_akhirnya)

        self._konsumsi(TipeToken.AKHIR, "Blok 'coba' harus ditutup dengan 'akhir'.")

        # Validasi minimal satu tangkap atau satu akhirnya
        if not daftar_tangkap and not blok_akhirnya:
             self._kesalahan(self._sebelumnya(), "Blok 'coba' harus memiliki setidaknya satu 'tangkap' atau 'akhirnya'.")

        return ast.CobaTangkap(ast.Bagian(blok_coba), daftar_tangkap, blok_akhirnya)

    def _pernyataan_assignment(self):
        # 'ubah' sudah dikonsumsi.
        # Kita parse sebuah ekspresi `panggilan` yang bisa berupa `nama`, `nama[0]`, atau `nama.prop`.
        target_expr = self._panggilan()

        # Periksa apakah targetnya adalah sesuatu yang bisa di-assign.
        # Ini mencegah sintaks seperti `ubah fungsi() = nilai`.
        if not isinstance(target_expr, (ast.Identitas, ast.Akses, ast.AmbilProperti)):
            # Kita menggunakan `_sebelumnya()` karena `_panggilan` akan mengkonsumsi token terakhir dari ekspresi target.
            raise self._kesalahan(self._sebelumnya(), "Target assignment tidak valid. Hanya variabel, akses indeks, atau properti yang bisa diubah.")

        self._konsumsi(TipeToken.SAMADENGAN, "Dibutuhkan '=' setelah target untuk assignment 'ubah'.")
        nilai = self._ekspresi()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah nilai assignment.")

        return ast.Assignment(target_expr, nilai)

    def _pernyataan_selama(self):
        token_selama = self._sebelumnya()
        kondisi = self._ekspresi()
        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah kondisi 'selama'.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup loop 'selama'.")
        return ast.Selama(token_selama, kondisi, ast.Bagian(badan))

    def _pernyataan_berhenti(self):
        token = self._sebelumnya()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'berhenti'.")
        return ast.Berhenti(token)

    def _pernyataan_lanjutkan(self):
        token = self._sebelumnya()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'lanjutkan'.")
        return ast.Lanjutkan(token)

    def _pernyataan_kembalikan(self):
        token_kunci = self._sebelumnya()
        nilai = None
        if not self._periksa(TipeToken.AKHIR_BARIS) and not self._periksa(TipeToken.TITIK_KOMA):
            nilai = self._ekspresi()

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah nilai kembalian.")
        return ast.PernyataanKembalikan(token_kunci, nilai)

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

    def _pernyataan_warnai(self):
        # warnai <ekspresi> maka ... akhir
        warna_expr = self._ekspresi()
        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah kode warna.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)
        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup blok warnai.")

        return ast.Warnai(warna_expr, ast.Bagian(badan))

    def _pernyataan_jika(self):
        kondisi = self._ekspresi()
        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah kondisi 'jika'.")
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        blok_maka = self._blok_pernyataan_hingga(TipeToken.AKHIR, TipeToken.LAIN)

        rantai_lain_jika = []
        blok_lain = None

        while self._cocok(TipeToken.LAIN):
            if self._cocok(TipeToken.JIKA):
                kondisi_lain_jika = self._ekspresi()
                self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah 'lain jika'.")
                self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

                blok_lain_jika = self._blok_pernyataan_hingga(TipeToken.AKHIR, TipeToken.LAIN)
                rantai_lain_jika.append((kondisi_lain_jika, ast.Bagian(blok_lain_jika)))
            else:
                self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional
                blok_lain = self._blok_pernyataan_hingga(TipeToken.AKHIR)
                break

        self._konsumsi(TipeToken.AKHIR, "Setiap struktur 'jika' harus ditutup dengan 'akhir'.")
        return ast.JikaMaka(kondisi, ast.Bagian(blok_maka), rantai_lain_jika, ast.Bagian(blok_lain) if blok_lain else None)

    def _pernyataan_pilih(self):
        ekspresi = self._ekspresi()
        self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

        daftar_kasus = []
        kasus_lainnya = None

        while self._cocok(TipeToken.KETIKA):
            nilai_kasus = self._ekspresi()
            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah nilai 'ketika'.")
            self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

            badan = self._blok_pernyataan_hingga(TipeToken.KETIKA, TipeToken.LAINNYA, TipeToken.AKHIR)
            daftar_kasus.append(ast.PilihKasus(nilai_kasus, ast.Bagian(badan)))

        if self._cocok(TipeToken.LAINNYA):
            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah 'lainnya'.")
            self._cocok(TipeToken.AKHIR_BARIS) # Baris baru opsional

            badan_lainnya = self._blok_pernyataan_hingga(TipeToken.AKHIR)
            kasus_lainnya = ast.KasusLainnya(ast.Bagian(badan_lainnya))

        self._konsumsi(TipeToken.AKHIR, "Struktur 'pilih' harus ditutup dengan 'akhir'.")
        return ast.Pilih(ekspresi, daftar_kasus, kasus_lainnya)

    def _pernyataan_jodohkan(self):
        ekspresi = self._ekspresi()
        self._konsumsi(TipeToken.DENGAN, "Dibutuhkan 'dengan' setelah ekspresi 'jodohkan'.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'dengan'.")

        daftar_kasus = []
        # Mengizinkan pemisah `|` opsional di awal
        self._cocok(TipeToken.GARIS_PEMISAH)

        while not self._periksa(TipeToken.AKHIR):
            pola = self._pola()

            jaga = None
            if self._cocok(TipeToken.JAGA):
                jaga = self._ekspresi()

            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah pola 'jodohkan'.")
            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

            badan = self._blok_pernyataan_hingga(TipeToken.AKHIR, TipeToken.GARIS_PEMISAH)
            daftar_kasus.append(ast.JodohkanKasus(pola, jaga, ast.Bagian(badan)))

            if not self._cocok(TipeToken.GARIS_PEMISAH):
                break

        if not daftar_kasus:
            self._kesalahan(self._intip(), "Blok 'jodohkan' harus memiliki setidaknya satu kasus.")

        self._konsumsi(TipeToken.AKHIR, "Struktur 'jodohkan' harus ditutup dengan 'akhir'.")
        return ast.Jodohkan(ekspresi, daftar_kasus)

    def _pola(self):
        """Mem-parse berbagai jenis pola untuk `jodohkan`."""
        if self._cocok(TipeToken.SIKU_BUKA): # Pola Daftar
            daftar_pola = []
            pola_sisa = None
            if not self._periksa(TipeToken.SIKU_TUTUP):
                while True:
                    if self._cocok(TipeToken.TITIK_TIGA):
                        pola_sisa = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama untuk sisa pola daftar.")
                        break
                    daftar_pola.append(self._pola())
                    if not self._cocok(TipeToken.KOMA):
                        break
            self._konsumsi(TipeToken.SIKU_TUTUP, "Dibutuhkan ']' untuk menutup pola daftar.")
            return ast.PolaDaftar(daftar_pola, pola_sisa)

        if self._intip().tipe in [TipeToken.ANGKA, TipeToken.TEKS, TipeToken.BENAR, TipeToken.SALAH, TipeToken.NIL]:
            return ast.PolaLiteral(self._primary())

        if self._periksa_berikutnya(TipeToken.KURUNG_BUKA): # Pola Varian
            nama_varian = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama varian.")
            self._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah nama varian.")
            daftar_ikatan = []
            if not self._periksa(TipeToken.KURUNG_TUTUP):
                while True:
                    # Di dalam varian, kita hanya mengizinkan NAMA atau _ (wildcard)
                    if self._periksa(TipeToken.NAMA):
                        if self._intip().nilai == "_":
                            daftar_ikatan.append(self._maju()) # Simpan token wildcard
                        else:
                            daftar_ikatan.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama ikatan atau '_'."))
                    else:
                         raise self._kesalahan(self._intip(), "Hanya nama atau '_' yang diizinkan sebagai ikatan pola varian.")

                    if not self._cocok(TipeToken.KOMA):
                        break
            self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah ikatan varian.")
            return ast.PolaVarian(nama_varian, daftar_ikatan)

        # Pola Wildcard atau Ikatan Variabel
        nama_token = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama, literal, atau '_' dalam pola.")
        if nama_token.nilai == "_":
            return ast.PolaWildcard(nama_token)
        # Jika nama diawali huruf kecil -> Ikatan Variabel, jika Kapital -> Pola Varian tanpa argumen
        if nama_token.nilai[0].islower():
            return ast.PolaIkatanVariabel(nama_token)
        else: # Huruf Kapital
            return ast.PolaVarian(nama_token, [])

    def _blok_pernyataan_hingga(self, *tipe_token_berhenti):
        daftar_pernyataan = []
        while not self._periksa(*tipe_token_berhenti) and not self._di_akhir():
            if self._cocok(TipeToken.AKHIR_BARIS):
                continue
            daftar_pernyataan.append(self._deklarasi())
        return daftar_pernyataan

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
        expr = self._ternary()

        if self._cocok(TipeToken.SAMADENGAN):
            equals = self._sebelumnya()
            nilai = self._penugasan() # Memungkinkan assignment berantai a = b = c

            if isinstance(expr, ast.Identitas):
                # Ini adalah re-assignment variabel, yang ilegal tanpa 'ubah'
                raise self._kesalahan(equals, "Operator '=' hanya diizinkan dalam deklarasi 'biar' atau 'tetap'. Gunakan 'ubah' untuk re-assignment.")
            elif isinstance(expr, ast.AmbilProperti):
                # Ini adalah penetapan properti, yang legal
                return ast.AturProperti(expr.objek, expr.nama, nilai)

            raise self._kesalahan(equals, "Target assignment tidak valid.")

        return expr

    def _ternary(self):
        expr = self._logika_atau()

        if self._cocok(TipeToken.TANYA):
            expr_benar = self._ekspresi()
            self._konsumsi(TipeToken.TITIK_DUA, "Dibutuhkan ':' dalam operasi ternary.")
            expr_salah = self._ekspresi()
            return ast.Ternary(expr, expr_benar, expr_salah)

        return expr

    def _pernyataan_ambil_semua(self):
        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'ambil_semua'.")
        alias = None
        if self._cocok(TipeToken.SEBAGAI):
            alias = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama alias setelah 'sebagai'.")

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'ambil_semua'.")
        return ast.AmbilSemua(path_file, alias)

    def _pernyataan_ambil_sebagian(self):
        # Legacy syntax: ambil_sebagian a,b dari "path"
        daftar_simbol = []
        daftar_simbol.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan setidaknya satu nama simbol untuk diimpor."))

        while self._cocok(TipeToken.KOMA):
            daftar_simbol.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama simbol setelah koma."))

        self._konsumsi(TipeToken.DARI, "Dibutuhkan kata kunci 'dari' setelah daftar simbol.")

        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'dari'.")

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'ambil_sebagian'.")
        return ast.AmbilSebagian(daftar_simbol, path_file)

    def _pernyataan_dari_ambil(self):
        # New syntax: dari "path" ambil sebagian a, b
        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'dari'.")

        if self._cocok(TipeToken.AMBIL_SEBAGIAN):
             daftar_simbol = []
             # Izinkan NAMA atau TULIS/PANJANG (Keywords yang sering dipakai sebagai nama fungsi)
             # Kita perlu helper khusus atau perluas _konsumsi

             # Helper lokal untuk konsumsi simbol import
             def konsumsi_simbol():
                 token = self._intip()
                 if token.tipe in [TipeToken.NAMA, TipeToken.TULIS, TipeToken.TIPE]: # Tambahkan keyword lain jika perlu
                     self._maju()
                     # Kembalikan sebagai token NAMA agar konsisten di AST
                     return Token(TipeToken.NAMA, token.nilai, token.baris, token.kolom)
                 raise self._kesalahan(token, "Dibutuhkan nama simbol.")

             daftar_simbol.append(konsumsi_simbol())

             while self._cocok(TipeToken.KOMA):
                 daftar_simbol.append(konsumsi_simbol())

             self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah import.")
             return ast.AmbilSebagian(daftar_simbol, path_file)

        raise self._kesalahan(self._intip(), "Setelah 'dari \"path\"', diharapkan 'ambil_sebagian'.")

    def _pernyataan_pinjam(self):
        butuh_aot = self._cocok(TipeToken.AOT)

        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'pinjam'.")
        alias = None
        if self._cocok(TipeToken.SEBAGAI):
            alias = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama alias setelah 'sebagai'.")

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'pinjam'.")
        return ast.Pinjam(path_file, alias, butuh_aot)

    def _buat_parser_biner(self, metode_lebih_tinggi, *tipe_token):
        def parser():
            expr = metode_lebih_tinggi()
            while self._cocok(*tipe_token):
                operator = self._sebelumnya()
                kanan = metode_lebih_tinggi()
                expr = ast.FoxBinary(expr, operator, kanan)
            return expr
        return parser

    def _logika_atau(self):
        return self._buat_parser_biner(self._logika_dan, TipeToken.ATAU)()
    def _logika_dan(self):
        return self._buat_parser_biner(self._perbandingan, TipeToken.DAN)()
    def _perbandingan(self):
        return self._buat_parser_biner(self._penjumlahan, TipeToken.SAMA_DENGAN, TipeToken.TIDAK_SAMA, TipeToken.KURANG_DARI, TipeToken.KURANG_SAMA, TipeToken.LEBIH_DARI, TipeToken.LEBIH_SAMA)()
    def _penjumlahan(self):
        return self._buat_parser_biner(self._perkalian, TipeToken.TAMBAH, TipeToken.KURANG)()
    def _perkalian(self):
        return self._buat_parser_biner(self._pangkat, TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO)()

    def _pangkat(self):
        expr = self._unary()
        if self._cocok(TipeToken.PANGKAT):
            operator = self._sebelumnya()
            kanan = self._pangkat()
            return ast.FoxBinary(expr, operator, kanan)
        return expr

    def _unary(self):
        if self._cocok(TipeToken.TIDAK, TipeToken.KURANG):
            operator = self._sebelumnya()
            kanan = self._unary()
            return ast.FoxUnary(operator, kanan)

        if self._cocok(TipeToken.TUNGGU):
            kata_kunci = self._sebelumnya()
            ekspresi = self._unary() # Memungkinkan `tunggu tunggu ...` meskipun tidak umum
            return ast.Tunggu(kata_kunci, ekspresi)

        return self._panggilan()

    def _panggilan(self):
        expr = self._primary()
        while True:
            if self._cocok(TipeToken.KURUNG_BUKA):
                expr = self._selesaikan_panggilan(expr)
            elif self._cocok(TipeToken.SIKU_BUKA):
                kunci = self._ekspresi()
                self._konsumsi(TipeToken.SIKU_TUTUP, "Dibutuhkan ']' setelah indeks.")
                expr = ast.Akses(expr, kunci)
            elif self._cocok(TipeToken.TITIK):
                # Izinkan NAMA, TIPE, JENIS, AMBIL, MAKA, dan DARI sebagai nama properti
                token_prop = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE, TipeToken.JENIS, TipeToken.AMBIL, TipeToken.MAKA, TipeToken.DARI), "Dibutuhkan nama properti setelah '.'.")

                # Normalisasi token menjadi NAMA agar AST tetap konsisten
                nama_token = Token(TipeToken.NAMA, token_prop.nilai, token_prop.baris, token_prop.kolom)
                expr = ast.AmbilProperti(expr, nama_token)
            else:
                break
        return expr

    def _selesaikan_panggilan(self, callee):
        argumen = []
        if not self._periksa(TipeToken.KURUNG_TUTUP):
            argumen.append(self._ekspresi())
            while self._cocok(TipeToken.KOMA):
                argumen.append(self._ekspresi())

        token_penutup = self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah argumen.")
        return ast.PanggilFungsi(callee, token_penutup, argumen)

    def _primary(self):
        if self._cocok(TipeToken.SALAH):
            return ast.Konstanta(Token(TipeToken.SALAH, False, self._sebelumnya().baris, self._sebelumnya().kolom))
        if self._cocok(TipeToken.BENAR):
            return ast.Konstanta(Token(TipeToken.BENAR, True, self._sebelumnya().baris, self._sebelumnya().kolom))
        if self._cocok(TipeToken.NIL):
            return ast.Konstanta(Token(TipeToken.NIL, None, self._sebelumnya().baris, self._sebelumnya().kolom))
        if self._cocok(TipeToken.ANGKA):
            return ast.Konstanta(self._sebelumnya())

        if self._cocok(TipeToken.TEKS):
            return self._parse_interpolasi_teks(self._sebelumnya())

        if self._cocok(TipeToken.INI):
            return ast.Ini(self._sebelumnya())

        if self._cocok(TipeToken.INDUK):
            kata_kunci = self._sebelumnya()
            self._konsumsi(TipeToken.TITIK, "Dibutuhkan '.' setelah 'induk'.")
            metode = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama metode setelah 'induk.'.")
            return ast.Induk(kata_kunci, metode)

        if self._cocok(TipeToken.NAMA, TipeToken.TIPE, TipeToken.JENIS, TipeToken.AMBIL):
            # Normalisasi token keyword menjadi 'NAMA' untuk konsistensi di AST
            token = self._sebelumnya()
            if token.tipe in [TipeToken.TIPE, TipeToken.JENIS, TipeToken.AMBIL]:
                token = Token(TipeToken.NAMA, token.nilai, token.baris, token.kolom)
            return ast.Identitas(token)
        if self._cocok(TipeToken.AMBIL):
            self._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah 'ambil'.")
            prompt = None
            if not self._periksa(TipeToken.KURUNG_TUTUP):
                prompt = self._ekspresi()
            self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah argumen 'ambil'.")
            return ast.Ambil(prompt)

        if self._cocok(TipeToken.SIKU_BUKA):
            elemen = []
            if not self._periksa(TipeToken.SIKU_TUTUP):
                elemen.append(self._ekspresi())
                while self._cocok(TipeToken.KOMA):
                    elemen.append(self._ekspresi())
            self._konsumsi(TipeToken.SIKU_TUTUP, "Dibutuhkan ']' untuk menutup daftar.")
            return ast.Daftar(elemen)

        if self._cocok(TipeToken.KURAWAL_BUKA):
            pasangan = []
            if not self._periksa(TipeToken.KURAWAL_TUTUP):
                kunci = self._ekspresi()
                self._konsumsi(TipeToken.TITIK_DUA, "Dibutuhkan ':' setelah kunci kamus.")
                nilai = self._ekspresi()
                pasangan.append((kunci, nilai))
                while self._cocok(TipeToken.KOMA):
                    kunci = self._ekspresi()
                    self._konsumsi(TipeToken.TITIK_DUA, "Dibutuhkan ':' setelah kunci kamus.")
                    nilai = self._ekspresi()
                    pasangan.append((kunci, nilai))
            self._konsumsi(TipeToken.KURAWAL_TUTUP, "Dibutuhkan '}' untuk menutup kamus.")
            return ast.Kamus(pasangan)

        if self._cocok(TipeToken.KURUNG_BUKA):
            expr = self._ekspresi()
            self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah ekspresi.")
            return expr

        raise self._kesalahan(self._intip(), "Ekspresi tidak terduga.")

    def _konsumsi(self, tipe, pesan):
        tipe_yang_diharapkan = tipe if isinstance(tipe, (list, tuple)) else [tipe]
        for t in tipe_yang_diharapkan:
            if self._periksa(t):
                return self._maju()

        # Gunakan token SEBELUMNYA untuk memberikan konteks lokasi yang lebih baik
        lokasi_kesalahan = self._sebelumnya() if self.saat_ini > 0 else self._intip()
        raise self._kesalahan(lokasi_kesalahan, pesan)

    def _konsumsi_akhir_baris(self, pesan):
        if self._cocok(TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA):
            return
        if self._periksa(TipeToken.AKHIR) or self._periksa(TipeToken.KURAWAL_TUTUP) or self._periksa(TipeToken.LAIN) or self._di_akhir():
             return
        raise self._kesalahan(self._intip(), pesan)

    def _cocok(self, *tipe_tokens):
        for tipe in tipe_tokens:
            if self._periksa(tipe):
                self._maju()
                return True
        return False

    def _periksa(self, *tipe_tokens):
        if self._di_akhir():
            return False
        for tipe in tipe_tokens:
            if self._intip().tipe == tipe:
                return True
        return False

    def _maju(self):
        if not self._di_akhir():
            self.saat_ini += 1
        return self._sebelumnya()

    def _di_akhir(self):
        return self._intip().tipe == TipeToken.ADS

    def _intip(self):
        return self.tokens[self.saat_ini]

    def _periksa_berikutnya(self, tipe_token):
        if self._di_akhir(): return False
        if self.tokens[self.saat_ini + 1].tipe == TipeToken.ADS: return False
        return self.tokens[self.saat_ini + 1].tipe == tipe_token

    def _sebelumnya(self):
        return self.tokens[self.saat_ini - 1]

    def _parse_interpolasi_teks(self, token: Token):
        """Memproses string literal untuk interpolasi."""
        text = token.nilai
        if '{' not in text:
            return ast.Konstanta(token)

        # Logic untuk scan string dan split
        # Kita butuh Lexer dan Parser rekursif.
        # Tapi karena ini Bootstrap parser (Python), kita bisa import lokal.
        from transisi.lx import Leksikal

        parts = []
        i = 0
        length = len(text)
        buffer = ""

        while i < length:
            char = text[i]
            if char == '\\':
                # Handle escaping \{
                if i + 1 < length and text[i+1] == '{':
                    buffer += '{'
                    i += 2
                    continue
                else:
                    buffer += char
                    i += 1
            elif char == '{':
                # Found interpolation start
                # Flush buffer if any
                if buffer:
                    # Buat token TEKS baru untuk bagian statis
                    static_token = Token(TipeToken.TEKS, buffer, token.baris, token.kolom)
                    parts.append(ast.Konstanta(static_token))
                    buffer = ""

                # Scan sampai closing '}' (balanced?)
                # Sederhana dulu: Scan sampai } pertama yang tidak di-quote.
                # Kita perlu scan code di dalam { ... }
                code_start = i + 1
                brace_depth = 1
                j = code_start
                in_quote = None

                while j < length and brace_depth > 0:
                    c = text[j]
                    if in_quote:
                        if c == '\\':
                            j += 2
                            continue
                        if c == in_quote:
                            in_quote = None
                        j += 1
                    else:
                        if c == '"' or c == "'":
                            in_quote = c
                        elif c == '{':
                            brace_depth += 1
                        elif c == '}':
                            brace_depth -= 1

                        if brace_depth > 0:
                            j += 1

                if brace_depth != 0:
                    # Unbalanced, anggap sebagai string biasa (atau error?)
                    # Fallback: treat '{' as literal if no matching '}' found?
                    # Strict: Error.
                    raise self._kesalahan(token, "Interpolasi string tidak ditutup dengan '}'.")

                code_str = text[code_start:j]

                # Recursively parse code_str
                # Note: code_str tidak punya baris/kolom yang akurat relatif terhadap file asli
                # Kita abaikan offset error detail untuk bootstrap.
                sub_lexer = Leksikal(code_str)
                sub_tokens, _ = sub_lexer.buat_token()
                sub_parser = Pengurai(sub_tokens)

                # Kita harap ekspresi tunggal.
                expr = sub_parser._ekspresi()

                # Wrap in KonversiTeks
                parts.append(ast.KonversiTeks(expr))

                i = j + 1 # Continue after '}'
            else:
                buffer += char
                i += 1

        if buffer:
            static_token = Token(TipeToken.TEKS, buffer, token.baris, token.kolom)
            parts.append(ast.Konstanta(static_token))

        if not parts:
            return ast.Konstanta(Token(TipeToken.TEKS, "", token.baris, token.kolom))

        # Gabungkan parts dengan FoxBinary(ADD)
        result = parts[0]
        for k in range(1, len(parts)):
            # Kita gunakan token op dummy
            op_plus = Token(TipeToken.TAMBAH, "+", token.baris, token.kolom)
            result = ast.FoxBinary(result, op_plus, parts[k])

        return result

    def _kesalahan(self, token: Token, pesan: str):
        self.daftar_kesalahan.append((token, pesan))
        return PenguraiKesalahan()
