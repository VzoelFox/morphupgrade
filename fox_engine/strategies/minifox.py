# fox_engine/strategies/minifox.py
# PATCH-014C: Perbarui MiniFoxStrategy untuk menggunakan io_handler eksplisit.
# TODO: Tambahkan logging yang lebih detail untuk eksekusi I/O.
import os
import asyncio
import warnings
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from .base import BaseStrategy
from ..core import TugasFox, IOType
from .simplefox import SimpleFoxStrategy

class MiniFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi yang dioptimalkan untuk operasi I/O-bound.
    Menggunakan ThreadPoolExecutor khusus untuk menangani tugas I/O
    tanpa memblokir event loop utama.
    """

    def __init__(self, max_io_workers: Optional[int] = None):
        """
        Inisialisasi strategi MiniFox.
        Jumlah worker I/O dapat dikonfigurasi melalui argumen atau variabel lingkungan.
        """
        # Konfigurasi fleksibel untuk jumlah worker I/O
        self.max_io_workers = max_io_workers or int(os.getenv('FOX_IO_WORKERS', 4))

        # Inisialisasi executor secara 'lazy' saat dibutuhkan
        self.io_executor = None
        self._initialized = False

    async def _initialize(self):
        """Inisialisasi ThreadPoolExecutor saat pertama kali dibutuhkan."""
        if not self._initialized:
            self.io_executor = ThreadPoolExecutor(
                max_workers=self.max_io_workers,
                thread_name_prefix="minifox_io_"
            )
            self._initialized = True
            # TODO: Tambahkan logging untuk inisialisasi

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi tugas I/O menggunakan io_handler eksplisit.
        Jika io_handler valid, tugas dijalankan di thread pool I/O.
        Jika tidak, tugas dialihkan ke SimpleFoxStrategy.
        """
        await self._initialize()

        if tugas.jenis_operasi == IOType.FILE:
            if tugas.io_handler and callable(tugas.io_handler):
                loop = asyncio.get_running_loop()

                def io_wrapper():
                    """Wrapper untuk menangkap hasil dan jumlah byte."""
                    # io_handler diharapkan mengembalikan tuple (hasil, jumlah_byte)
                    hasil, jumlah_byte = tugas.io_handler()
                    tugas.bytes_processed = jumlah_byte
                    return hasil

                future = loop.run_in_executor(
                    self.io_executor,
                    io_wrapper
                )

                if tugas.batas_waktu:
                    return await asyncio.wait_for(future, timeout=tugas.batas_waktu)
                return await future

            # Fallback jika io_handler tidak ada atau tidak valid
            pesan_peringatan = (
                f"MiniFox: io_handler tidak ditemukan atau tidak valid "
                f"untuk tugas '{tugas.nama}'. Kembali ke SimpleFox."
            )
            warnings.warn(pesan_peringatan)
            return await SimpleFoxStrategy().execute(tugas)

        # Fallback untuk tugas non-I/O
        return await SimpleFoxStrategy().execute(tugas)

    def shutdown(self):
        """Membersihkan sumber daya ThreadPoolExecutor."""
        if self.io_executor:
            self.io_executor.shutdown(wait=True)
            # TODO: Tambahkan logging untuk shutdown
