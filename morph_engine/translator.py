# transisi/translator.py
# Interpreter untuk "Kelahiran Kembali MORPH"

from . import absolute_sntx_morph as ast
from .morph_t import TipeToken

class KesalahanRuntime(Exception):
    def __init__(self, token, pesan):
        self.token = token
        self.pesan = pesan
        super().__init__(pesan)

class Lingkungan:
    """Manajemen scope dan simbol (variabel/fungsi)."""
    def __init__(self, induk=None):
        self.nilai = {}
        self.induk = induk

    def definisi(self, nama: str, nilai):
        self.nilai[nama] = nilai

    def dapatkan(self, token):
        nama = token.nilai
        if nama in self.nilai:
            return self.nilai[nama]
        if self.induk is not None:
            return self.induk.dapatkan(token)
        raise KesalahanRuntime(token, f"Variabel '{nama}' belum didefinisikan.")

    def tetapkan(self, token, nilai):
        nama = token.nilai
        if nama in self.nilai:
            self.nilai[nama] = nilai
            return
        if self.induk is not None:
            self.induk.tetapkan(token, nilai)
            return
        raise KesalahanRuntime(token, f"Variabel '{nama}' belum didefinisikan.")


class Penerjemah:
    """Visitor yang mengeksekusi AST."""
    def __init__(self, formatter):
        self.lingkungan = Lingkungan()
        self.formatter = formatter

    def terjemahkan(self, program: ast.Bagian):
        try:
            for pernyataan in program.daftar_pernyataan:
                self._eksekusi(pernyataan)
        except KesalahanRuntime as e:
            print(self.formatter.format_runtime(e))

    def _eksekusi(self, pernyataan: ast.St):
        return pernyataan.terima(self)

    def _evaluasi(self, ekspresi: ast.Xprs):
        return ekspresi.terima(self)

    def _fitur_belum_aktif(self, node, nama_fitur):
        """Membuat kesalahan runtime untuk fitur yang belum diimplementasikan."""
        pesan = f"Fitur '{nama_fitur}' belum diaktifkan di Morph."
        # Coba dapatkan token yang paling relevan dari node
        token = getattr(node, 'token', None) or getattr(node, 'nama', None) or getattr(node, 'kata_kunci', None)
        raise KesalahanRuntime(token, pesan)

    # --- Visitor untuk Pernyataan (Statements) ---

    def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            self._eksekusi(pernyataan)

    def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        self._evaluasi(node.ekspresi)

    def kunjungi_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        nilai = None
        if node.nilai is not None:
            nilai = self._evaluasi(node.nilai)
        self.lingkungan.definisi(node.nama.nilai, nilai)

    def kunjungi_Tulis(self, node: ast.Tulis):
        for arg in node.argumen:
            nilai = self._evaluasi(arg)
            print(self._ke_string(nilai), end=' ')
        print() # Newline di akhir

    def kunjungi_Assignment(self, node: ast.Assignment):
        nilai = self._evaluasi(node.nilai)
        self.lingkungan.tetapkan(node.nama, nilai)
        return nilai

    # --- Visitor untuk Ekspresi (Expressions) ---

    def kunjungi_Identitas(self, node: ast.Identitas):
        return self.lingkungan.dapatkan(node.token)

    def kunjungi_Konstanta(self, node: ast.Konstanta):
        return node.nilai

    def kunjungi_FoxUnary(self, node: ast.FoxUnary):
        kanan = self._evaluasi(node.kanan)

        if node.op.tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kanan)
            return -kanan
        if node.op.tipe == TipeToken.TIDAK:
            return not self._apakah_benar(kanan)

        return None # Harusnya tidak pernah terjadi

    def kunjungi_FoxBinary(self, node: ast.FoxBinary):
        kiri = self._evaluasi(node.kiri)
        kanan = self._evaluasi(node.kanan)
        op_tipe = node.op.tipe

        # Operasi Aritmatika
        if op_tipe == TipeToken.TAMBAH:
            if isinstance(kiri, (int, float)) and isinstance(kanan, (int, float)):
                return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str):
                return kiri + kanan
            raise KesalahanRuntime(node.op, "Operan harus dua angka atau dua teks.")
        if op_tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri - kanan
        if op_tipe == TipeToken.KALI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri * kanan
        if op_tipe == TipeToken.BAGI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            if kanan == 0:
                raise KesalahanRuntime(node.op, "Tidak bisa membagi dengan nol.")
            return kiri / kanan

        # Operasi Perbandingan
        if op_tipe == TipeToken.LEBIH_DARI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri > kanan
        if op_tipe == TipeToken.KURANG_DARI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri < kanan
        if op_tipe == TipeToken.LEBIH_SAMA:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri >= kanan
        if op_tipe == TipeToken.KURANG_SAMA:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            return kiri <= kanan

        # Operasi Kesetaraan
        if op_tipe == TipeToken.SAMA_DENGAN:
            return kiri == kanan
        if op_tipe == TipeToken.TIDAK_SAMA:
            return kiri != kanan

        return None # Harusnya tidak pernah terjadi

    # --- Visitor untuk Fitur Fase 2 (Placeholder) ---

    def kunjungi_Daftar(self, node: ast.Daftar):
        self._fitur_belum_aktif(node, "daftar literal ([...])")

    def kunjungi_Kamus(self, node: ast.Kamus):
        self._fitur_belum_aktif(node, "kamus literal ({...})")

    def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi):
        self._fitur_belum_aktif(node, "pemanggilan fungsi")

    def kunjungi_Akses(self, node: ast.Akses):
        self._fitur_belum_aktif(node, "akses anggota '[...]'")

    def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        if self._apakah_benar(self._evaluasi(node.kondisi)):
            self._eksekusi_blok(node.blok_maka)
        else:
            for kondisi_lain, blok_lain in node.rantai_lain_jika:
                if self._apakah_benar(self._evaluasi(kondisi_lain)):
                    self._eksekusi_blok(blok_lain)
                    return # Hanya satu cabang yang dieksekusi

            if node.blok_lain is not None:
                self._eksekusi_blok(node.blok_lain)

    def _eksekusi_blok(self, blok_node: ast.Bagian):
        lingkungan_blok = Lingkungan(induk=self.lingkungan)
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in blok_node.daftar_pernyataan:
                self._eksekusi(pernyataan)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        self._fitur_belum_aktif(node, "deklarasi fungsi")

    def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        self._fitur_belum_aktif(node, "pernyataan 'kembalikan'")

    def kunjungi_Selama(self, node: ast.Selama):
        self._fitur_belum_aktif(node, "perulangan 'selama'")

    def kunjungi_Ambil(self, node: ast.Ambil):
        self._fitur_belum_aktif(node, "fungsi bawaan 'ambil'")

    def kunjungi_Pinjam(self, node: ast.Pinjam):
        self._fitur_belum_aktif(node, "peminjaman modul Python ('pinjam')")

    def kunjungi_Pilih(self, node: ast.Pilih):
        self._fitur_belum_aktif(node, "struktur kontrol 'pilih/ketika'")

    def kunjungi_PilihKasus(self, node: ast.PilihKasus):
        self._fitur_belum_aktif(node, "struktur kontrol 'pilih/ketika'")

    def kunjungi_KasusLainnya(self, node: ast.KasusLainnya):
        self._fitur_belum_aktif(node, "struktur kontrol 'pilih/ketika'")

    # --- Helper Methods ---

    def _ke_string(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, bool): return "benar" if obj else "salah"
        return str(obj)

    def _apakah_benar(self, obj):
        """Mendefinisikan 'truthiness' di MORPH."""
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _periksa_tipe_angka(self, operator, *operands):
        for operand in operands:
            # Boolean tidak dianggap sebagai angka dalam MORPH
            if not isinstance(operand, (int, float)) or isinstance(operand, bool):
                raise KesalahanRuntime(operator, "Operan harus berupa angka.")

# --- Monkey-patching Visitor ke AST Nodes ---
# Ini adalah cara simpel untuk mengimplementasikan visitor pattern
# tanpa mengubah kelas-kelas AST itu sendiri.

def patch_ast_nodes():
    def terima(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            raise NotImplementedError(f"Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
        return metode(self)

    ast.MRPH.terima = terima

patch_ast_nodes()
