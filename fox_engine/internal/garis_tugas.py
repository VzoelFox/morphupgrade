# fox_engine/internal/garis_tugas.py

import asyncio

class GarisTugas:
    """
    Sebuah implementasi dari semaphore, yang mengontrol akses ke sumber daya
    bersama dengan sebuah penghitung. Mirip dengan asyncio.Semaphore.

    Jika penghitung lebih besar dari nol, ia akan dikurangi satu dan tugas
    diizinkan masuk. Jika nol, tugas akan diblokir hingga tugas lain
    melepaskan semaphore.
    """
    def __init__(self, nilai: int = 1):
        if nilai < 0:
            raise ValueError("Nilai GarisTugas harus >= 0")
        self._semaphore = asyncio.Semaphore(nilai)

    async def dapatkan(self):
        """
        Memperoleh semaphore.

        Menunggu jika perlu hingga semaphore dapat diperoleh.
        """
        await self._semaphore.acquire()

    def lepaskan(self):
        """
        Melepaskan semaphore, menambah penghitung internal.
        """
        self._semaphore.release()

    def terkunci(self) -> bool:
        """
        Mengembalikan True jika semaphore tidak dapat diperoleh segera.
        """
        return self._semaphore.locked()

    async def __aenter__(self):
        """Memasuki context manager asinkron, memperoleh semaphore."""
        await self.dapatkan()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Keluar dari context manager asinkron, melepaskan semaphore."""
        self.lepaskan()
