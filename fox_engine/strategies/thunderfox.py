# fox_engine/strategies/thunderfox.py
# FASE-2.5: Ekstraksi logika ThunderFox ke kelas strategi mandiri.
import asyncio
import time
from typing import Any, Callable

from .base import BaseStrategy
from ..core import TugasFox
from ..internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from .waterfox import WaterFoxStrategy
from .simplefox import SimpleFoxStrategy

class ThunderFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi yang disimulasikan sebagai kompilasi Ahead-of-Time (AOT).
    Dirancang untuk tugas-tugas berat CPU, dieksekusi dalam ThreadPoolExecutor
    untuk menghindari pemblokan event loop utama.
    """

    def __init__(self, eksekutor_tfox: JalurUtamaMultiArah, waterfox_strategy: WaterFoxStrategy):
        """
        Inisialisasi strategi ThunderFox.

        Args:
            eksekutor_tfox: Eksekutor bersama dari ManajerFox untuk menjalankan tugas.
            waterfox_strategy: Instans strategi WaterFox untuk fallback tugas async.
        """
        self.eksekutor_tfox = eksekutor_tfox
        self.waterfox_strategy = waterfox_strategy

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi tugas berat CPU secara non-blocking.
        Mendelegasikan tugas async ke WaterFoxStrategy.
        """
        # Periksa apakah tugas adalah coroutine atau fungsi sinkron
        if asyncio.iscoroutinefunction(tugas.coroutine_func):
            # Jika coroutine, lebih cocok dijalankan oleh WaterFox
            return await self.waterfox_strategy.execute(tugas)

        # Untuk fungsi sinkron, jalankan di executor yang disediakan
        loop = asyncio.get_running_loop()

        # Bungkus fungsi sinkron dan argumennya untuk eksekusi
        func_wrapper = lambda: tugas.coroutine_func(*tugas.coroutine_args, **tugas.coroutine_kwargs)

        try:
            # Jalankan di executor kustom yang disuntikkan dari ManajerFox
            masa_depan = loop.run_in_executor(
                self.eksekutor_tfox, func_wrapper
            )

            if tugas.batas_waktu:
                return await asyncio.wait_for(masa_depan, timeout=tugas.batas_waktu)
            return await masa_depan
        except AttributeError:
             return await SimpleFoxStrategy().execute(tugas)

    async def shutdown(self):
        """
        ThunderFoxStrategy menggunakan eksekutor bersama yang dikelola oleh ManajerFox,
        sehingga tidak ada tindakan shutdown spesifik yang diperlukan di sini.
        """
        pass
