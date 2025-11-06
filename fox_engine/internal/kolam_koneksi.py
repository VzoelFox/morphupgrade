# fox_engine/internal/kolam_koneksi.py
# PATCH-018A: Modul baru untuk mengelola kolam koneksi jaringan.
"""
Modul ini menyediakan manajemen kolam koneksi untuk operasi jaringan
di dalam MiniFoxStrategy. Ini mengabstraksi pembuatan dan pembersihan
sesi klien HTTP.
"""

import aiohttp
import asyncio
from typing import Optional

class KolamKoneksiAIOHTTP:
    """
    Pengelola untuk aiohttp.ClientSession, memastikan sesi tunggal
    dibuat dan ditutup dengan benar. aiohttp sendiri menangani
    kolam koneksi internal secara efisien.
    """

    def __init__(self):
        self._sesi: Optional[aiohttp.ClientSession] = None
        self._kunci = asyncio.Lock()

    async def dapatkan_sesi(self) -> aiohttp.ClientSession:
        """
        Mengambil sesi aiohttp yang ada atau membuat yang baru jika belum ada.
        Ini adalah metode thread-safe dan coroutine-safe.

        Returns:
            aiohttp.ClientSession: Sesi klien HTTP yang aktif.
        """
        async with self._kunci:
            if self._sesi is None or self._sesi.closed:
                # TODO: Izinkan konfigurasi kustom untuk ClientSession
                self._sesi = aiohttp.ClientSession()
        return self._sesi

    async def tutup(self):
        """
        Menutup sesi aiohttp jika ada dan sedang terbuka.
        Ini adalah coroutine dan harus di-await.
        """
        async with self._kunci:
            if self._sesi and not self._sesi.closed:
                await self._sesi.close()
                self._sesi = None
