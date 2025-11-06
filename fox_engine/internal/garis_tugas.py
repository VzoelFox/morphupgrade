# fox_engine/internal/garis_tugas.py
import asyncio

class GarisTugas:
    """
    Implementasi Semaphore dari prinsip dasar menggunakan asyncio.Condition.
    Mengontrol akses ke sumber daya bersama dengan sebuah penghitung.
    """
    def __init__(self, nilai: int = 1):
        if nilai < 0:
            raise ValueError("Nilai GarisTugas harus >= 0")
        self._nilai = nilai
        self._kondisi = asyncio.Condition()

    async def dapatkan(self):
        """Memperoleh semaphore, menunggu jika penghitung adalah nol."""
        async with self._kondisi:
            await self._kondisi.wait_for(lambda: self._nilai > 0)
            self._nilai -= 1

    async def lepaskan(self):
        """
        Melepaskan semaphore, menambah penghitung internal dan memberi tahu
        satu tugas yang menunggu.
        """
        async with self._kondisi:
            self._nilai += 1
            self._kondisi.notify(1)

    def terkunci(self) -> bool:
        """Mengembalikan True jika semaphore tidak dapat diperoleh segera."""
        return self._nilai == 0

    async def __aenter__(self):
        """Memasuki context manager asinkron, memperoleh semaphore."""
        await self.dapatkan()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Keluar dari context manager asinkron, melepaskan semaphore."""
        await self.lepaskan()
