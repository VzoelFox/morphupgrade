# fox_engine/strategies/minifox.py
# PATCH-013B: Implementasi dasar MiniFoxStrategy
import os
import asyncio
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
        Mengeksekusi tugas. Jika tugas ditandai sebagai operasi I/O,
        tugas tersebut akan dijalankan di thread pool I/O. Jika tidak,
        tugas akan dialihkan ke SimpleFoxStrategy.
        """
        await self._initialize()

        # Routing berdasarkan jenis operasi yang ditandai secara eksplisit
        if tugas.jenis_operasi == IOType.FILE:
            # Dapatkan fungsi blocking dari atribut yang dilampirkan
            blocking_func = getattr(tugas.coroutine, 'blocking_func', None)

            if not callable(blocking_func):
                # Fallback jika pola yang diharapkan tidak ditemukan
                # TODO: Tambahkan logging peringatan di sini
                return await SimpleFoxStrategy().execute(tugas)

            loop = asyncio.get_running_loop()

            # Menjalankan fungsi blocking di thread pool I/O.
            # Ini adalah cara yang benar untuk menangani I/O blocking
            # dalam aplikasi asyncio.
            future = loop.run_in_executor(
                self.io_executor,
                blocking_func  # Jalankan fungsi sinkron secara langsung
            )

            # Menangani batas waktu jika ditentukan
            if tugas.batas_waktu:
                return await asyncio.wait_for(future, timeout=tugas.batas_waktu)
            return await future

        # Fallback ke SimpleFox untuk tugas non-I/O atau yang tidak ditandai
        return await SimpleFoxStrategy().execute(tugas)

    def shutdown(self):
        """Membersihkan sumber daya ThreadPoolExecutor."""
        if self.io_executor:
            self.io_executor.shutdown(wait=True)
            # TODO: Tambahkan logging untuk shutdown
