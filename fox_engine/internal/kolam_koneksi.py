# fox_engine/internal/kolam_koneksi.py
# PATCH-018A: Modul baru untuk mengelola kolam koneksi jaringan.
# PATCH-019A: (Perbaikan) Implementasikan pool sesi yang sebenarnya untuk mencegah kebocoran koneksi.
"""
Modul ini menyediakan manajemen kolam koneksi untuk operasi jaringan
di dalam MiniFoxStrategy. Ini mengabstraksi pembuatan dan pembersihan
sesi klien HTTP.
"""

import aiohttp
import asyncio
from typing import Optional, Set

class KolamKoneksiAIOHTTP:
    """
    Mengelola kolam sesi aiohttp.ClientSession untuk digunakan kembali.
    Mencegah biaya pembuatan sesi baru untuk setiap permintaan.
    """

    def __init__(self, maks_ukuran_kolam: int = 20):
        self._maks_ukuran_kolam = maks_ukuran_kolam
        self._kolam: asyncio.Queue[aiohttp.ClientSession] = asyncio.Queue(maxsize=maks_ukuran_kolam)
        self._sesi_aktif: Set[aiohttp.ClientSession] = set()
        self._kunci = asyncio.Lock()

    async def dapatkan_sesi(self) -> aiohttp.ClientSession:
        """
        Mengambil sesi dari kolam atau membuat yang baru jika kolam kosong
        dan belum mencapai ukuran maksimum.

        Returns:
            aiohttp.ClientSession: Sesi klien HTTP yang aktif.
        """
        async with self._kunci:
            if not self._kolam.empty():
                return await self._kolam.get()

            if len(self._sesi_aktif) < self._maks_ukuran_kolam:
                # Buat sesi baru jika kita masih di bawah batas
                sesi_baru = aiohttp.ClientSession()
                self._sesi_aktif.add(sesi_baru)
                return sesi_baru

        # Jika kolam kosong dan kita sudah mencapai batas, tunggu sesi tersedia
        return await self._kolam.get()

    async def kembalikan_sesi(self, sesi: aiohttp.ClientSession):
        """
        Mengembalikan sesi ke kolam untuk digunakan kembali.

        Args:
            sesi (aiohttp.ClientSession): Sesi yang akan dikembalikan.
        """
        if sesi in self._sesi_aktif and not sesi.closed:
            await self._kolam.put(sesi)

    async def tutup(self):
        """
        Menutup semua sesi aktif yang dikelola oleh kolam.
        Ini adalah coroutine dan harus di-await.
        """
        async with self._kunci:
            for sesi in self._sesi_aktif:
                if not sesi.closed:
                    await sesi.close()
            self._sesi_aktif.clear()
            # Bersihkan antrian
            while not self._kolam.empty():
                self._kolam.get_nowait()
