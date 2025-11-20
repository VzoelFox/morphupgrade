# fox_engine/strategies/waterfox.py
# FASE-2.5: Ekstraksi logika WaterFox ke kelas strategi mandiri.
# FASE-3: Implementasi Hit Counter untuk JIT.

import asyncio
import logging
from typing import Any, Dict

from .base import BaseStrategy
from ..core import TugasFox
from ..internal.garis_tugas import GarisTugas

logger = logging.getLogger(__name__)

class WaterFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi Just-in-Time (JIT) adaptif.
    Melacak frekuensi eksekusi tugas dan mempromosikan ke optimisasi jika 'panas'.
    """
    def __init__(self, semafor_wfox: GarisTugas):
        """
        Inisialisasi strategi WaterFox.
        """
        self.semafor_wfox = semafor_wfox
        self.hit_counter: Dict[str, int] = {}
        self.jit_threshold = 5 # Ambang batas untuk dianggap 'hot'

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi coroutine tugas.
        Melacak hit count. Jika melebihi threshold, log (simulasi JIT compile).
        """

        # 1. Update Hit Counter
        count = self.hit_counter.get(tugas.nama, 0) + 1
        self.hit_counter[tugas.nama] = count

        if count == self.jit_threshold:
            logger.info(f"🔥 WaterFox: Tugas '{tugas.nama}' panas (hit {count}). Memicu optimisasi JIT...")
            # Di sini kita akan memanggil Optimizer.optimize() di background
            # dan menyimpan versi teroptimasi.

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
