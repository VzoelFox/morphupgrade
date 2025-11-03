# morph_engine/penerjemah.py
from .node_ast import *
from .token_morph import TipeToken

class KesalahanRuntime(Exception):
    pass

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
            raise KesalahanRuntime(f"Fungsi '{nama_fungsi}' tidak didefinisikan.")

    def kunjungi_NodePengenal(self, node):
        """Mengambil nilai variabel dari tabel simbol."""
        nama_var = node.nilai
        nilai = self.tabel_simbol.get(nama_var)
        if nilai is None:
            raise KesalahanRuntime(f"Variabel '{nama_var}' tidak didefinisikan.")
        return nilai

    def kunjungi_NodeTeks(self, node):
        """Mengembalikan nilai literal dari teks."""
        return node.nilai

    # --- Metode Visitor Baru untuk Sprint 1 ---

    def kunjungi_NodeAngka(self, node):
        """Mengembalikan nilai dari node angka (int atau float)."""
        return node.nilai

    def kunjungi_NodeOperasiUnary(self, node):
        """Mengevaluasi operasi unary (negasi angka atau logika)."""
        operand = self.kunjungi(node.operand)
        operator = node.operator.tipe

        if operator == TipeToken.KURANG:
            if not isinstance(operand, (int, float)):
                raise KesalahanRuntime("Operator '-' hanya bisa digunakan pada angka.")
            return -operand
        elif operator == TipeToken.TIDAK:
            return not bool(operand)

        # Fallback jika ada operator unary lain yang belum diimplementasi
        raise KesalahanRuntime(f"Operator unary '{operator}' tidak didukung.")

    def kunjungi_NodeOperasiBiner(self, node):
        """Mengevaluasi operasi biner (aritmatika, perbandingan, logika)."""
        kiri = self.kunjungi(node.kiri)
        kanan = self.kunjungi(node.kanan)
        op = node.operator.tipe

        # Operasi Aritmatika
        if op in (TipeToken.TAMBAH, TipeToken.KURANG, TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO):
            if not isinstance(kiri, (int, float)) or not isinstance(kanan, (int, float)):
                raise KesalahanRuntime(f"Operasi '{node.operator.nilai}' membutuhkan operan numerik.")
            if op == TipeToken.TAMBAH: return kiri + kanan
            if op == TipeToken.KURANG: return kiri - kanan
            if op == TipeToken.KALI: return kiri * kanan
            if op == TipeToken.BAGI:
                if kanan == 0: raise KesalahanRuntime("Tidak bisa membagi dengan nol.")
                return kiri / kanan
            if op == TipeToken.MODULO:
                if kanan == 0: raise KesalahanRuntime("Tidak bisa modulo dengan nol.")
                return kiri % kanan

        # Operasi Perbandingan
        if op == TipeToken.SAMA_DENGAN_SAMA: return kiri == kanan
        if op == TipeToken.TIDAK_SAMA: return kiri != kanan
        if op == TipeToken.LEBIH_BESAR: return kiri > kanan
        if op == TipeToken.LEBIH_KECIL: return kiri < kanan
        if op == TipeToken.LEBIH_BESAR_SAMA: return kiri >= kanan
        if op == TipeToken.LEBIH_KECIL_SAMA: return kiri <= kanan

        # Operasi Logika
        if op == TipeToken.DAN: return bool(kiri) and bool(kanan)
        if op == TipeToken.ATAU: return bool(kiri) or bool(kanan)

        # Fallback jika ada operator biner lain yang belum diimplementasi
        raise KesalahanRuntime(f"Operator biner '{op}' tidak didukung.")

    def interpretasi(self):
        """Memulai proses interpretasi dari node akar (program)."""
        try:
            return self.kunjungi(self.ast)
        except (NameError, TypeError, ZeroDivisionError) as e:
            # Menangkap kesalahan Python bawaan dan membungkusnya dalam KesalahanRuntime
            raise KesalahanRuntime(str(e))
