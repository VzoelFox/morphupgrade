# fox_engine/strategies/thunderfox.py
# FASE-2.5: Ekstraksi logika ThunderFox ke kelas strategi mandiri.
import asyncio
import time
from typing import Any, Callable

from .base import BaseStrategy
from ..core import TugasFox
from ..internal.jalur_utama_multi_arah import JalurUtamaMultiArah

class ThunderFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi yang disimulasikan sebagai kompilasi Ahead-of-Time (AOT).
    Dirancang untuk tugas-tugas berat CPU, dieksekusi dalam ThreadPoolExecutor
    untuk menghindari pemblokan event loop utama.
    """

    def __init__(self, eksekutor_tfox: JalurUtamaMultiArah):
        """
        Inisialisasi strategi ThunderFox.

        Args:
            eksekutor_tfox: Eksekutor bersama dari ManajerFox untuk menjalankan tugas.
        """
        self.eksekutor_tfox = eksekutor_tfox

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi coroutine tugas di dalam ThreadPoolExecutor untuk mensimulasikan
        operasi non-blocking untuk tugas berat CPU.
        """
        loop = asyncio.get_event_loop()

        def tugas_terbungkus_aot() -> Any:
            """
            Wrapper yang menjalankan coroutine di dalam thread eksekutor.
            Ini mensimulasikan bagaimana kompilasi AOT dapat memindahkan beban kerja
            berat dari event loop utama.
            """
            try:
                waktu_mulai_eksekusi = time.time()
                loop_tugas = asyncio.new_event_loop()
                asyncio.set_event_loop(loop_tugas)
                hasil = loop_tugas.run_until_complete(tugas.coroutine())
                durasi_eksekusi = time.time() - waktu_mulai_eksekusi

                # Simulasi 'pembayaran' dari waktu kompilasi AOT.
                # Semakin lama tugas berjalan, semakin besar keuntungan optimisasinya.
                keuntungan_optimisasi = max(0.05, min(0.25, durasi_eksekusi * 0.1))
                time.sleep(keuntungan_optimisasi)

                return hasil
            finally:
                loop_tugas.close()

        # Mengirim wrapper ke eksekutor thread pool kustom
        masa_depan = self.eksekutor_tfox.kirim(tugas_terbungkus_aot)

        # Menggunakan loop.run_in_executor untuk menunggu hasil dari thread
        # tanpa memblokir event loop utama.
        coro_hasil = loop.run_in_executor(None, masa_depan.hasil)

        if tugas.batas_waktu:
            return await asyncio.wait_for(coro_hasil, timeout=tugas.batas_waktu)
        return await coro_hasil

    async def shutdown(self):
        """
        ThunderFoxStrategy menggunakan eksekutor bersama yang dikelola oleh ManajerFox,
        sehingga tidak ada tindakan shutdown spesifik yang diperlukan di sini.
        """
        pass
