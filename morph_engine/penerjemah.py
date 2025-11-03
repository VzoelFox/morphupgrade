# morph_engine/penerjemah.py
# Changelog:
# - PATCH-012B: Implementasi fungsi bawaan `jumlah()`.
#              - Mendukung multi-argumen numerik (int/float).
#              - Validasi tipe argumen yang ketat.
#              - Mengembalikan 0 jika tanpa argumen.
# - PATCH-012A: Memperbaiki validasi argumen untuk fungsi `panjang`.
#              - Memastikan pesan error spesifik saat jumlah argumen salah.
# - PATCH-011: Membangun fondasi untuk manajemen scope.
#              - `tabel_simbol` diubah menjadi stack of dictionaries (`[{}]`).
#              - Logika pencarian, deklarasi, dan assignment diubah untuk mendukung scope.
#              - Menambahkan method `masuk_scope` dan `keluar_scope` untuk masa depan.
# - PATCH-009: Menambahkan pencegahan deklarasi variabel duplikat.
#              - Class `Simbol` sekarang menyimpan token deklarasi.
#              - `kunjungi_NodeDeklarasiVariabel` melempar error jika variabel sudah ada.
# - PATCH-010: Menambahkan metode `kunjungi_NodeAssignment` untuk menangani
#              logika assignment.
#              - Memisahkan logika deklarasi murni di `kunjungi_NodeDeklarasiVariabel`.
#              - Memperbaiki pesan error untuk assignment ke var yang belum ada.

from .node_ast import *
from .token_morph import TipeToken

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2): return levenshtein_distance(s2, s1)
    if len(s2) == 0: return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions, deletions = previous_row[j + 1] + 1, current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class KesalahanRuntime(Exception):
    def __init__(self, pesan, node):
        token = None
        if hasattr(node, 'nama_variabel') and hasattr(node.nama_variabel, 'token'): token = node.nama_variabel.token
        elif hasattr(node, 'token'): token = node.token
        elif hasattr(node, 'operator'): token = node.operator
        elif hasattr(node, 'nama_fungsi') and hasattr(node.nama_fungsi, 'token'): token = node.nama_fungsi.token
        if token: super().__init__(f"Kesalahan Runtime di baris {token.baris}, kolom {token.kolom}: {pesan}")
        else: super().__init__(f"Kesalahan Runtime: {pesan}")
        self.node = node

class Simbol:
    def __init__(self, nilai, tipe_deklarasi, token_deklarasi):
        self.nilai = nilai
        self.tipe_deklarasi = tipe_deklarasi
        self.token_deklarasi = token_deklarasi

class PengunjungNode:
    def kunjungi(self, node):
        nama_metode = f'kunjungi_{type(node).__name__}'
        pengunjung = getattr(self, nama_metode, self.kunjungan_umum)
        return pengunjung(node)
    def kunjungan_umum(self, node):
        raise Exception(f'Tidak ada metode kunjungi_{type(node).__name__}')

