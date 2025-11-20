# fox_engine/errors.py
# PATCH-017A: Tambahkan sistem eksepsi kustom untuk penanganan galat yang lebih baik.
"""
Modul ini mendefinisikan eksepsi kustom untuk Fox Engine.
Menggunakan eksepsi spesifik memungkinkan penanganan galat yang lebih
terperinci dan informatif di seluruh library.
"""

class FoxEngineError(Exception):
    """Kelas dasar untuk semua eksepsi yang terkait dengan Fox Engine."""
    pass

class IOKesalahan(FoxEngineError):
    """
    Dimunculkan ketika terjadi kesalahan I/O umum selama eksekusi tugas.
    Membungkus galat I/O standar seperti IOError.
    """
    def __init__(self, pesan: str, path: str):
        self.path = path
        super().__init__(f"{pesan}: {path}")

class FileTidakDitemukan(IOKesalahan):
    """
    Dimunculkan secara spesifik ketika operasi file gagal karena
    file atau direktori tidak ada.
    """
    def __init__(self, path: str):
        super().__init__(f"File atau direktori tidak ditemukan", path)

class JaringanKesalahan(FoxEngineError):
    """
    Dimunculkan ketika terjadi kesalahan terkait jaringan selama eksekusi tugas.
    """
    def __init__(self, pesan: str, alamat: str):
        self.alamat = alamat
        super().__init__(f"{pesan}: {alamat}")

class TugasTidakValidError(FoxEngineError):
    """
    Dimunculkan ketika tugas tidak memenuhi syarat validasi.
    """
    pass
