# fox_engine/internal/jalur_utama_multi_arah.py
# PATCH-021A: Refaktor besar untuk menggunakan ThreadPoolExecutor standar.
# Menghapus implementasi JalurEvakuasi dan HasilMasaDepan kustom.

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any

class JalurUtamaMultiArah:
    """
    Wrapper di sekitar ThreadPoolExecutor standar Python untuk mengelola
    pool utas pekerja. Ini mempertahankan API yang kompatibel dengan
    versi sebelumnya sambil menggunakan implementasi yang lebih robust.
    """
    def __init__(self, maks_pekerja: int, nama_prefiks_jalur: str = "JalurEvakuasi"):
        if maks_pekerja <= 0:
            raise ValueError("maks_pekerja harus lebih dari 0")

        self._executor = ThreadPoolExecutor(
            max_workers=maks_pekerja,
            thread_name_prefix=nama_prefiks_jalur
        )

    def kirim(self, fn: Callable, *args, **kwargs) -> Future:
        """
        Mengirimkan tugas (fungsi) untuk dieksekusi oleh salah satu pekerja.

        Returns:
            Sebuah objek concurrent.futures.Future.
        """
        return self._executor.submit(fn, *args, **kwargs)

    def matikan(self, tunggu: bool = True):
        """
        Mematikan pool pekerja.

        Args:
            tunggu: Jika True, akan memblokir hingga semua tugas selesai
                    dan semua pekerja berhenti.
        """
        self._executor.shutdown(wait=tunggu)

    # Alias untuk kompatibilitas
    submit = kirim
    shutdown = matikan

    # Metode ini diperlukan agar objek ini bisa digunakan langsung
    # oleh asyncio.run_in_executor
    def __enter__(self):
        return self._executor.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._executor.__exit__(exc_type, exc_val, exc_tb)