class Penerjemah(PengunjungNode):
    def __init__(self, ast):
        self.ast = ast
        self.tabel_simbol = [{}] # Stack of scopes, dimulai dengan global scope

    def masuk_scope(self):
        """
        Mendorong scope baru ke dalam stack.
        Dipanggil saat memasuki blok baru (jika, selama, fungsi).
        Mendukung variable shadowing standar.
        """
        # TODO: Panggil masuk_scope() saat masuk blok jika/selama/fungsi
        self.tabel_simbol.append({})

    def keluar_scope(self):
        """Menghapus scope saat ini dari stack."""
        self.tabel_simbol.pop()

    def _cari_simbol(self, nama_var):
        """Mencari simbol dari scope terdalam ke terluar."""
        for scope in reversed(self.tabel_simbol):
            if nama_var in scope:
                return scope[nama_var]
        return None

    def kunjungi_NodeProgram(self, node):
        for pernyataan in node.daftar_pernyataan:
            self.kunjungi(pernyataan)

    def kunjungi_NodeDeklarasiVariabel(self, node):
        nama_var = node.nama_variabel.nilai
        scope_sekarang = self.tabel_simbol[-1]

        if nama_var in scope_sekarang:
            simbol_lama = scope_sekarang[nama_var]
            raise KesalahanRuntime(
                f"Variabel '{nama_var}' sudah dideklarasikan di scope ini pada baris {simbol_lama.token_deklarasi.baris}.",
                node
            )

        nilai_var = self.kunjungi(node.nilai)
        tipe_deklarasi = node.jenis_deklarasi.tipe
        token_deklarasi = node.nama_variabel.token
        scope_sekarang[nama_var] = Simbol(nilai_var, tipe_deklarasi, token_deklarasi)

    def kunjungi_NodeAssignment(self, node):
        nama_var = node.nama_variabel.nilai
        simbol = self._cari_simbol(nama_var)

        if simbol is None:
            # Menggunakan logika yang sama dengan NodePengenal untuk pesan error
            semua_simbol_terlihat = set()
            for scope in self.tabel_simbol:
                semua_simbol_terlihat.update(scope.keys())

            saran_terdekat = None
            jarak_terkecil = 3
            for nama_simbol in semua_simbol_terlihat:
                jarak = levenshtein_distance(nama_var, nama_simbol)
                if jarak < jarak_terkecil:
                    jarak_terkecil, saran_terdekat = jarak, nama_simbol

            pesan = f"Variabel '{nama_var}' belum dideklarasikan. Gunakan 'biar {nama_var} = ...' untuk deklarasi baru."
            if saran_terdekat:
                pesan += f" Mungkin maksud Anda '{saran_terdekat}'?"
            raise KesalahanRuntime(pesan, node)

        if simbol.tipe_deklarasi == TipeToken.TETAP:
            raise KesalahanRuntime(f"Variabel tetap '{nama_var}' tidak dapat diubah nilainya.", node)

        nilai_var = self.kunjungi(node.nilai)
        simbol.nilai = nilai_var

    def kunjungi_NodePanggilFungsi(self, node):
        nama_fungsi = node.nama_fungsi.nilai
        argumen = [self.kunjungi(arg) for arg in node.daftar_argumen]

        if nama_fungsi == 'tulis':
            # Fungsi 'tulis' sekarang dapat menerima nol atau lebih argumen
            output = " ".join(map(str, argumen))
            print(output)
        elif nama_fungsi == 'panjang':
            # Phase 1: Fix Validasi panjang() (5 menit)
            if len(argumen) != 1:
                raise KesalahanRuntime(
                    f"Fungsi 'panjang' membutuhkan tepat 1 argumen, tetapi menerima {len(argumen)}.",
                    node
                )
            arg = argumen[0]
            if isinstance(arg, str):
                return len(arg)
            raise KesalahanRuntime(f"Fungsi 'panjang()' tidak mendukung tipe '{type(arg).__name__}'.", node)
        elif nama_fungsi == 'jumlah':
            # Phase 2: Implement jumlah() (10 menit)
            for i, arg in enumerate(argumen):
                if not isinstance(arg, (int, float)):
                    raise KesalahanRuntime(
                        f"Fungsi 'jumlah' hanya menerima angka. Argumen ke-{i+1} adalah tipe '{type(arg).__name__}'.",
                        node
                    )
            return sum(argumen) if argumen else 0
        else:
            raise KesalahanRuntime(f"Fungsi '{nama_fungsi}' tidak didefinisikan.", node)

    def kunjungi_NodePengenal(self, node):
        nama_var = node.nilai
        simbol = self._cari_simbol(nama_var)
        if simbol is None:
            semua_simbol_terlihat = set()
            for scope in self.tabel_simbol:
                semua_simbol_terlihat.update(scope.keys())

            saran_terdekat = None
            jarak_terkecil = 3
            for nama_simbol in semua_simbol_terlihat:
                jarak = levenshtein_distance(nama_var, nama_simbol)
                if jarak < jarak_terkecil:
                    jarak_terkecil, saran_terdekat = jarak, nama_simbol

            pesan = f"Variabel '{nama_var}' tidak didefinisikan."
            if saran_terdekat:
                pesan += f" Mungkin maksud Anda '{saran_terdekat}'?"
            raise KesalahanRuntime(pesan, node)
        return simbol.nilai

    def kunjungi_NodeTeks(self, node): return node.nilai
    def kunjungi_NodeAngka(self, node): return node.nilai
    def kunjungi_NodeBoolean(self, node): return node.nilai

    def kunjungi_NodeJika(self, node):
        self.masuk_scope()
        try:
            kondisi = self.kunjungi(node.kondisi)
            if bool(kondisi):
                for pernyataan in node.blok_maka:
                    self.kunjungi(pernyataan)
        finally:
            self.keluar_scope()

    def kunjungi_NodeOperasiUnary(self, node):
        operand = self.kunjungi(node.operand)
        operator = node.operator.tipe
        if operator == TipeToken.KURANG:
            if not isinstance(operand, (int, float)): raise KesalahanRuntime("Operator '-' hanya bisa digunakan pada angka.", node)
            return -operand
        elif operator == TipeToken.TIDAK:
            return not bool(operand)
        raise KesalahanRuntime(f"Operator unary '{operator}' tidak didukung.", node)

    def kunjungi_NodeOperasiBiner(self, node):
        kiri, kanan, op = self.kunjungi(node.kiri), self.kunjungi(node.kanan), node.operator.tipe
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
