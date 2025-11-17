# fox_engine/manager.py
# PATCH-014F: Integrasikan pelacakan metrik MiniFox di ManajerFox.
# PATCH-015B: Implementasikan mekanisme shutdown terpusat yang memanggil shutdown strategi.
# PATCH-017D: Ganti `print` dengan `logging` dan tambahkan log siklus hidup tugas.
# FASE-2.5: Refactor ThunderFox & WaterFox menjadi strategi mandiri.
# FASE-3A: Tambahkan pelacakan sumber daya (CPU, Memori) dan info OS.
# TODO: Buat metode terpisah untuk menangani logika kegagalan metrik.
import asyncio
import time
import logging
import platform
import warnings
from typing import Dict, Optional, Any, List

# Impor psutil secara kondisional untuk graceful degradation
try:
    import psutil
    PSUTIL_TERSEDIA = True
except ImportError:
    psutil = None
    PSUTIL_TERSEDIA = False

from .core import FoxMode, TugasFox, MetrikFox, StatusTugas, IOType
from .internal.kunci_async import Kunci
from .internal.garis_tugas import GarisTugas
from .internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from .safety import PemutusSirkuit, PencatatTugas
from .strategies import (
    BaseStrategy, SimpleFoxStrategy, MiniFoxStrategy, ThunderFoxStrategy, WaterFoxStrategy
)
from .kontrol_kualitas import KontrolKualitasFox
from .batas_adaptif import BatasAdaptif

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
            FoxMode.MINIFOX: MiniFoxStrategy(),
            FoxMode.THUNDERFOX: ThunderFoxStrategy(self.eksekutor_tfox),
            FoxMode.WATERFOX: WaterFoxStrategy(self.semafor_wfox),
        }

        # Sistem keamanan dan kualitas
        self.pemutus_sirkuit = PemutusSirkuit()
        self.pencatat_tugas = PencatatTugas()
        self.kontrol_kualitas = KontrolKualitasFox()
        self.batas_adaptif = BatasAdaptif(
            maks_pekerja_tfox_awal=maks_pekerja_tfox,
            maks_konkuren_wfox_awal=maks_konkuren_wfox
        )
        self.pemutus_sirkuit_tfox = PemutusSirkuit(ambang_kegagalan=3, batas_waktu_reset=30.0)

        # Manajemen status
        self.metrik = MetrikFox()
        self._sedang_shutdown = False
        self._kunci = Kunci()
        self._kunci_sekuensial = asyncio.Lock()

        # Fase 3A: Dapatkan info OS dan proses saat ini
        self.metrik.info_os = f"{platform.system()} {platform.release()} ({platform.machine()})"
        if PSUTIL_TERSEDIA:
            self._proses_saat_ini = psutil.Process()
        else:
            warnings.warn(
                "Pustaka 'psutil' tidak ditemukan. Metrik penggunaan sumber daya (CPU/Memori) akan dinonaktifkan. "
                "Instal dengan 'pip install psutil' untuk mengaktifkannya."
            )

        # Cache untuk kompilasi AoT (akan dikembangkan di Fase 2)
        self.cache_aot: Dict[str, Any] = {}

        logger.info(f"🐺 ManajerFox diinisialisasi pada {self.metrik.info_os}: {maks_pekerja_tfox} pekerja tfox, {maks_konkuren_wfox} wfox konkuren")

    async def kirim(self, tugas: TugasFox) -> Any:
        """Mengirimkan tugas untuk eksekusi dengan pemeriksaan keamanan dasar."""
        logger.debug(f"Menerima tugas '{tugas.nama}' dengan mode awal {tugas.mode.name}.")

        async with self._kunci:
            if self._sedang_shutdown:
                raise RuntimeError("ManajerFox sedang dalam proses shutdown")

        # Fase 1: Validasi Kualitas dan Keamanan
        self.kontrol_kualitas.validasi_tugas(tugas)

        if not self.pemutus_sirkuit.bisa_eksekusi():
            raise RuntimeError("Pemutus sirkuit terbuka - sistem kemungkinan kelebihan beban")

        # Logika Kontrol Kualitas: Penundaan dan Eksekusi Sekuensial
        async def _eksekutor_terbungkus():
            waktu_kirim = time.time()
            if tugas.penundaan_mulai > 0:
                await asyncio.sleep(tugas.penundaan_mulai)

            if not tugas.jalankan_segera:
                async with self._kunci_sekuensial:
                    waktu_tunggu = time.time() - waktu_kirim
                    self.metrik.waktu_tunggu_total += waktu_tunggu
                    return await self._eksekusi_internal(tugas)
            else:
                waktu_tunggu = time.time() - waktu_kirim
                self.metrik.waktu_tunggu_total += waktu_tunggu
                return await self._eksekusi_internal(tugas)

        # Buat coroutine eksekusi internal yang sudah dibungkus
        coro_eksekusi = _eksekutor_terbungkus()

        # Bungkus dalam asyncio.Task untuk pelacakan
        tugas_asyncio = asyncio.create_task(coro_eksekusi)

        # Daftarkan tugas dan tugas_asyncio-nya.
        # Logika penanganan nama duplikat sekarang ada di dalam PencatatTugas.
        self.pencatat_tugas.daftarkan_tugas(tugas, tugas_asyncio)

        try:
            return await tugas_asyncio
        finally:
            status_akhir = StatusTugas.SELESAI if tugas_asyncio.done() and not tugas_asyncio.exception() else StatusTugas.GAGAL
            self.pencatat_tugas.hapus_tugas(tugas.nama, status=status_akhir)

    async def _eksekusi_internal(self, tugas: TugasFox) -> Any:
        """Logika inti eksekusi, dibungkus sebagai coroutine terpisah."""
        e = None
        waktu_mulai = time.time()
        cpu_mulai = 0
        mem_mulai = 0

        # Fase 3A: Ukur sumber daya awal jika psutil tersedia
        if PSUTIL_TERSEDIA:
            cpu_mulai = self._proses_saat_ini.cpu_times().user
            mem_mulai = self._proses_saat_ini.memory_info().rss

        mode_eksekusi_awal = tugas.mode

        async def _coba_eksekusi(mode, nama_tahap):
            tugas.mode = mode
            logger.info(f"[{nama_tahap}] Mencoba eksekusi tugas '{tugas.nama}' dengan mode {mode.value}.")
            return await self.strategi[mode].execute(tugas)

        try:
            # Percobaan Pertama (Mode Asli)
            hasil = await _coba_eksekusi(mode_eksekusi_awal, "Proses A")
        except Exception as e_awal:
            logger.warning(f"Tugas '{tugas.nama}' gagal pada mode awal ({mode_eksekusi_awal.value}): {e_awal}. Memulai fallback ke mfox.")
            try:
                # Percobaan Kedua (Fallback ke mfox)
                hasil = await _coba_eksekusi(FoxMode.MINIFOX, "Proses A.1")
            except Exception as e_mfox:
                logger.error(f"Fallback mfox untuk tugas '{tugas.nama}' juga gagal: {e_mfox}. Memulai fallback terakhir ke sfox.")
                try:
                    # Percobaan Ketiga (Fallback terakhir ke sfox)
                    hasil = await _coba_eksekusi(FoxMode.SIMPLEFOX, "Proses A+")
                except Exception as e_sfox:
                    logger.critical(f"Semua fallback gagal untuk tugas '{tugas.nama}'. Galat akhir (sfox): {e_sfox}", exc_info=True)
                    # Catat kegagalan akhir dan re-raise
                    e = e_sfox
                    self.pemutus_sirkuit.catat_kegagalan()
                    self.metrik.tugas_gagal += 1
                    raise

        # Jika berhasil di tahap mana pun
        durasi = time.time() - waktu_mulai
        if PSUTIL_TERSEDIA:
            tugas.penggunaan_cpu = self._proses_saat_ini.cpu_times().user - cpu_mulai
            tugas.penggunaan_memori = self._proses_saat_ini.memory_info().rss - mem_mulai
        else:
            tugas.penggunaan_cpu = 0
            tugas.penggunaan_memori = 0

        logger.info(f"Tugas '{tugas.nama}' berhasil diselesaikan dalam {durasi:.4f} detik pada mode {tugas.mode.value}.")
        self.pemutus_sirkuit.catat_keberhasilan()
        self._catat_dan_perbarui_metrik_keberhasilan(tugas, durasi)

        return hasil

    async def shutdown(self, timeout: float = 10.0):
        """Melakukan shutdown manajer dan semua strateginya secara anggun."""
        async with self._kunci:
            if self._sedang_shutdown:
                return
            self._sedang_shutdown = True

        logger.info("🦊 ManajerFox memulai proses shutdown...")

        # Beri waktu tugas aktif untuk selesai secara normal
        logger.info(f"Menunggu hingga {self.pencatat_tugas.dapatkan_jumlah_aktif()} tugas aktif selesai (batas waktu: {timeout} detik)...")
        waktu_mulai = time.time()
        batas_waktu_terlampaui = False
        while self.pencatat_tugas.dapatkan_jumlah_aktif() > 0:
            if time.time() - waktu_mulai > timeout:
                logger.warning("Batas waktu shutdown terlampaui.")
                batas_waktu_terlampaui = True
                break
            await asyncio.sleep(0.1)

        # Jika batas waktu terlampaui, batalkan tugas yang tersisa secara paksa
        if batas_waktu_terlampaui:
            tugas_tersisa = self.pencatat_tugas.dapatkan_semua_tugas_asyncio_aktif()
            logger.warning(f"Membatalkan {len(tugas_tersisa)} tugas yang tersisa secara paksa...")
            for tugas_asyncio in tugas_tersisa:
                tugas_asyncio.cancel()
            # Beri sedikit waktu agar pembatalan diproses
            await asyncio.sleep(0.2)

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
        self.__perbarui_metrik_keberhasilan(tugas, durasi)


    def __perbarui_metrik_keberhasilan(self, tugas: TugasFox, durasi: float):
        """
        Memperbarui metrik keberhasilan untuk mode tertentu.
        Metode ini dijadikan privat untuk mencegah pemanggilan ganda.
        """
        mode = tugas.mode
        if mode == FoxMode.THUNDERFOX:
            self.metrik.tugas_tfox_selesai += 1
            n = self.metrik.tugas_tfox_selesai
            # Perbarui rata-rata durasi
            self.metrik.avg_durasi_tfox = (self.metrik.avg_durasi_tfox * (n - 1) + durasi) / n
            # Perbarui rata-rata CPU dan Memori jika tersedia
            if tugas.penggunaan_cpu is not None:
                self.metrik.avg_cpu_tfox = (self.metrik.avg_cpu_tfox * (n - 1) + tugas.penggunaan_cpu) / n
            if tugas.penggunaan_memori is not None:
                self.metrik.avg_mem_tfox = (self.metrik.avg_mem_tfox * (n - 1) + tugas.penggunaan_memori) / n
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

            # Perbarui metrik I/O secara eksplisit berdasarkan jenis_operasi
            if tugas.bytes_processed > 0 and tugas.jenis_operasi:
                if tugas.jenis_operasi in [IOType.FILE_BACA, IOType.STREAM_BACA, IOType.NETWORK_TERIMA]:
                    self.metrik.bytes_dibaca += tugas.bytes_processed
                elif tugas.jenis_operasi in [IOType.FILE_TULIS, IOType.STREAM_TULIS, IOType.NETWORK_KIRIM]:
                    self.metrik.bytes_ditulis += tugas.bytes_processed

    def dapatkan_metrik(self) -> MetrikFox:
        """Mengambil data metrik saat ini."""
        return self.metrik

    def cetak_laporan_metrik(self):
        """Mencetak laporan komprehensif tentang kinerja dan penggunaan sumber daya."""
        print("\n--- Laporan Metrik Fox Engine ---")
        print(f"Info OS             : {self.metrik.info_os}")

        # Metrik Kesehatan & Beban
        print("\n--- Kesehatan & Beban Sistem ---")
        jumlah_tugas_aktif = self.pencatat_tugas.dapatkan_jumlah_aktif()
        print(f"Tugas Aktif         : {jumlah_tugas_aktif}")
        total_tugas = jumlah_tugas_aktif + self.metrik.tugas_gagal + (self.metrik.tugas_sfox_selesai + self.metrik.tugas_wfox_selesai + self.metrik.tugas_tfox_selesai + self.metrik.tugas_mfox_selesai)
        avg_waktu_tunggu = (self.metrik.waktu_tunggu_total / total_tugas) * 1000 if total_tugas > 0 else 0
        print(f"Avg. Waktu Tunggu   : {avg_waktu_tunggu:.2f} ms")
        print(f"Status Pemutus      : {self.pemutus_sirkuit._status}")

        # Metrik Tugas Umum
        total_selesai = self.metrik.tugas_sfox_selesai + self.metrik.tugas_wfox_selesai + \
                        self.metrik.tugas_tfox_selesai + self.metrik.tugas_mfox_selesai
        print(f"\nTotal Tugas Selesai : {total_selesai}")
        print(f"Total Tugas Gagal   : {self.metrik.tugas_gagal}")

        # Metrik per Strategi
        print("\n--- Kinerja Strategi ---")
        if self.metrik.tugas_sfox_selesai > 0:
            print(f"SimpleFox (sfox)    : {self.metrik.tugas_sfox_selesai} tugas, avg durasi: {self.metrik.avg_durasi_sfox:.4f}s")
        if self.metrik.tugas_wfox_selesai > 0:
            print(f"WaterFox (wfox)     : {self.metrik.tugas_wfox_selesai} tugas, avg durasi: {self.metrik.avg_durasi_wfox:.4f}s")
        if self.metrik.tugas_tfox_selesai > 0:
            print(f"ThunderFox (tfox)   : {self.metrik.tugas_tfox_selesai} tugas, avg durasi: {self.metrik.avg_durasi_tfox:.4f}s, avg cpu: {self.metrik.avg_cpu_tfox:.4f}s")
        if self.metrik.tugas_mfox_selesai > 0:
            print(f"MiniFox (mfox)      : {self.metrik.tugas_mfox_selesai} tugas, avg durasi: {self.metrik.avg_durasi_mfox:.4f}s")

        # Metrik I/O
        if self.metrik.bytes_dibaca > 0 or self.metrik.bytes_ditulis > 0:
            print("\n--- Aktivitas I/O (MiniFox) ---")
            print(f"Total Bytes Dibaca  : {self.metrik.bytes_dibaca} bytes")
            print(f"Total Bytes Ditulis : {self.metrik.bytes_ditulis} bytes")

        # Metrik Penggunaan Sumber Daya
        if PSUTIL_TERSEDIA:
            print("\n--- Penggunaan Sumber Daya Saat Ini ---")
            mem_info = self._proses_saat_ini.memory_info()
            print(f"Penggunaan Memori   : {mem_info.rss / 1024 / 1024:.2f} MB (RSS)")
            # Penggunaan CPU bisa jadi lebih rumit, getloadavg() mungkin lebih baik untuk gambaran umum
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                print(f"Beban CPU Sistem    : {cpu_percent}%")
            except Exception:
                pass # cpu_percent bisa gagal di beberapa lingkungan

        print("-----------------------------------\n")
