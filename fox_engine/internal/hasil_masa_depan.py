# fox_engine/internal/hasil_masa_depan.py

import threading

class HasilMasaDepan:
    """
    Mewakili hasil dari sebuah komputasi asinkron yang dijalankan
    di 'JalurEvakuasi'. Objek ini mirip dengan 'Future' object.
    """
    def __init__(self):
        self._hasil = None
        self._pengecualian = None
        self._acara_selesai = threading.Event()

    def atur_hasil(self, hasil):
        """Menetapkan hasil dari komputasi dan menandai future sebagai selesai."""
        self._hasil = hasil
        self._acara_selesai.set()

    def atur_pengecualian(self, pengecualian):
        """Menetapkan pengecualian jika komputasi gagal dan menandai future sebagai selesai."""
        self._pengecualian = pengecualian
        self._acara_selesai.set()

    def hasil(self, timeout: float = None) -> any:
        """
        Menunggu dan mengembalikan hasil dari komputasi.

        Jika komputasi menghasilkan pengecualian, pengecualian itu akan
        dimunculkan kembali oleh metode ini.
        """
        self._acara_selesai.wait(timeout)
        if self._pengecualian:
            raise self._pengecualian
        return self._hasil
