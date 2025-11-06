# fox_engine/strategies/minifox.py
# PATCH-014C: Perbarui MiniFoxStrategy untuk menggunakan io_handler eksplisit.
# PATCH-015A: Perluas dukungan I/O untuk File & Network, refaktor logika eksekusi.
# PATCH-015C: Tambahkan logging detail untuk inisialisasi, eksekusi, dan shutdown.
# PATCH-016A: Refactor metode execute untuk meningkatkan ekstensibilitas.
# TODO: Implementasikan mekanisme shutdown terpusat dari ManajerFox. (SELESAI)
import os
import asyncio
import warnings
import logging
from typing import Any, Optional

from .base import BaseStrategy
from ..core import TugasFox, IOType
from ..internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from .simplefox import SimpleFoxStrategy
from ..errors import FileTidakDitemukan, IOKesalahan

logger = logging.getLogger(__name__)

class MiniFoxStrategy(BaseStrategy):
    """
    Strategi eksekusi yang dioptimalkan untuk operasi I/O-bound.
    Menggunakan ThreadPoolExecutor khusus untuk menangani tugas I/O
    tanpa memblokir event loop utama.
    """

    def __init__(self, max_io_workers: Optional[int] = None):
        """
        Inisialisasi strategi MiniFox.
        Jumlah worker I/O dapat dikonfigurasi melalui argumen atau variabel lingkungan.
        """
        self.max_io_workers = max_io_workers or int(os.getenv('FOX_IO_WORKERS', 4))
        self.io_executor: Optional[JalurUtamaMultiArah] = None
        self._initialized = False

    async def _initialize(self):
        """Inisialisasi JalurUtamaMultiArah saat pertama kali dibutuhkan."""
        if not self._initialized:
            logger.info(f"Menginisialisasi JalurUtamaMultiArah MiniFox dengan {self.max_io_workers} pekerja.")
            self.io_executor = JalurUtamaMultiArah(
                maks_pekerja=self.max_io_workers,
                nama_prefiks_jalur="minifox_io"
            )
            self._initialized = True

    async def _jalankan_io_di_executor(self, tugas: TugasFox) -> Any:
        """Helper untuk menjalankan io_handler di ThreadPoolExecutor."""
        logger.debug(f"Menjalankan tugas I/O '{tugas.nama}' ({tugas.jenis_operasi.name}) di executor MiniFox.")
        loop = asyncio.get_running_loop()

        def io_wrapper():
            """Wrapper untuk menangkap hasil dan jumlah byte dengan penanganan galat spesifik."""
            resource_path = tugas.nama  # Asumsi nama tugas adalah path sumber daya
            try:
                hasil, jumlah_byte = tugas.io_handler()
                tugas.bytes_processed = jumlah_byte
                return hasil
            except FileNotFoundError:
                logger.error(f"File tidak ditemukan untuk tugas '{tugas.nama}': {resource_path}", exc_info=True)
                raise FileTidakDitemukan(path=resource_path)
            except PermissionError:
                logger.error(f"Izin ditolak untuk tugas '{tugas.nama}': {resource_path}", exc_info=True)
                raise IOKesalahan(pesan="Izin akses file ditolak", path=resource_path)
            except (IOError, OSError) as e:
                logger.error(f"Terjadi kesalahan I/O umum di dalam io_handler untuk tugas '{tugas.nama}': {e}", exc_info=True)
                raise IOKesalahan(pesan=f"Kesalahan I/O umum: {e}", path=resource_path)
            except Exception as e:
                logger.error(f"Terjadi kesalahan tak terduga di dalam io_handler untuk tugas '{tugas.nama}': {e}", exc_info=True)
                # Ulempar kembali kesalahan tak terduga agar tidak disembunyikan
                raise

        masa_depan = self.io_executor.kirim(io_wrapper)
        coro_hasil = loop.run_in_executor(None, masa_depan.hasil)

        if tugas.batas_waktu:
            return await asyncio.wait_for(coro_hasil, timeout=tugas.batas_waktu)
        return await coro_hasil

    async def _handle_file_io(self, tugas: TugasFox) -> Any:
        """Menangani tugas I/O file secara spesifik."""
        logger.debug(f"Mengarahkan tugas I/O File '{tugas.nama}' ke handler spesifik.")
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
        """Menangani tugas I/O jaringan secara spesifik."""
        logger.debug(f"Mengarahkan tugas I/O Jaringan '{tugas.nama}' ke handler spesifik.")
        if tugas.io_handler and callable(tugas.io_handler):
            return await self._jalankan_io_di_executor(tugas)

        pesan_peringatan = (
            f"MiniFox: io_handler tidak ditemukan atau tidak valid "
            f"untuk tugas jaringan '{tugas.nama}'. Kembali ke SimpleFox."
        )
        warnings.warn(pesan_peringatan)
        logger.warning(pesan_peringatan)
        return await SimpleFoxStrategy().execute(tugas)

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi tugas berdasarkan jenis operasinya.
        Tugas I/O akan diarahkan ke handler spesifik, sementara
        tugas lainnya akan dieksekusi oleh SimpleFox.
        """
        await self._initialize()

        if tugas.jenis_operasi == IOType.FILE:
            return await self._handle_file_io(tugas)

        if tugas.jenis_operasi == IOType.NETWORK:
            return await self._handle_network_io(tugas)

        # Fallback untuk tugas non-I/O atau jenis I/O lainnya
        return await SimpleFoxStrategy().execute(tugas)

    def shutdown(self):
        """Membersihkan sumber daya JalurUtamaMultiArah."""
        if self.io_executor and self._initialized:
            logger.info("Memulai proses shutdown untuk JalurUtamaMultiArah MiniFox.")
            self.io_executor.matikan(tunggu=True)
            logger.info("JalurUtamaMultiArah MiniFox berhasil dimatikan.")
            self._initialized = False
