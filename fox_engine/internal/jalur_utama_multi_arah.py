# fox_engine/internal/jalur_utama_multi_arah.py

from queue import Queue
from typing import Callable, Optional

from .hasil_masa_depan import HasilMasaDepan
from .jalur_evakuasi import JalurEvakuasi

class JalurUtamaMultiArah:
    """
    Mengelola sebuah pool dari JalurEvakuasi (utas pekerja) untuk
    menjalankan tugas secara asinkron. Mirip dengan ThreadPoolExecutor.
    """
    def __init__(self, maks_pekerja: int, nama_prefiks_jalur: str = "JalurEvakuasi"):
        if maks_pekerja <= 0:
            raise ValueError("maks_pekerja harus lebih dari 0")

        self._antrean_tugas = Queue()
        self._daftar_pekerja = []

        for i in range(maks_pekerja):
            pekerja = JalurEvakuasi(
                antrean_tugas=self._antrean_tugas,
                nama=f"{nama_prefiks_jalur}_{i}"
            )
            pekerja.start()
            self._daftar_pekerja.append(pekerja)

    def kirim(self, fn: Callable, *args, **kwargs) -> HasilMasaDepan:
        """
        Mengirimkan tugas (fungsi) untuk dieksekusi oleh salah satu pekerja.

        Returns:
            Sebuah objek HasilMasaDepan yang akan berisi hasil dari eksekusi.
        """
        # Bungkus fungsi dan argumennya
        tugas = lambda: fn(*args, **kwargs)
        masa_depan = HasilMasaDepan()
        self._antrean_tugas.put((tugas, masa_depan))
        return masa_depan

    def matikan(self, tunggu: bool = True):
        """
        Mematikan pool pekerja.

        Args:
            tunggu: Jika True, akan memblokir hingga semua tugas selesai
                    dan semua pekerja berhenti.
        """
        # Kirim sinyal berhenti untuk setiap pekerja
        for _ in self._daftar_pekerja:
            self._antrean_tugas.put((None, None))

        if tunggu:
            # Tunggu semua pekerja selesai
            for pekerja in self._daftar_pekerja:
                pekerja.join()

    # Alias untuk kompatibilitas
    submit = kirim
    shutdown = matikan
