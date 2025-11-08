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
import aiohttp
from ..errors import IOKesalahan, JaringanKesalahan
import threading
from ..internal.jalur_utama_multi_arah import JalurUtamaMultiArah
from ..internal.kolam_koneksi import KolamKoneksiAIOHTTP
# Kunci async tidak lagi diperlukan untuk inisialisasi executor
# from ..internal.kunci_async import Kunci
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
        # Gunakan threading.Lock untuk inisialisasi yang aman antar-thread
        self._init_lock = threading.Lock()

    def _initialize_executor_sync(self):
        """
        Inisialisasi JalurUtamaMultiArah yang thread-safe.
        Metode ini sinkron dan menggunakan threading.Lock.
        """
        # Pola double-checked locking untuk performa
        if not self._initialized:
            with self._init_lock:
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
            except Exception:
                # Galat akan ditangkap dan dicatat oleh ManajerFox.
                # Cukup teruskan (re-raise) galatnya.
                raise

        try:
            masa_depan = self.io_executor.kirim(io_wrapper)
            # Menunggu hasil di dalam executor, di mana pengecualian akan dimunculkan
            return await loop.run_in_executor(None, masa_depan.hasil)
        except FileNotFoundError as e:
            raise FileTidakDitemukan(path=tugas.nama) from e
        except IOError as e:
            raise IOKesalahan(pesan=str(e), path=tugas.nama) from e

    async def _handle_file_io(self, tugas: TugasFox) -> Any:
        """Menangani tugas I/O file yang blocking."""
        # Panggil inisialisasi yang thread-safe
        self._initialize_executor_sync()
        logger.debug(f"Mengarahkan tugas I/O File '{tugas.nama}' ke executor.")
        if tugas.io_handler and callable(tugas.io_handler):
            return await self._jalankan_io_di_executor(tugas)

        # Jika io_handler tidak valid, ini adalah kesalahan konfigurasi tugas.
        # Seharusnya gagal dengan cepat alih-alih melakukan fallback diam-diam.
        raise IOKesalahan(
            pesan=f"io_handler tidak ditemukan atau tidak valid untuk tugas file '{tugas.nama}'",
            path=tugas.nama  # Path tidak tersedia, gunakan nama tugas
        )

    async def _handle_network_io(self, tugas: TugasFox) -> Any:
        """Menangani tugas I/O jaringan secara non-blocking menggunakan kolam koneksi."""
        logger.debug(f"Mengarahkan tugas I/O Jaringan '{tugas.nama}' ke kolam koneksi.")

        # Berbeda dengan file I/O, jaringan I/O di sini bersifat native async.
        # Kita tidak menggunakan io_handler, melainkan coroutine utama dari tugas.
        if not asyncio.iscoroutinefunction(tugas.coroutine_func):
            raise TypeError(f"Tugas jaringan '{tugas.nama}' harus memiliki fungsi coroutine.")

        sesi = None
        try:
            sesi = await self.kolam_koneksi.dapatkan_sesi()

            # Jalankan coroutine tugas, dengan melewatkan sesi sebagai argumen pertama.
            # Pengguna bertanggung jawab untuk menggunakan sesi ini.
            coro = tugas.coroutine_func(sesi, *tugas.coroutine_args, **tugas.coroutine_kwargs)

            if tugas.batas_waktu:
                hasil = await asyncio.wait_for(coro, timeout=tugas.batas_waktu)
            else:
                hasil = await coro

            return hasil
        except asyncio.TimeoutError:
            raise JaringanKesalahan(f"Tugas jaringan '{tugas.nama}' melampaui batas waktu", alamat=tugas.nama)
        except Exception as e:
            # Bungkus ulang galat sebagai JaringanKesalahan untuk penanganan yang konsisten.
            raise JaringanKesalahan(f"Terjadi galat jaringan saat menjalankan '{tugas.nama}': {e}", alamat=tugas.nama) from e
        finally:
            # Pastikan sesi selalu dikembalikan ke kolam, bahkan jika terjadi galat.
            if sesi:
                await self.kolam_koneksi.kembalikan_sesi(sesi)

    async def execute(self, tugas: TugasFox) -> Any:
        """
        Mengeksekusi tugas berdasarkan jenis operasinya.
        """
        # Periksa apakah jenis operasi terkait file
        if tugas.jenis_operasi in [
            IOType.FILE_BACA, IOType.FILE_TULIS, IOType.FILE_GENERIC,
            IOType.STREAM_BACA, IOType.STREAM_TULIS, IOType.STREAM_GENERIC
        ]:
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
