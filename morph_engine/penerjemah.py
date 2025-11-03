# morph_engine/penerjemah.py
from .node_ast import *

class PengunjungNode:
    """
    Kelas dasar untuk 'mengunjungi' setiap node di AST.
    Secara dinamis memanggil metode kunjungi_<NamaTipeNode> berdasarkan tipe node.
    """
    def kunjungi(self, node):
        nama_metode = f'kunjungi_{type(node).__name__}'
        pengunjung = getattr(self, nama_metode, self.kunjungan_umum)
        return pengunjung(node)

    def kunjungan_umum(self, node):
        raise Exception(f'Tidak ada metode kunjungi_{type(node).__name__}')

class Penerjemah(PengunjungNode):
    def __init__(self, ast):
        self.ast = ast
        self.tabel_simbol = {} # Tabel untuk menyimpan variabel

    def kunjungi_NodeProgram(self, node):
        """Mengeksekusi setiap pernyataan dalam program."""
        for pernyataan in node.daftar_pernyataan:
            self.kunjungi(pernyataan)

    def kunjungi_NodeDeklarasiVariabel(self, node):
        """Menyimpan variabel dan nilainya ke dalam tabel simbol."""
        nama_var = node.nama_variabel.nilai
        nilai_var = self.kunjungi(node.nilai)
        self.tabel_simbol[nama_var] = nilai_var

    def kunjungi_NodePanggilFungsi(self, node):
        """Menangani pemanggilan fungsi, khusus untuk 'tulis'."""
        nama_fungsi = node.nama_fungsi.nilai
        if nama_fungsi == 'tulis':
            argumen = self.kunjungi(node.argumen)
            print(argumen)
        else:
            raise NameError(f"Fungsi '{nama_fungsi}' tidak didefinisikan.")

    def kunjungi_NodePengenal(self, node):
        """Mengambil nilai variabel dari tabel simbol."""
        nama_var = node.nilai
        nilai = self.tabel_simbol.get(nama_var)
        if nilai is None:
            raise NameError(f"Variabel '{nama_var}' tidak didefinisikan.")
        return nilai

    def kunjungi_NodeTeks(self, node):
        """Mengembalikan nilai literal dari teks."""
        return node.nilai

    def interpretasi(self):
        """Memulai proses interpretasi dari node akar (program)."""
        self.kunjungi(self.ast)
