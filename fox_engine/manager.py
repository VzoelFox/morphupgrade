# fox_engine/manager.py
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any
import heapq

from .core import FoxMode, TugasFox, MetrikFox, StatusTugas
from .safety import PemutusSirkuit, PencatatTugas

class ManajerFox:
    """
    Manajer inti yang mengatur siklus hidup tugas, pemilihan mode eksekusi (AoT/JIT),
    dan menerapkan mekanisme keamanan dasar untuk Fase 1.
    """

    def __init__(self,
                 maks_pekerja_tfox: int = 2,      # Pengaturan default yang konservatif
                 maks_konkuren_wfox: int = 10,
                 aktifkan_aot: bool = True):

        # Konfigurasi
        self.maks_pekerja_tfox = maks_pekerja_tfox
        self.maks_konkuren_wfox = maks_konkuren_wfox
        self.aktifkan_aot = aktifkan_aot

        # Lingkungan eksekusi
        self.eksekutor_tfox = ThreadPoolExecutor(
            max_workers=maks_pekerja_tfox,
            thread_name_prefix="thunderfox_"
        )
        self.semafor_wfox = asyncio.Semaphore(maks_konkuren_wfox)

        # Sistem keamanan
        self.pemutus_sirkuit = PemutusSirkuit()
        self.pencatat_tugas = PencatatTugas()
        self.pemutus_sirkuit_tfox = PemutusSirkuit(ambang_kegagalan=3, batas_waktu_reset=30.0)

        # Manajemen status
        self.metrik = MetrikFox()
        self._sedang_shutdown = False
        self._kunci = threading.RLock()

        # Cache untuk kompilasi AoT (akan dikembangkan di Fase 2)
        self.cache_aot: Dict[str, Any] = {}

        print(f"🐺 ManajerFox diinisialisasi: {maks_pekerja_tfox} pekerja tfox, {maks_konkuren_wfox} wfox konkuren")

    async def kirim(self, tugas: TugasFox) -> Any:
        """Mengirimkan tugas untuk eksekusi dengan pemeriksaan keamanan dasar."""

        # Pemeriksaan awal
        if self._sedang_shutdown:
            raise RuntimeError("ManajerFox sedang dalam proses shutdown")

        if not self.pemutus_sirkuit.bisa_eksekusi():
            raise RuntimeError("Pemutus sirkuit terbuka - sistem kemungkinan kelebihan beban")

        if not self.pencatat_tugas.daftarkan_tugas(tugas):
            raise ValueError(f"Tugas '{tugas.nama}' sudah berjalan")

        e = None
        try:
            # Pemilihan mode
            if tugas.mode == FoxMode.AUTO:
                tugas.mode = self._pilih_mode(tugas)

            # Eksekusi berdasarkan mode
            if tugas.mode == FoxMode.THUNDERFOX:
                if not self.pemutus_sirkuit_tfox.bisa_eksekusi():
                    # Kembali ke wfox jika sirkuit tfox terbuka
                    tugas.mode = FoxMode.WATERFOX
                    hasil = await self._eksekusi_waterfox(tugas)
                else:
                    hasil = await self._eksekusi_thunderfox(tugas)
            else: # WATERFOX
                hasil = await self._eksekusi_waterfox(tugas)

            # Catat keberhasilan
            self.pemutus_sirkuit.catat_keberhasilan()
            if tugas.mode == FoxMode.THUNDERFOX:
                self.pemutus_sirkuit_tfox.catat_keberhasilan()

            return hasil

        except Exception as exc:
            e = exc
            # Catat kegagalan
            self.pemutus_sirkuit.catat_kegagalan()
            if tugas.mode == FoxMode.THUNDERFOX:
                self.pemutus_sirkuit_tfox.catat_kegagalan()

            self.metrik.tugas_gagal += 1
            raise
        finally:
            status_akhir = StatusTugas.SELESAI if e is None else StatusTugas.GAGAL
            self.pencatat_tugas.hapus_tugas(tugas.nama, status=status_akhir)


    def _pilih_mode(self, tugas: TugasFox) -> FoxMode:
        """Heuristik sederhana untuk pemilihan mode (Fase 1)."""
        # Heuristik dasar: tugas dengan estimasi durasi > 0.5 detik -> tfox
        if self.aktifkan_aot and tugas.estimasi_durasi and tugas.estimasi_durasi > 0.5:
            return FoxMode.THUNDERFOX
        return FoxMode.WATERFOX

    async def _eksekusi_thunderfox(self, tugas: TugasFox) -> Any:
        """Eksekusi dengan pendekatan ThunderFox (simulasi AoT)."""
        loop = asyncio.get_event_loop()

        # Simulasi sederhana AoT (akan ditingkatkan di Fase selanjutnya)
        def tugas_terbungkus_aot():
            try:
                # Simulasi keuntungan kompilasi AoT
                waktu_mulai = time.time()

                # Jalankan di event loop baru khusus untuk thread ini
                loop_tugas = asyncio.new_event_loop()
                asyncio.set_event_loop(loop_tugas)
                hasil = loop_tugas.run_until_complete(tugas.coroutine())

                # Simulasi keuntungan optimisasi dari AoT
                keuntungan_optimisasi = max(0.1, min(0.3, (time.time() - waktu_mulai) * 0.1))
                time.sleep(keuntungan_optimisasi) # Mensimulasikan waktu kompilasi AoT yang 'terbayar'

                return hasil
            finally:
                loop_tugas.close()

        # Eksekusi dengan penanganan batas waktu
        if tugas.batas_waktu:
            return await asyncio.wait_for(
                loop.run_in_executor(self.eksekutor_tfox, tugas_terbungkus_aot),
                timeout=tugas.batas_waktu
            )
        else:
            return await loop.run_in_executor(self.eksekutor_tfox, tugas_terbungkus_aot)

    async def _eksekusi_waterfox(self, tugas: TugasFox) -> Any:
        """Eksekusi dengan pendekatan WaterFox (JIT)."""
        async with self.semafor_wfox:
            if tugas.batas_waktu:
                return await asyncio.wait_for(tugas.coroutine(), timeout=tugas.batas_waktu)
            else:
                return await tugas.coroutine()

    async def shutdown(self, timeout: float = 10.0):
        """Melakukan shutdown manajer secara anggun."""
        self._sedang_shutdown = True

        print("🦊 ManajerFox memulai proses shutdown...")

        # Tunggu tugas yang aktif untuk selesai
        waktu_mulai = time.time()
        while self.pencatat_tugas.dapatkan_jumlah_aktif() > 0:
            if time.time() - waktu_mulai > timeout:
                print("⚠️  Batas waktu terlampaui saat menunggu tugas selesai.")
                break
            await asyncio.sleep(0.1)

        # Matikan eksekutor
        self.eksekutor_tfox.shutdown(wait=True)

        print("✅ ManajerFox berhasil dimatikan.")

    def dapatkan_metrik(self) -> MetrikFox:
        """Mengambil data metrik saat ini."""
        return self.metrik
