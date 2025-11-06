# fox_engine/manager.py
# PATCH-014F: Integrasikan pelacakan metrik MiniFox di ManajerFox.
# PATCH-015B: Implementasikan mekanisme shutdown terpusat yang memanggil shutdown strategi.
# PATCH-017D: Ganti `print` dengan `logging` dan tambahkan log siklus hidup tugas.
# TODO: Buat metode terpisah untuk menangani logika kegagalan metrik.
import asyncio
import time
import logging
from typing import Dict, Optional, Any, List

from .core import FoxMode, TugasFox, MetrikFox, StatusTugas
from .internal.kunci import Kunci
from .internal.garis_tugas import GarisTugas
from .internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from .safety import PemutusSirkuit, PencatatTugas
from .strategies import BaseStrategy, SimpleFoxStrategy, MiniFoxStrategy
from .kontrol_kualitas import KontrolKualitasFox

logger = logging.getLogger(__name__)

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
        self.eksekutor_tfox = JalurUtamaMultiArah(
            maks_pekerja=maks_pekerja_tfox,
            nama_prefiks_jalur="thunderfox"
        )
        self.semafor_wfox = GarisTugas(maks_konkuren_wfox)

        # Daftar strategi untuk manajemen terpusat
        self.strategi: Dict[FoxMode, BaseStrategy] = {
            FoxMode.SIMPLEFOX: SimpleFoxStrategy(),
            FoxMode.MINIFOX: MiniFoxStrategy()
        }

        # Sistem keamanan dan kualitas
        self.pemutus_sirkuit = PemutusSirkuit()
        self.pencatat_tugas = PencatatTugas()
        self.kontrol_kualitas = KontrolKualitasFox()
        self.pemutus_sirkuit_tfox = PemutusSirkuit(ambang_kegagalan=3, batas_waktu_reset=30.0)

        # Manajemen status
        self.metrik = MetrikFox()
        self._sedang_shutdown = False
        self._kunci = Kunci()

        # Cache untuk kompilasi AoT (akan dikembangkan di Fase 2)
        self.cache_aot: Dict[str, Any] = {}

        logger.info(f"🐺 ManajerFox diinisialisasi: {maks_pekerja_tfox} pekerja tfox, {maks_konkuren_wfox} wfox konkuren")

    async def kirim(self, tugas: TugasFox) -> Any:
        """Mengirimkan tugas untuk eksekusi dengan pemeriksaan keamanan dasar."""
        logger.debug(f"Menerima tugas '{tugas.nama}' dengan mode awal {tugas.mode.name}.")

        # Fase 1: Validasi Kualitas dan Keamanan
        self.kontrol_kualitas.validasi_tugas(tugas)
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
                tugas.mode = self.kontrol_kualitas.pilih_strategi_optimal(
                    tugas=tugas,
                    aktifkan_aot=self.aktifkan_aot,
                    jumlah_tugas_aktif=self.pencatat_tugas.dapatkan_jumlah_aktif(),
                    ambang_batas_beban=self.maks_konkuren_wfox,
                )
                logger.debug(f"Mode AUTO terpilih untuk tugas '{tugas.nama}': {tugas.mode.name}.")

            # Eksekusi berdasarkan mode
            logger.info(f"Memulai eksekusi tugas '{tugas.nama}' dengan strategi {tugas.mode.name}.")
            if tugas.mode == FoxMode.THUNDERFOX:
                if not self.pemutus_sirkuit_tfox.bisa_eksekusi():
                    tugas.mode = FoxMode.WATERFOX  # Fallback
                    logger.warning(f"Pemutus sirkuit ThunderFox terbuka, fallback ke {tugas.mode.name} untuk tugas '{tugas.nama}'.")
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
            logger.info(f"Tugas '{tugas.nama}' berhasil diselesaikan dalam {durasi:.4f} detik.")
            self.pemutus_sirkuit.catat_keberhasilan()
            if tugas.mode == FoxMode.THUNDERFOX:
                self.pemutus_sirkuit_tfox.catat_keberhasilan()

            self._catat_dan_perbarui_metrik_keberhasilan(tugas, durasi)

            return hasil

        except Exception as exc:
            e = exc
            logger.error(f"Tugas '{tugas.nama}' gagal dengan galat: {exc}", exc_info=True)
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

        # Kirim tugas ke eksekutor kustom kita
        masa_depan = self.eksekutor_tfox.kirim(tugas_terbungkus_aot)

        # Gunakan eksekutor default asyncio untuk menunggu hasil blocking
        # dari future kustom kita tanpa memblokir event loop utama.
        coro_hasil = loop.run_in_executor(None, masa_depan.hasil)

        # Eksekusi dengan penanganan batas waktu
        if tugas.batas_waktu:
            return await asyncio.wait_for(coro_hasil, timeout=tugas.batas_waktu)
        else:
            return await coro_hasil

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

        logger.info("🦊 ManajerFox memulai proses shutdown...")

        # Tunggu tugas yang aktif untuk selesai
        waktu_mulai = time.time()
        while self.pencatat_tugas.dapatkan_jumlah_aktif() > 0:
            if time.time() - waktu_mulai > timeout:
                logger.warning(f"Batas waktu terlampaui saat menunggu {self.pencatat_tugas.dapatkan_jumlah_aktif()} tugas selesai.")
                break
            await asyncio.sleep(0.1)

        # Matikan eksekutor dan strategi
        self.eksekutor_tfox.matikan(tunggu=True)
        for mode, strategi in self.strategi.items():
            try:
                await strategi.shutdown()
                logger.info(f"Strategi {mode.name} berhasil dimatikan.")
            except Exception as e:
                logger.error(f"Kesalahan saat mematikan strategi {mode.name}: {e}", exc_info=True)

        logger.info("✅ ManajerFox berhasil dimatikan.")

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
