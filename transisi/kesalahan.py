# morph_engine/kesalahan.py
# Modul untuk mendefinisikan exception kustom untuk interpreter MORPH.

from .morph_t import Token

class KesalahanMorph(Exception):
    """Kelas dasar untuk semua kesalahan yang terjadi di lingkungan MORPH."""
    def __init__(self, token: Token | None, pesan: str):
        self.token = token
        self.pesan = pesan
        # Inisialisasi baris dan kolom dengan nilai default jika token tidak ada
        self.baris = token.baris if token else 0
        self.kolom = token.kolom if token else 0
        super().__init__(pesan)

    def __str__(self):
        return f"[{self.__class__.__name__}] di baris {self.baris}: {self.pesan}"

# --- KESALAHAN RUNTIME ---

class KesalahanRuntime(KesalahanMorph):
    """Kelas dasar untuk kesalahan yang terjadi saat eksekusi (runtime)."""
    pass

class KesalahanPola(KesalahanRuntime):
    """Terjadi ketika pattern matching tidak exhaustive atau tidak valid."""
    pass

class KesalahanTipe(KesalahanRuntime):
    """Terjadi ketika operasi menerima tipe data yang tidak sesuai."""
    pass

class KesalahanNama(KesalahanRuntime):
    """Terjadi ketika sebuah variabel atau nama tidak ditemukan."""
    pass

class KesalahanIndeks(KesalahanRuntime):
    """Terjadi ketika indeks daftar di luar jangkauan."""
    pass

class KesalahanKunci(KesalahanRuntime):
    """Terjadi ketika kunci kamus tidak ditemukan atau tipe kunci tidak valid."""
    pass

class KesalahanPembagianNol(KesalahanRuntime):
    """Terjadi saat mencoba membagi dengan nol."""
    pass

# --- KESALAHAN FFI ---

class KesalahanFFI(KesalahanRuntime):
    """Base untuk semua FFI-related errors."""
    def __init__(self, token, pesan, python_exception=None):
        super().__init__(token, pesan)
        self.python_exception = python_exception

class KesalahanImportFFI(KesalahanFFI):
    """Terjadi saat gagal import Python module."""
    pass

class KesalahanPanggilanFFI(KesalahanFFI):
    """Terjadi saat Python function call error."""
    pass

class KesalahanAtributFFI(KesalahanFFI):
    """Terjadi saat akses attribute Python tidak ditemukan."""
    pass
