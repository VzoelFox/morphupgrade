# fox_engine/internal/kunci_async.py
# PERBAIKAN: Mengganti implementasi Kunci berbasis threading dengan asyncio.Lock
# untuk mendukung asynchronous context manager (`async with`).

import asyncio

class Kunci:
    """
    Wrapper sederhana di sekitar asyncio.Lock untuk menyediakan antarmuka
    yang konsisten dalam ekosistem Fox Engine.
    """
    def __init__(self):
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        """Memasuki context manager asinkron, memperoleh kunci."""
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Keluar dari context manager asinkron, melepaskan kunci."""
        self._lock.release()

    async def dapatkan(self):
        """Memperoleh kunci secara eksplisit."""
        await self._lock.acquire()

    def lepaskan(self):
        """Melepaskan kunci secara eksplisit."""
        self._lock.release()
