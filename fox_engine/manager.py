# fox_engine/manager.py
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any
import heapq

from .core import FoxMode, TugasFox, MetrikFox, StatusTugas
from .safety import PemutusSirkuit, PencatatTugas
from .batas_adaptif import BatasAdaptif
from .monitor_sumber_daya import MonitorSumberDaya


class ManajerFox:
    """
    Manajer inti yang mengatur siklus hidup tugas, pemilihan mode eksekusi,
    dan secara dinamis menyesuaikan kapasitas worker pool berdasarkan beban sistem.
    """

    def __init__(self,
                 maks_pekerja_tfox_awal: int = 2,
                 maks_konkuren_wfox_awal: int = 10,
                 aktifkan_aot: bool = True):

        # Konfigurasi
        self.aktifkan_aot = aktifkan_aot
        self.batas_adaptif = BatasAdaptif(maks_pekerja_tfox_awal, maks_konkuren_wfox_awal)

        # State untuk melacak ukuran pool saat ini
        self._ukuran_pool_tfox_saat_ini = self.batas_adaptif.maks_pekerja_tfox
        self._ukuran_pool_wfox_saat_ini = self.batas_adaptif.maks_konkuren_wfox

        # Lingkungan eksekusi (akan dikelola secara dinamis)
        self.eksekutor_tfox = ThreadPoolExecutor(
            max_workers=self._ukuran_pool_tfox_saat_ini,
            thread_name_prefix="thunderfox_"
        )
        self.semafor_wfox = asyncio.Semaphore(self._ukuran_pool_wfox_saat_ini)

        # Sistem keamanan & pemantauan
        self.monitor = MonitorSumberDaya(self.batas_adaptif)
        self.pemutus_sirkuit = PemutusSirkuit()
        self.pencatat_tugas = PencatatTugas()
        self.pemutus_sirkuit_tfox = PemutusSirkuit(ambang_kegagalan=3, batas_waktu_reset=30.0)

        # Manajemen status
        self.metrik = MetrikFox()
        self._sedang_shutdown = False
        self._kunci = threading.RLock()

        # Cache untuk kompilasi AoT (akan dikembangkan di Fase 2)
        self.cache_aot: Dict[str, Any] = {}

        print(f"🐺 ManajerFox diinisialisasi: {self._ukuran_pool_tfox_saat_ini} pekerja tfox, {self._ukuran_pool_wfox_saat_ini} wfox konkuren")

    def _sesuaikan_ukuran_pool(self):
        """Menyesuaikan ukuran worker pool (executor dan semaphore) secara dinamis."""
        ukuran_baru_tfox = self.batas_adaptif.maks_pekerja_tfox
        ukuran_baru_wfox = self.batas_adaptif.maks_konkuren_wfox

        with self._kunci:
            if self._ukuran_pool_tfox_saat_ini != ukuran_baru_tfox:
                print(f"🔄 Menyesuaikan pool ThunderFox: {self._ukuran_pool_tfox_saat_ini} -> {ukuran_baru_tfox}")
                executor_lama = self.eksekutor_tfox

                # Matikan executor lama di thread terpisah agar tidak memblokir
                shutdown_thread = threading.Thread(target=executor_lama.shutdown, args=(True,))
                shutdown_thread.start()

                self.eksekutor_tfox = ThreadPoolExecutor(
                    max_workers=ukuran_baru_tfox,
                    thread_name_prefix="thunderfox_"
                )
                self._ukuran_pool_tfox_saat_ini = ukuran_baru_tfox

            if self._ukuran_pool_wfox_saat_ini != ukuran_baru_wfox:
                print(f"🔄 Menyesuaikan pool WaterFox: {self._ukuran_pool_wfox_saat_ini} -> {ukuran_baru_wfox}")
                self.semafor_wfox = asyncio.Semaphore(ukuran_baru_wfox)
                self._ukuran_pool_wfox_saat_ini = ukuran_baru_wfox

    async def kirim(self, tugas: TugasFox) -> Any:
        """Mengirimkan tugas untuk eksekusi dengan pemeriksaan keamanan dasar."""

        # --- PEMERIKSAAN KESEHATAN SISTEM & PENYESUAIAN ADAPTIF (FASE 2) ---
        kesehatan = self.monitor.cek_kesehatan_sistem()
        if self.batas_adaptif.perbarui_berdasarkan_metrik(kesehatan):
            self._sesuaikan_ukuran_pool()

        if self.monitor.sistem_kritis(kesehatan):
            raise RuntimeError(f"Tugas '{tugas.nama}' ditolak: Sistem dalam kondisi kritis.")

        if self.monitor.sistem_kelebihan_beban(kesehatan):
            if tugas.mode == FoxMode.THUNDERFOX or (tugas.mode == FoxMode.AUTO and self._pilih_mode(tugas) == FoxMode.THUNDERFOX):
                print(f"⚠️  Sistem di bawah tekanan. Mengalihkan tugas '{tugas.nama}' ke mode WaterFox.")
                tugas.mode = FoxMode.WATERFOX

        # --- PEMERIKSAAN KEAMANAN (FASE 1) ---
        if self._sedang_shutdown:
            raise RuntimeError("ManajerFox sedang dalam proses shutdown")

        if not self.pemutus_sirkuit.bisa_eksekusi():
            raise RuntimeError("Pemutus sirkuit terbuka - sistem kemungkinan kelebihan beban")

        if not self.pencatat_tugas.daftarkan_tugas(tugas):
            raise ValueError(f"Tugas '{tugas.nama}' sudah berjalan")

        e = None
        try:
            # Pemilihan mode (jika masih auto)
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
