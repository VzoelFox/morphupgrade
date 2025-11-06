# fox_engine/strategies/waterfox.py
# FASE-2.5: Ekstraksi logika WaterFox ke kelas strategi mandiri.
import asyncio
from typing import Any

from .base import BaseStrategy
from ..core import TugasFox
from ..internal.garis_tugas import GarisTugas

class WaterFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi Just-in-Time (JIT) adaptif.
    Menggunakan semaphore untuk membatasi konkurensi, ideal untuk beban kerja
    campuran yang memerlukan skala adaptif tanpa overhead dari thread pool.
    """
    def __init__(self, semafor_wfox: GarisTugas):
        """
        Inisialisasi strategi WaterFox.

        Args:
            semafor_wfox: Semaphore bersama dari ManajerFox untuk mengontrol konkurensi.
        """
        self.semafor_wfox = semafor_wfox

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi coroutine tugas di bawah kendali semaphore untuk
        mengelola konkurensi.
        """
        async with self.semafor_wfox:
            coro = tugas.coroutine_func(*tugas.coroutine_args, **tugas.coroutine_kwargs)
            if tugas.batas_waktu:
                return await asyncio.wait_for(coro, timeout=tugas.batas_waktu)
            return await coro

    async def shutdown(self):
        """
        WaterFoxStrategy menggunakan semaphore bersama yang dikelola oleh ManajerFox,
        sehingga tidak ada tindakan shutdown spesifik yang diperlukan di sini.
        """
        pass
