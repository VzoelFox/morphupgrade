# fox_engine/manager.py
# PATCH-014F: Integrasikan pelacakan metrik MiniFox di ManajerFox.
# PATCH-015B: Implementasikan mekanisme shutdown terpusat yang memanggil shutdown strategi.
# TODO: Buat metode terpisah untuk menangani logika kegagalan metrik.
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Any, List

from .core import FoxMode, TugasFox, MetrikFox, StatusTugas
from .safety import PemutusSirkuit, PencatatTugas
from .strategies import BaseStrategy, SimpleFoxStrategy, MiniFoxStrategy

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

        # Daftar strategi untuk manajemen terpusat
        self.strategi: Dict[FoxMode, BaseStrategy] = {
            FoxMode.SIMPLEFOX: SimpleFoxStrategy(),
            FoxMode.MINIFOX: MiniFoxStrategy()
        }

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
        waktu_mulai = time.time()
        try:
            # Pemilihan mode
            if tugas.mode == FoxMode.AUTO:
                tugas.mode = self._pilih_mode(tugas)

            # Eksekusi berdasarkan mode
            if tugas.mode == FoxMode.THUNDERFOX:
                if not self.pemutus_sirkuit_tfox.bisa_eksekusi():
                    tugas.mode = FoxMode.WATERFOX  # Fallback
                    hasil = await self._eksekusi_waterfox(tugas)
                else:
                    hasil = await self._eksekusi_thunderfox(tugas)
            elif tugas.mode == FoxMode.WATERFOX:
                hasil = await self._eksekusi_waterfox(tugas)
            elif tugas.mode in self.strategi:
                 hasil = await self.strategi[tugas.mode].execute(tugas)
            else:
                raise ValueError(f"Mode Fox tidak dikenal atau strategi tidak terdaftar: {tugas.mode}")


            # Catat keberhasilan
            durasi = time.time() - waktu_mulai
            self.pemutus_sirkuit.catat_keberhasilan()
            if tugas.mode == FoxMode.THUNDERFOX:
                self.pemutus_sirkuit_tfox.catat_keberhasilan()

            self._catat_dan_perbarui_metrik_keberhasilan(tugas, durasi)

            return hasil

        except Exception as exc:
            e = exc
            # Catat kegagalan
            self.pemutus_sirkuit.catat_kegagalan()
            self.metrik.tugas_gagal += 1

            if tugas.mode == FoxMode.THUNDERFOX:
                self.pemutus_sirkuit_tfox.catat_kegagalan()
            elif tugas.mode == FoxMode.MINIFOX:
                self.metrik.tugas_mfox_gagal += 1

            raise
        finally:
            status_akhir = StatusTugas.SELESAI if e is None else StatusTugas.GAGAL
            self.pencatat_tugas.hapus_tugas(tugas.nama, status=status_akhir)


    def _pilih_mode(self, tugas: TugasFox) -> FoxMode:
        """Heuristik yang disempurnakan untuk pemilihan mode dengan SimpleFox & MiniFox."""
        # Aturan 1: Jika tidak ada estimasi durasi -> SimpleFox (pilihan aman default)
        if tugas.estimasi_durasi is None:
            return FoxMode.SIMPLEFOX

        # Aturan 2: Tugas yang sangat singkat (< 0.1 detik) -> SimpleFox
        if tugas.estimasi_durasi < 0.1:
            return FoxMode.SIMPLEFOX

        # Aturan 3: Tugas berat I/O (deteksi sederhana) -> MiniFox
        if self._is_io_heavy_task(tugas):
            return FoxMode.MINIFOX

        # Aturan 4: Tugas berat CPU (> 0.5 detik) -> ThunderFox
        if self.aktifkan_aot and tugas.estimasi_durasi > 0.5:
            return FoxMode.THUNDERFOX

        # Default: WaterFox untuk beban kerja seimbang
        return FoxMode.WATERFOX

    def _is_io_heavy_task(self, tugas: TugasFox) -> bool:
        """Deteksi sederhana untuk tugas berat I/O (Fase 1)."""
        # Heuristik: periksa nama tugas atau atribut coroutine
        io_keywords = ['file', 'read', 'write', 'network', 'download', 'upload', 'io', 'socket']
        task_name_lower = tugas.nama.lower()
        return any(keyword in task_name_lower for keyword in io_keywords)

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
        """Melakukan shutdown manajer dan semua strateginya secara anggun."""
        if self._sedang_shutdown:
            return
        self._sedang_shutdown = True

        print("🦊 ManajerFox memulai proses shutdown...")

        # Tunggu tugas yang aktif untuk selesai
        waktu_mulai = time.time()
        while self.pencatat_tugas.dapatkan_jumlah_aktif() > 0:
            if time.time() - waktu_mulai > timeout:
                print(f"⚠️  Batas waktu terlampaui saat menunggu {self.pencatat_tugas.dapatkan_jumlah_aktif()} tugas selesai.")
                break
            await asyncio.sleep(0.1)

        # Matikan eksekutor dan strategi
        self.eksekutor_tfox.shutdown(wait=True)
        for mode, strategi in self.strategi.items():
            try:
                strategi.shutdown()
                print(f"✅ Strategi {mode.name} berhasil dimatikan.")
            except Exception as e:
                print(f"⚠️ Kesalahan saat mematikan strategi {mode.name}: {e}")


        print("✅ ManajerFox berhasil dimatikan.")

    def _catat_dan_perbarui_metrik_keberhasilan(self, tugas: TugasFox, durasi: float):
        """
        FIX-BLOCKER-4: Helper terpusat untuk memastikan metrik keberhasilan
        dicatat dan diperbarui tepat sekali per tugas.
        """
        self._perbarui_metrik_keberhasilan(tugas, durasi)


    def _perbarui_metrik_keberhasilan(self, tugas: TugasFox, durasi: float):
        """Memperbarui metrik keberhasilan untuk mode tertentu."""
        mode = tugas.mode
        if mode == FoxMode.THUNDERFOX:
            self.metrik.tugas_tfox_selesai += 1
            lama = self.metrik.avg_durasi_tfox
            n = self.metrik.tugas_tfox_selesai
            self.metrik.avg_durasi_tfox = (lama * (n - 1) + durasi) / n
        elif mode == FoxMode.WATERFOX:
            self.metrik.tugas_wfox_selesai += 1
            lama = self.metrik.avg_durasi_wfox
            n = self.metrik.tugas_wfox_selesai
            self.metrik.avg_durasi_wfox = (lama * (n - 1) + durasi) / n
        elif mode == FoxMode.SIMPLEFOX:
            self.metrik.tugas_sfox_selesai += 1
            lama = self.metrik.avg_durasi_sfox
            n = self.metrik.tugas_sfox_selesai
            self.metrik.avg_durasi_sfox = (lama * (n - 1) + durasi) / n
        elif mode == FoxMode.MINIFOX:
            self.metrik.tugas_mfox_selesai += 1
            lama = self.metrik.avg_durasi_mfox
            n = self.metrik.tugas_mfox_selesai
            self.metrik.avg_durasi_mfox = (lama * (n - 1) + durasi) / n

            # Perbarui metrik I/O
            if tugas.bytes_processed > 0:
                nama_tugas_lower = tugas.nama.lower()
                if 'baca' in nama_tugas_lower or 'salin' in nama_tugas_lower:
                    self.metrik.bytes_dibaca += tugas.bytes_processed
                elif 'tulis' in nama_tugas_lower:
                    self.metrik.bytes_ditulis += tugas.bytes_processed

    def dapatkan_metrik(self) -> MetrikFox:
        """Mengambil data metrik saat ini."""
        return self.metrik
