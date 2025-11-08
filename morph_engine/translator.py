# transisi/translator.py
# Interpreter untuk "Kelahiran Kembali MORPH"

from . import absolute_sntx_morph as ast
from .morph_t import TipeToken

class KesalahanRuntime(Exception):
    def __init__(self, token, pesan):
        self.token = token
        self.pesan = pesan
        super().__init__(pesan)

# Exception khusus untuk menangani alur kontrol 'kembalikan'
class NilaiKembalian(Exception):
    def __init__(self, nilai):
        self.nilai = nilai

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

# Kelas untuk representasi fungsi saat runtime
class Fungsi:
    def __init__(self, deklarasi: ast.FungsiDeklarasi, penutup: Lingkungan):
        self.deklarasi = deklarasi
        self.penutup = penutup # Lingkungan tempat fungsi didefinisikan

    def __str__(self):
        return f"<fungsi {self.deklarasi.nama.nilai}>"

    def panggil(self, interpreter, node_panggil: ast.PanggilFungsi):
        argumen = [interpreter._evaluasi(arg) for arg in node_panggil.argumen]

        # Buat lingkungan baru untuk eksekusi fungsi
        lingkungan_fungsi = Lingkungan(induk=self.penutup)

        # Validasi jumlah argumen
        if len(argumen) != len(self.deklarasi.parameter):
            raise KesalahanRuntime(
                node_panggil.token, # Gunakan token dari node pemanggil
                f"Jumlah argumen tidak cocok. Diharapkan {len(self.deklarasi.parameter)}, diterima {len(argumen)}."
            )

        # Ikat argumen ke parameter di lingkungan baru
        for param, arg in zip(self.deklarasi.parameter, argumen):
            lingkungan_fungsi.definisi(param.nilai, arg)

        # Eksekusi badan fungsi
        try:
            interpreter._eksekusi_blok(self.deklarasi.badan, lingkungan_fungsi)
        except NilaiKembalian as e:
            return e.nilai

        # Fungsi yang tidak memiliki pernyataan 'kembalikan' akan mengembalikan 'nil'
        return None


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
        # Jika target adalah akses indeks, tangani secara khusus
        if isinstance(node.nama, ast.Akses):
            objek = self._evaluasi(node.nama.objek)
            kunci = self._evaluasi(node.nama.kunci)

            if isinstance(objek, list) and isinstance(kunci, int):
                if 0 <= kunci < len(objek):
                    objek[kunci] = nilai
                    return nilai
                else:
                    raise KesalahanRuntime(node.nama.objek.token, "Indeks di luar jangkauan.")
            raise KesalahanRuntime(node.nama.objek.token, "Hanya bisa menetapkan nilai ke elemen daftar dengan indeks angka.")

        self.lingkungan.tetapkan(node.nama, nilai)
        return nilai


    def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        fungsi = Fungsi(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)

    def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        nilai = None
        if node.nilai is not None:
            nilai = self._evaluasi(node.nilai)
        raise NilaiKembalian(nilai)

    def kunjungi_Selama(self, node: ast.Selama):
        while self._apakah_benar(self._evaluasi(node.kondisi)):
            self._eksekusi_blok(node.badan, Lingkungan(induk=self.lingkungan))


    # --- Visitor untuk Ekspresi (Expressions) ---

    def kunjungi_Daftar(self, node: ast.Daftar):
        return [self._evaluasi(elem) for elem in node.elemen]

    def kunjungi_Akses(self, node: ast.Akses):
        objek = self._evaluasi(node.objek)
        kunci = self._evaluasi(node.kunci)

        if isinstance(objek, (list, str)):
            if not isinstance(kunci, int):
                raise KesalahanRuntime(node.kunci.token, "Indeks harus berupa angka.")

            if 0 <= kunci < len(objek):
                return objek[kunci]
            else:
                # Mengembalikan nil jika di luar jangkauan, sama seperti Python
                return None

        raise KesalahanRuntime(node.objek.token, "Hanya daftar atau teks yang bisa diakses dengan indeks.")


    def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi):
        callee = self._evaluasi(node.callee)

        if not isinstance(callee, Fungsi):
            raise KesalahanRuntime(node.token, "Hanya fungsi yang bisa dipanggil.")

        return callee.panggil(self, node)

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

    def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        if self._apakah_benar(self._evaluasi(node.kondisi)):
            self._eksekusi_blok(node.blok_maka, Lingkungan(induk=self.lingkungan))
        else:
            for kondisi_lain, blok_lain in node.rantai_lain_jika:
                if self._apakah_benar(self._evaluasi(kondisi_lain)):
                    self._eksekusi_blok(blok_lain, Lingkungan(induk=self.lingkungan))
                    return

            if node.blok_lain is not None:
                self._eksekusi_blok(node.blok_lain, Lingkungan(induk=self.lingkungan))

    def _eksekusi_blok(self, blok_node: ast.Bagian, lingkungan_blok: Lingkungan):
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in blok_node.daftar_pernyataan:
                self._eksekusi(pernyataan)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    # --- Helper Methods ---

    def _ke_string(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, bool): return "benar" if obj else "salah"
        # Representasi daftar yang lebih mirip Python
        if isinstance(obj, list):
            return f"[{', '.join(self._ke_string(e) for e in obj)}]"
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
            # Fallback untuk node yang belum diimplementasikan secara eksplisit
            # Ini akan mencegah crash tetapi tidak akan melakukan apa-apa
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return metode(self)

    ast.MRPH.terima = terima

patch_ast_nodes()
