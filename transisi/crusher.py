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
        try:
            if self._cocok(TipeToken.PINJAM):
                return self._pernyataan_pinjam()
            if self._cocok(TipeToken.KELAS):
                return self._deklarasi_kelas()
            if self._cocok(TipeToken.AMBIL_SEMUA):
                return self._pernyataan_ambil_semua()
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
        except PenguraiKesalahan:
            self._sinkronisasi()
            return None

    def _deklarasi_kelas(self):
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama setelah 'kelas'.")

        superkelas = None
        if self._cocok(TipeToken.WARISI):
            nama_super = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama superkelas setelah 'warisi'.")
            superkelas = ast.Identitas(nama_super)

        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah nama kelas.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

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
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup fungsi.")
        return ast.FungsiAsinkDeklarasi(nama, parameter, ast.Bagian(badan))

    def _deklarasi_fungsi(self, jenis: str):
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
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

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
        nama = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel.")

        nilai = None
        if self._cocok(TipeToken.SAMADENGAN):
            nilai = self._ekspresi()

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah deklarasi variabel.")
        return ast.DeklarasiVariabel(jenis_deklarasi, nama, nilai)

    def _pernyataan(self):
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
        if self._cocok(TipeToken.KURAWAL_BUKA):
            return ast.Bagian(self._blok())
        return self._pernyataan_ekspresi()

    def _pernyataan_assignment(self):
        # 'ubah' sudah dikonsumsi. Target bisa berupa nama variabel atau akses item.
        target_expr = self._panggilan()

        self._konsumsi(TipeToken.SAMADENGAN, "Dibutuhkan '=' setelah target untuk assignment 'ubah'.")
        nilai = self._ekspresi()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah nilai assignment.")

        if isinstance(target_expr, ast.Identitas):
            return ast.Assignment(target_expr.token, nilai)
        elif isinstance(target_expr, ast.Akses):
            return ast.Assignment(target_expr, nilai)

        raise self._kesalahan(self._sebelumnya(), "Target 'ubah' tidak valid. Hanya variabel atau akses item yang didukung.")

    def _pernyataan_selama(self):
        token_selama = self._sebelumnya()
        kondisi = self._ekspresi()
        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah kondisi 'selama'.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

        badan = self._blok_pernyataan_hingga(TipeToken.AKHIR)

        self._konsumsi(TipeToken.AKHIR, "Dibutuhkan 'akhir' untuk menutup loop 'selama'.")
        return ast.Selama(token_selama, kondisi, ast.Bagian(badan))

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

    def _pernyataan_jika(self):
        kondisi = self._ekspresi()
        self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah kondisi 'jika'.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

        blok_maka = self._blok_pernyataan_hingga(TipeToken.AKHIR, TipeToken.LAIN)

        rantai_lain_jika = []
        blok_lain = None

        while self._cocok(TipeToken.LAIN):
            if self._cocok(TipeToken.JIKA):
                kondisi_lain_jika = self._ekspresi()
                self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah 'lain jika'.")
                self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

                blok_lain_jika = self._blok_pernyataan_hingga(TipeToken.AKHIR, TipeToken.LAIN)
                rantai_lain_jika.append((kondisi_lain_jika, ast.Bagian(blok_lain_jika)))
            else:
                self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'lain'.")
                blok_lain = self._blok_pernyataan_hingga(TipeToken.AKHIR)
                break

        self._konsumsi(TipeToken.AKHIR, "Setiap struktur 'jika' harus ditutup dengan 'akhir'.")
        return ast.JikaMaka(kondisi, ast.Bagian(blok_maka), rantai_lain_jika, ast.Bagian(blok_lain) if blok_lain else None)

    def _pernyataan_pilih(self):
        ekspresi = self._ekspresi()
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah ekspresi 'pilih'.")

        daftar_kasus = []
        kasus_lainnya = None

        while self._cocok(TipeToken.KETIKA):
            nilai_kasus = self._ekspresi()
            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah nilai 'ketika'.")
            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

            badan = self._blok_pernyataan_hingga(TipeToken.KETIKA, TipeToken.LAINNYA, TipeToken.AKHIR)
            daftar_kasus.append(ast.PilihKasus(nilai_kasus, ast.Bagian(badan)))

        if self._cocok(TipeToken.LAINNYA):
            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah 'lainnya'.")
            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

            badan_lainnya = self._blok_pernyataan_hingga(TipeToken.AKHIR)
            kasus_lainnya = ast.KasusLainnya(ast.Bagian(badan_lainnya))

        self._konsumsi(TipeToken.AKHIR, "Struktur 'pilih' harus ditutup dengan 'akhir'.")
        return ast.Pilih(ekspresi, daftar_kasus, kasus_lainnya)

    def _pernyataan_jodohkan(self):
        ekspresi = self._ekspresi()
        self._konsumsi(TipeToken.DENGAN, "Dibutuhkan kata kunci 'dengan' setelah ekspresi.")
        self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'dengan'.")

        daftar_kasus = []
        while self._cocok(TipeToken.GARIS_PEMISAH):
            pola = self._pola()

            jaga = None
            if self._cocok(TipeToken.KETIKA):
                jaga = self._ekspresi()

            self._konsumsi(TipeToken.MAKA, "Dibutuhkan 'maka' setelah pola atau kondisi 'ketika'.")
            self._konsumsi_akhir_baris("Dibutuhkan baris baru setelah 'maka'.")

            badan = self._blok_pernyataan_hingga(TipeToken.GARIS_PEMISAH, TipeToken.AKHIR)
            daftar_kasus.append(ast.JodohkanKasus(pola, ast.Bagian(badan), jaga))

        if not daftar_kasus:
            raise self._kesalahan(self._sebelumnya(), "Blok 'jodohkan' harus memiliki setidaknya satu kasus '|'.")

        self._konsumsi(TipeToken.AKHIR, "Struktur 'jodohkan' harus ditutup dengan 'akhir'.")
        return ast.Jodohkan(ekspresi, daftar_kasus)

    def _pola(self):
        # Pola Daftar
        if self._cocok(TipeToken.SIKU_BUKA):
            daftar_pola = []
            pola_sisa = None
            if not self._periksa(TipeToken.SIKU_TUTUP):
                # Parse elemen-elemen sebelum pola sisa (jika ada)
                while not self._periksa(TipeToken.SIKU_TUTUP) and not self._periksa(TipeToken.TITIK_TIGA):
                    daftar_pola.append(self._pola())
                    if not self._cocok(TipeToken.KOMA):
                        # Jika tidak ada koma, kita harus berada di akhir atau di pola sisa
                        break

                # Cek untuk pola sisa
                if self._cocok(TipeToken.TITIK_TIGA):
                    pola_sisa = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama untuk pola sisa '...' dalam daftar.")
                    # Pola sisa tidak boleh diikuti oleh koma
                    if self._cocok(TipeToken.KOMA):
                        raise self._kesalahan(self._sebelumnya(), "Tidak boleh ada elemen setelah pola sisa '...' dalam daftar.")

            self._konsumsi(TipeToken.SIKU_TUTUP, "Dibutuhkan ']' untuk menutup pola daftar.")
            return ast.PolaDaftar(daftar_pola, pola_sisa)

        # Pola Literal
        if self._cocok(TipeToken.ANGKA, TipeToken.TEKS, TipeToken.BENAR, TipeToken.SALAH, TipeToken.NIL):
            return ast.PolaLiteral(ast.Konstanta(self._sebelumnya()))

        # Pola NAMA (bisa Varian, Ikatan Variabel, atau Wildcard)
        if self._periksa(TipeToken.NAMA):
            token_nama = self._intip()
            nama = token_nama.nilai

            # Wildcard
            if nama == '_':
                self._maju()
                return ast.PolaWildcard(token_nama)

            # Cek apakah ini Varian dengan parameter
            if self._periksa_berikutnya(TipeToken.KURUNG_BUKA):
                self._maju() # Konsumsi NAMA
                self._maju() # Konsumsi KURUNG_BUKA
                daftar_ikatan = []
                if not self._periksa(TipeToken.KURUNG_TUTUP):
                    ikatan = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel atau '_' dalam pola varian.")
                    daftar_ikatan.append(ikatan)
                    while self._cocok(TipeToken.KOMA):
                        ikatan = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel atau '_' setelah koma.")
                        daftar_ikatan.append(ikatan)
                self._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah parameter pola varian.")
                return ast.PolaVarian(token_nama, daftar_ikatan)

            # Jika bukan, ini adalah Ikatan Variabel atau Varian tanpa argumen
            self._maju() # Konsumsi NAMA
            first_char = nama[0] if nama else ''
            if 'a' <= first_char <= 'z':
                return ast.PolaIkatanVariabel(token_nama)
            else:
                return ast.PolaVarian(token_nama, []) # Varian tanpa argumen

        raise self._kesalahan(self._intip(), "Pola tidak valid.")

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
        expr = self._logika_atau()

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

    def _pernyataan_ambil_semua(self):
        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'ambil_semua'.")
        alias = None
        if self._cocok(TipeToken.SEBAGAI):
            alias = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama alias setelah 'sebagai'.")

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'ambil_semua'.")
        return ast.AmbilSemua(path_file, alias)

    def _pernyataan_ambil_sebagian(self):
        daftar_simbol = []
        daftar_simbol.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan setidaknya satu nama simbol untuk diimpor."))

        while self._cocok(TipeToken.KOMA):
            daftar_simbol.append(self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama simbol setelah koma."))

        self._konsumsi(TipeToken.DARI, "Dibutuhkan kata kunci 'dari' setelah daftar simbol.")

        path_file = self._konsumsi(TipeToken.TEKS, "Dibutuhkan path file modul setelah 'dari'.")

        self._konsumsi_akhir_baris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'ambil_sebagian'.")
        return ast.AmbilSebagian(daftar_simbol, path_file)

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
                token_prop = self._konsumsi((TipeToken.NAMA, TipeToken.TIPE), "Dibutuhkan nama properti setelah '.'.")
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
        if self._cocok(TipeToken.ANGKA, TipeToken.TEKS):
            return ast.Konstanta(self._sebelumnya())

        if self._cocok(TipeToken.INI):
            return ast.Ini(self._sebelumnya())

        if self._cocok(TipeToken.INDUK):
            kata_kunci = self._sebelumnya()
            self._konsumsi(TipeToken.TITIK, "Dibutuhkan '.' setelah 'induk'.")
            metode = self._konsumsi(TipeToken.NAMA, "Dibutuhkan nama metode setelah 'induk.'.")
            return ast.Induk(kata_kunci, metode)

        if self._cocok(TipeToken.NAMA, TipeToken.TIPE):
            # Normalisasi token 'TIPE' menjadi 'NAMA' untuk konsistensi di AST
            token = self._sebelumnya()
            if token.tipe == TipeToken.TIPE:
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

    def _kesalahan(self, token: Token, pesan: str):
        self.daftar_kesalahan.append((token, pesan))
        return PenguraiKesalahan()

    def _sinkronisasi(self):
        self._maju()
        while not self._di_akhir():
            if self._sebelumnya().tipe in (TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA):
                return
            if self._intip().tipe in [
                TipeToken.FUNGSI, TipeToken.BIAR, TipeToken.TETAP,
                TipeToken.JIKA, TipeToken.SELAMA, TipeToken.KEMBALIKAN,
                TipeToken.TULIS, TipeToken.UBAH,
            ]:
                return
            self._maju()
