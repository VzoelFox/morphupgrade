# fox_engine/strategies/minifox.py
# PATCH-014C: Perbarui MiniFoxStrategy untuk menggunakan io_handler eksplisit.
# PATCH-015A: Perluas dukungan I/O untuk File & Network, refaktor logika eksekusi.
# PATCH-015C: Tambahkan logging detail untuk inisialisasi, eksekusi, dan shutdown.
# PATCH-016A: Refactor metode execute untuk meningkatkan ekstensibilitas.
# PATCH-018B: Integrasikan KolamKoneksiAIOHTTP untuk manajemen sesi jaringan.
# TODO: Implementasikan mekanisme shutdown terpusat dari ManajerFox. (SELESAI)
import os
import asyncio
import warnings
import logging
from typing import Any, Optional

from .base import BaseStrategy
from ..core import TugasFox, IOType
from ..internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from ..internal.kolam_koneksi import KolamKoneksiAIOHTTP
from .simplefox import SimpleFoxStrategy

logger = logging.getLogger(__name__)

class MiniFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi yang dioptimalkan untuk operasi I/O-bound.
    Menggunakan ThreadPoolExecutor untuk I/O file yang blocking dan kolam koneksi
    untuk I/O jaringan yang non-blocking.
    """

    def __init__(self, max_io_workers: Optional[int] = None):
        """
        Inisialisasi strategi MiniFox.
        """
        self.max_io_workers = max_io_workers or int(os.getenv('FOX_IO_WORKERS', 4))
        self.io_executor: Optional[JalurUtamaMultiArah] = None
        self.kolam_koneksi = KolamKoneksiAIOHTTP()
        self._initialized = False

    async def _initialize_executor(self):
        """Inisialisasi JalurUtamaMultiArah saat pertama kali dibutuhkan."""
        if not self._initialized:
            logger.info(f"Menginisialisasi JalurUtamaMultiArah MiniFox dengan {self.max_io_workers} pekerja.")
            self.io_executor = JalurUtamaMultiArah(
                maks_pekerja=self.max_io_workers,
                nama_prefiks_jalur="minifox_io"
            )
            self._initialized = True

    async def _jalankan_io_di_executor(self, tugas: TugasFox) -> Any:
        """Helper untuk menjalankan io_handler file di ThreadPoolExecutor."""
        logger.debug(f"Menjalankan tugas I/O File '{tugas.nama}' di executor MiniFox.")
        loop = asyncio.get_running_loop()

        def io_wrapper():
            """Wrapper untuk menangkap hasil dan jumlah byte."""
            try:
                hasil, jumlah_byte = tugas.io_handler()
                tugas.bytes_processed = jumlah_byte
                return hasil
            except Exception as e:
                logger.error(f"Terjadi kesalahan di dalam io_handler untuk tugas '{tugas.nama}': {e}", exc_info=True)
                raise

        masa_depan = self.io_executor.kirim(io_wrapper)
        coro_hasil = loop.run_in_executor(None, masa_depan.hasil)

        if tugas.batas_waktu:
            return await asyncio.wait_for(coro_hasil, timeout=tugas.batas_waktu)
        return await coro_hasil

    async def _handle_file_io(self, tugas: TugasFox) -> Any:
        """Menangani tugas I/O file yang blocking."""
        await self._initialize_executor()
        logger.debug(f"Mengarahkan tugas I/O File '{tugas.nama}' ke executor.")
        if tugas.io_handler and callable(tugas.io_handler):
            return await self._jalankan_io_di_executor(tugas)

        pesan_peringatan = (
            f"MiniFox: io_handler tidak ditemukan atau tidak valid "
            f"untuk tugas file '{tugas.nama}'. Kembali ke SimpleFox."
        )
        warnings.warn(pesan_peringatan)
        logger.warning(pesan_peringatan)
        return await SimpleFoxStrategy().execute(tugas)

    async def _handle_network_io(self, tugas: TugasFox) -> Any:
        """Menangani tugas I/O jaringan secara non-blocking menggunakan kolam koneksi."""
        logger.debug(f"Mengarahkan tugas I/O Jaringan '{tugas.nama}' ke kolam koneksi.")

        # Berbeda dengan file I/O, jaringan I/O di sini bersifat native async.
        # Kita tidak menggunakan io_handler, melainkan coroutine utama dari tugas.
        if not asyncio.iscoroutinefunction(tugas.coroutine):
            raise TypeError(f"Tugas jaringan '{tugas.nama}' harus memiliki coroutine, bukan fungsi biasa.")

        sesi = await self.kolam_koneksi.dapatkan_sesi()

        # Jalankan coroutine tugas, dengan melewatkan sesi sebagai argumen.
        # Pengguna bertanggung jawab untuk menggunakan sesi ini.
        if tugas.batas_waktu:
            return await asyncio.wait_for(tugas.coroutine(sesi), timeout=tugas.batas_waktu)
        return await tugas.coroutine(sesi)

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi tugas berdasarkan jenis operasinya.
        """
        # Periksa apakah jenis operasi terkait file
        if tugas.jenis_operasi in [IOType.FILE_BACA, IOType.FILE_TULIS, IOType.FILE_GENERIC, IOType.STREAM_BACA, IOType.STREAM_TULIS]:
            return await self._handle_file_io(tugas)

        # Periksa apakah jenis operasi terkait jaringan
        if tugas.jenis_operasi in [IOType.NETWORK_KIRIM, IOType.NETWORK_TERIMA, IOType.NETWORK_GENERIC]:
            return await self._handle_network_io(tugas)

        # Fallback untuk tugas non-I/O atau jenis I/O lainnya
        logger.debug(f"Tugas '{tugas.nama}' tidak memiliki jenis I/O spesifik, kembali ke SimpleFox.")
        return await SimpleFoxStrategy().execute(tugas)

    async def shutdown(self):
        """Membersihkan semua sumber daya, termasuk executor dan kolam koneksi."""
        logger.info("Memulai proses shutdown untuk MiniFoxStrategy.")
        if self.io_executor and self._initialized:
            logger.info("Mematikan JalurUtamaMultiArah MiniFox.")
            self.io_executor.matikan(tunggu=True)
            logger.info("JalurUtamaMultiArah MiniFox berhasil dimatikan.")
            self._initialized = False

        logger.info("Menutup kolam koneksi jaringan.")
        await self.kolam_koneksi.tutup()
        logger.info("Kolam koneksi jaringan berhasil ditutup.")
