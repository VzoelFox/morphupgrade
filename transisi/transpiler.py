# transisi/transpiler.py
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token

from .penerjemah import Lingkungan

class Transpiler:
    """
    Mengubah AST MORPH menjadi source code Python yang fungsional.
    """
    def __init__(self, lingkungan: Lingkungan):
        self.level_indentasi = 0
        self.kode_python = ""
        self.lingkungan = lingkungan
        self.variabel_lokal = set()

    def _tambah_indentasi(self):
        self.level_indentasi += 1

    def _kurangi_indentasi(self):
        self.level_indentasi -= 1

    def _tulis(self, s, baris_baru=True):
        indentasi = "    " * self.level_indentasi
        self.kode_python += indentasi + s
        if baris_baru:
            self.kode_python += "\n"

    def transpilasi(self, node: ast.FungsiDeklarasi) -> str:
        """Metode utama untuk memulai proses transpilasi."""
        self.kode_python = ""
        # Daftarkan parameter fungsi sebagai variabel lokal
        for param in node.parameter:
            self.variabel_lokal.add(param.nilai)

        self.kunjungi(node)
        return self.kode_python

    def kunjungi(self, node):
        """Mendelegasikan ke metode 'kunjungi_*' yang sesuai."""
        nama_metode = f"kunjungi_{type(node).__name__}"
        visitor = getattr(self, nama_metode, self.visitor_default)
        return visitor(node)

    def visitor_default(self, node):
        raise NotImplementedError(f"Visitor untuk {type(node).__name__} belum diimplementasikan.")

    # --- Visitor untuk Pernyataan (Statements) ---

    def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        # Hanya transpilasi isi fungsi, bukan deklarasi 'def'
        # Variabel '__hasil' akan dideklarasikan oleh eksekutor.
        self.kunjungi(node.badan)

    def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            self.kunjungi(pernyataan)

    def kunjungi_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        nama_var = node.nama.nilai
        self.variabel_lokal.add(nama_var)
        nilai = self.kunjungi(node.nilai)
        self._tulis(f"{nama_var} = {nilai}")

    def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        nilai = self.kunjungi(node.nilai)
        # Simpan nilai ke variabel hasil, jangan langsung return
        self._tulis(f"__hasil = {nilai}")

    def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        # Transpilasi ekspresi, tetapi jangan lakukan apa pun dengan hasilnya
        # karena ini adalah pernyataan.
        self.kunjungi(node.ekspresi)

    def kunjungi_Assignment(self, node: ast.Assignment):
        nilai = self.kunjungi(node.nilai)
        target = self.kunjungi(node.target)
        self._tulis(f"{target} = {nilai}")

    def kunjungi_Selama(self, node: ast.Selama):
        kondisi = self.kunjungi(node.kondisi)
        self._tulis(f"while {kondisi}:")
        self._tambah_indentasi()
        self.kunjungi(node.badan)
        self._kurangi_indentasi()

    def kunjungi_Tulis(self, node: ast.Tulis):
        argumen_py = [self.kunjungi(arg) for arg in node.argumen]
        self._tulis(f"print({', '.join(argumen_py)})")

    def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        # Handle 'if'
        kondisi_if = self.kunjungi(node.kondisi)
        self._tulis(f"if {kondisi_if}:")
        self._tambah_indentasi()
        self.kunjungi(node.blok_maka)
        self._kurangi_indentasi()

        # Handle 'lain jika' (elif)
        for kondisi_lain, blok_lain in node.rantai_lain_jika:
            kondisi_elif = self.kunjungi(kondisi_lain)
            self._tulis(f"elif {kondisi_elif}:")
            self._tambah_indentasi()
            self.kunjungi(blok_lain)
            self._kurangi_indentasi()

        # Handle 'lain' (else)
        if node.blok_lain:
            self._tulis("else:")
            self._tambah_indentasi()
            self.kunjungi(node.blok_lain)
            self._kurangi_indentasi()

    # --- Visitor untuk Ekspresi (Expressions) ---
    def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi) -> str:
        callee = self.kunjungi(node.callee)
        argumen = [self.kunjungi(arg) for arg in node.argumen]
        return f"{callee}({', '.join(argumen)})"

    def kunjungi_AmbilProperti(self, node: ast.AmbilProperti) -> str:
        objek = self.kunjungi(node.objek)
        return f"{objek}.{node.nama.nilai}"

    def kunjungi_FoxBinary(self, node: ast.FoxBinary) -> str:
        kiri = self.kunjungi(node.kiri)
        kanan = self.kunjungi(node.kanan)

        # Peta token MORPH ke operator Python
        operator_map = {
            # Aritmatika
            TipeToken.TAMBAH: "+",
            TipeToken.KURANG: "-",
            TipeToken.KALI: "*",
            TipeToken.BAGI: "/",
            # Perbandingan
            TipeToken.SAMA_DENGAN: "==",
            TipeToken.TIDAK_SAMA: "!=",
            TipeToken.KURANG_DARI: "<",
            TipeToken.KURANG_SAMA: "<=",
            TipeToken.LEBIH_DARI: ">",
            TipeToken.LEBIH_SAMA: ">=",
            # Logika
            TipeToken.DAN: "and",
            TipeToken.ATAU: "or",
        }
        op = operator_map.get(node.op.tipe)
        if op is None:
            raise NotImplementedError(f"Operator biner {node.op.tipe} belum didukung.")

        return f"({kiri} {op} {kanan})"

    def kunjungi_Identitas(self, node: ast.Identitas) -> str:
        # Jika nama ada di variabel lokal, itu adalah variabel biasa.
        # Jika tidak, kita asumsikan itu adalah objek dari lingkup luar (FFI).
        nama = node.token.nilai
        if nama in self.variabel_lokal:
            return nama
        # Jika tidak, kita perlu mengaksesnya dari namespace eksternal.
        # Untuk sekarang, kita kembalikan saja namanya, dan eksekutor
        # akan bertanggung jawab untuk menyediakannya.
        return nama

    def kunjungi_Konstanta(self, node: ast.Konstanta) -> str:
        nilai = node.nilai
        if isinstance(nilai, str):
            return f'"{nilai}"'
        return str(nilai)

    def kunjungi_Daftar(self, node: ast.Daftar) -> str:
        elemen = [self.kunjungi(elem) for elem in node.elemen]
        return f"[{', '.join(elemen)}]"

    def kunjungi_Kamus(self, node: ast.Kamus) -> str:
        pasangan = []
        for kunci_node, nilai_node in node.pasangan:
            kunci = self.kunjungi(kunci_node)
            nilai = self.kunjungi(nilai_node)
            pasangan.append(f"{kunci}: {nilai}")
        return f"{{{', '.join(pasangan)}}}"

    def kunjungi_Akses(self, node: ast.Akses) -> str:
        objek = self.kunjungi(node.objek)
        kunci = self.kunjungi(node.kunci)
        return f"{objek}[{kunci}]"
