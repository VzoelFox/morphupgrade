# morph_engine/penerjemah.py
from .node_ast import *
from .token_morph import TipeToken

def levenshtein_distance(s1, s2):
    """Menghitung jarak Levenshtein antara dua string."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class KesalahanRuntime(Exception):
    def __init__(self, pesan, node):
        token = node.token if hasattr(node, 'token') else (node.operator if hasattr(node, 'operator') else (node.nama_variabel.token if hasattr(node, 'nama_variabel') else (node.nama_fungsi.token if hasattr(node, 'nama_fungsi') else None)))
        if token:
            super().__init__(f"Kesalahan Runtime di baris {token.baris}, kolom {token.kolom}: {pesan}")
        else:
            super().__init__(f"Kesalahan Runtime: {pesan}")
        self.node = node

class Simbol:
    def __init__(self, nilai, tipe_deklarasi):
        self.nilai = nilai
        self.tipe_deklarasi = tipe_deklarasi

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
        self.tabel_simbol = {}

    def kunjungi_NodeProgram(self, node):
        for pernyataan in node.daftar_pernyataan:
            self.kunjungi(pernyataan)

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai
        nilai_var = self.kunjungi(node.nilai)
        simbol_ada = self.tabel_simbol.get(nama_var)

        if simbol_ada:
            if simbol_ada.tipe_deklarasi == TipeToken.TETAP:
                raise KesalahanRuntime(f"Variabel tetap '{nama_var}' tidak dapat diubah nilainya.", node)
            simbol_ada.nilai = nilai_var
        else:
            tipe_deklarasi = node.jenis_deklarasi.tipe
            self.tabel_simbol[nama_var] = Simbol(nilai_var, tipe_deklarasi)

    def kunjungi_NodePanggilFungsi(self, node):
        nama_fungsi = node.nama_fungsi.nilai
        if nama_fungsi == 'tulis':
            if node.argumen is None: # Validasi argumen
                raise KesalahanRuntime("Fungsi 'tulis' membutuhkan satu argumen.", node)
            argumen = self.kunjungi(node.argumen)
            print(argumen)
        else:
            raise KesalahanRuntime(f"Fungsi '{nama_fungsi}' tidak didefinisikan.", node)

    def kunjungi_NodePengenal(self, node):
        nama_var = node.nilai
        simbol = self.tabel_simbol.get(nama_var)
        if simbol is None:
            # Logika "Did you mean?"
            saran_terdekat = None
            jarak_terkecil = 3  # Ambang batas
            for nama_simbol in self.tabel_simbol:
                jarak = levenshtein_distance(nama_var, nama_simbol)
                if jarak < jarak_terkecil:
                    jarak_terkecil = jarak
                    saran_terdekat = nama_simbol

            pesan = f"Variabel '{nama_var}' tidak didefinisikan."
            if saran_terdekat:
                pesan += f" Mungkin maksud Anda '{saran_terdekat}'?"
            raise KesalahanRuntime(pesan, node)
        return simbol.nilai

    def kunjungi_NodeTeks(self, node):
        return node.nilai

    def kunjungi_NodeAngka(self, node):
        return node.nilai

    def kunjungi_NodeOperasiUnary(self, node):
        operand = self.kunjungi(node.operand)
        operator = node.operator.tipe
        if operator == TipeToken.KURANG:
            if not isinstance(operand, (int, float)):
                raise KesalahanRuntime("Operator '-' hanya bisa digunakan pada angka.", node)
            return -operand
        elif operator == TipeToken.TIDAK:
            return not bool(operand)
        raise KesalahanRuntime(f"Operator unary '{operator}' tidak didukung.", node)

    def kunjungi_NodeOperasiBiner(self, node):
        kiri = self.kunjungi(node.kiri)
        kanan = self.kunjungi(node.kanan)
        op = node.operator.tipe
        tipe_kiri_str, tipe_kanan_str = type(kiri).__name__, type(kanan).__name__

        if op == TipeToken.TAMBAH:
            if isinstance(kiri, (int, float)) and isinstance(kanan, (int, float)): return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str): return kiri + kanan
            raise KesalahanRuntime(f"Operasi '+' tidak didukung antara tipe '{tipe_kiri_str}' dan '{tipe_kanan_str}'.", node)

        if op in (TipeToken.KURANG, TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO):
            if not isinstance(kiri, (int, float)) or not isinstance(kanan, (int, float)):
                raise KesalahanRuntime(f"Operasi '{node.operator.nilai}' tidak didukung antara tipe '{tipe_kiri_str}' dan '{tipe_kanan_str}'.", node)
            if op == TipeToken.KURANG: return kiri - kanan
            if op == TipeToken.KALI: return kiri * kanan
            if op == TipeToken.BAGI:
                if kanan == 0: raise KesalahanRuntime("Tidak bisa membagi dengan nol.", node)
                return kiri / kanan
            if op == TipeToken.MODULO:
                if kanan == 0: raise KesalahanRuntime("Tidak bisa modulo dengan nol.", node)
                return kiri % kanan

        if op in (TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL, TipeToken.LEBIH_BESAR_SAMA, TipeToken.LEBIH_KECIL_SAMA):
            try:
                if op == TipeToken.SAMA_DENGAN_SAMA: return kiri == kanan
                if op == TipeToken.TIDAK_SAMA: return kiri != kanan
                if op == TipeToken.LEBIH_BESAR: return kiri > kanan
                if op == TipeToken.LEBIH_KECIL: return kiri < kanan
                if op == TipeToken.LEBIH_BESAR_SAMA: return kiri >= kanan
                if op == TipeToken.LEBIH_KECIL_SAMA: return kiri <= kanan
            except TypeError:
                raise KesalahanRuntime(f"Operasi perbandingan '{node.operator.nilai}' tidak didukung antara tipe '{tipe_kiri_str}' dan '{tipe_kanan_str}'.", node)

        if op == TipeToken.DAN: return bool(kiri) and bool(kanan)
        if op == TipeToken.ATAU: return bool(kiri) or bool(kanan)
        raise KesalahanRuntime(f"Operator biner '{op.nilai}' tidak didukung.", node)

    def interpretasi(self):
        return self.kunjungi(self.ast)
