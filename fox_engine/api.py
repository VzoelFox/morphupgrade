# fox_engine/api.py
# PATCH-014D: Perbarui API untuk mendukung arsitektur io_handler.
# PATCH-014E: Tambahkan helper I/O untuk tulis, salin, dan hapus.
# PATCH-016D: Integrasikan operasi file yang dioptimalkan ke dalam API.
# PATCH-018C: Refactor API jaringan untuk menggunakan coroutine alih-alih io_handler.
# PATCH-019B: (Perbaikan) Implementasikan backpressure yang efektif untuk streaming file.
# TODO: Tambahkan validasi tipe argumen di helper I/O.
import os
import shutil
import asyncio
from .core import FoxMode, TugasFox, IOType
from .manager import ManajerFox
from typing import Callable, Optional, Any, Tuple
from .internal.operasi_file import (
    baca_file_dengan_buffer,
    tulis_file_dengan_buffer,
    stream_file_per_baris
)

# Instance manajer global dengan inisialisasi malas (lazy initialization)
_manajer_fox: Optional[ManajerFox] = None

def dapatkan_manajer_fox() -> ManajerFox:
    """
    Mengambil atau membuat instance ManajerFox global.
    Pola ini memastikan hanya ada satu manajer yang aktif.
    """
    global _manajer_fox
    if _manajer_fox is None:
        _manajer_fox = ManajerFox()
    return _manajer_fox

def dapatkan_manajer_fox_tanpa_inisialisasi() -> Optional[ManajerFox]:
    """
    Mengambil instance ManajerFox global hanya jika sudah ada,
    tanpa memicu inisialisasi. Berguna untuk teardown pengujian.
    """
    global _manajer_fox
    return _manajer_fox

async def tfox(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode ThunderFox (AoT).
    Cocok untuk tugas-tugas yang berat secara komputasi.
    """
    # Ekstrak argumen non-TugasFox dari kwargs
    tugas_kwargs = {
        k: kwargs.pop(k) for k in
        ['prioritas', 'batas_waktu', 'estimasi_durasi', 'jalankan_segera', 'penundaan_mulai']
        if k in kwargs
    }

    tugas = TugasFox(
        nama=nama,
        coroutine_func=coro_func,
        coroutine_args=args,
        coroutine_kwargs=kwargs,
        mode=FoxMode.THUNDERFOX,
        **tugas_kwargs
    )
    return await dapatkan_manajer_fox().kirim(tugas)

async def wfox(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode WaterFox (JIT).
    Cocok untuk operasi I/O atau tugas-tugas cepat.
    """
    tugas_kwargs = {
        k: kwargs.pop(k) for k in
        ['prioritas', 'batas_waktu', 'estimasi_durasi', 'jalankan_segera', 'penundaan_mulai']
        if k in kwargs
    }
    tugas = TugasFox(
        nama=nama,
        coroutine_func=coro_func,
        coroutine_args=args,
        coroutine_kwargs=kwargs,
        mode=FoxMode.WATERFOX,
        **tugas_kwargs
    )
    return await dapatkan_manajer_fox().kirim(tugas)

async def sfox(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode SimpleFox (async murni).
    Cocok untuk tugas-tugas yang sangat ringan dan latensi rendah.
    """
    tugas_kwargs = {
        k: kwargs.pop(k) for k in
        ['prioritas', 'batas_waktu', 'estimasi_durasi', 'jalankan_segera', 'penundaan_mulai']
        if k in kwargs
    }
    tugas = TugasFox(
        nama=nama,
        coroutine_func=coro_func,
        coroutine_args=args,
        coroutine_kwargs=kwargs,
        mode=FoxMode.SIMPLEFOX,
        **tugas_kwargs
    )
    return await dapatkan_manajer_fox().kirim(tugas)

async def mfox(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode MiniFox (spesialis I/O).
    Cocok untuk operasi file atau jaringan.
    """
    tugas_kwargs = {
        k: kwargs.pop(k) for k in
        ['prioritas', 'batas_waktu', 'estimasi_durasi', 'jalankan_segera', 'penundaan_mulai', 'jenis_operasi', 'io_handler']
        if k in kwargs
    }
    tugas = TugasFox(
        nama=nama,
        coroutine_func=coro_func,
        coroutine_args=args,
        coroutine_kwargs=kwargs,
        mode=FoxMode.MINIFOX,
        **tugas_kwargs
    )
    return await dapatkan_manajer_fox().kirim(tugas)


async def mfox_baca_file(nama: str, path: str, **kwargs) -> bytes:
    """
    Membaca konten file secara asinkron menggunakan MiniFox dengan buffer.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path lengkap ke file yang akan dibaca.
        **kwargs: Argumen tambahan untuk `mfox` (misalnya, `batas_waktu`).

    Returns:
        bytes: Konten file sebagai bytes.
    """
    def _io_handler_baca():
        """Handler I/O yang memanggil fungsi baca ber-buffer."""
        return baca_file_dengan_buffer(path)

    async def _placeholder():
        pass

    return await mfox(
        nama,
        _placeholder,
        jenis_operasi=IOType.FILE_BACA,
        io_handler=_io_handler_baca,
        **kwargs
    )

async def mfox_tulis_file(nama: str, path: str, konten: bytes, **kwargs) -> int:
    """
    Menulis konten ke file secara asinkron menggunakan MiniFox dengan buffer.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path lengkap ke file yang akan ditulis.
        konten (bytes): Konten bytes yang akan ditulis ke file.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        int: Jumlah byte yang berhasil ditulis.
    """
    def _io_handler_tulis():
        """Handler I/O yang memanggil fungsi tulis ber-buffer."""
        _, jumlah_byte = tulis_file_dengan_buffer(path, konten)
        # Handler harus mengembalikan (hasil, jumlah_byte)
        return jumlah_byte, jumlah_byte

    async def _placeholder():
        pass

    return await mfox(
        nama,
        _placeholder,
        jenis_operasi=IOType.FILE_TULIS,
        io_handler=_io_handler_tulis,
        **kwargs
    )

async def mfox_salin_file(nama: str, path_sumber: str, path_tujuan: str, **kwargs) -> int:
    """
    Menyalin file dari sumber ke tujuan secara asinkron menggunakan MiniFox.

    Args:
        nama (str): Nama unik untuk tugas.
        path_sumber (str): Path file sumber.
        path_tujuan (str): Path file tujuan.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        int: Ukuran file yang disalin dalam byte.
    """
    def _io_handler_salin():
        """Handler I/O untuk menyalin file."""
        shutil.copy2(path_sumber, path_tujuan)
        jumlah_byte = os.path.getsize(path_tujuan)
        return jumlah_byte, jumlah_byte

    async def _placeholder():
        pass

    return await mfox(
        nama,
        _placeholder,
        # Salin adalah operasi baca dan tulis, kita tandai sebagai BACA
        # karena metrik utamanya adalah byte yang dibaca dari sumber.
        jenis_operasi=IOType.FILE_BACA,
        io_handler=_io_handler_salin,
        **kwargs
    )

async def mfox_hapus_file(nama: str, path: str, **kwargs) -> bool:
    """
    Menghapus file secara asinkron menggunakan MiniFox.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path file yang akan dihapus.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        bool: True jika file berhasil dihapus.
    """
    def _io_handler_hapus():
        """Handler I/O untuk menghapus file."""
        os.remove(path)
        return True, 0  # Tidak ada byte yang diproses, kembalikan 0

    async def _placeholder():
        pass

    return await mfox(
        nama,
        _placeholder,
        # Hapus tidak melibatkan transfer byte, jadi tipe generik sudah cukup.
        jenis_operasi=IOType.FILE_GENERIC,
        io_handler=_io_handler_hapus,
        **kwargs
    )

async def mfox_stream_file(nama: str, path: str, **kwargs) -> Any:
    """
    Melakukan streaming baris file secara asinkron dengan backpressure EFEKTIF.

    Fungsi ini mengembalikan sebuah async generator yang dapat diiterasi.
    Backpressure memastikan thread I/O hanya membaca secepat consumer memproses.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path lengkap ke file yang akan di-stream.
        **kwargs: Argumen tambahan untuk `mfox` (misalnya, `batas_waktu`).

    Yields:
        bytes: Setiap baris dari file sebagai bytes.

    Raises:
        IOKesalahan: Jika terjadi error saat membaca file.
        FileTidakDitemukan: Jika file tidak ditemukan.
    """
    # Queue dengan ukuran terbatas untuk backpressure
    queue = asyncio.Queue(maxsize=10)
    loop = asyncio.get_running_loop()

    # Container untuk exception dari thread I/O
    exception_holder = {'exception': None}

    def _io_handler_stream():
        """
        Handler I/O dengan backpressure yang EFEKTIF.
        Thread ini akan BLOCK jika queue penuh (consumer lambat).
        """
        try:
            total_bytes = 0
            for baris, ukuran_byte in stream_file_per_baris(path):
                # ✅ FIX: Wait untuk Future agar blocking
                future = asyncio.run_coroutine_threadsafe(
                    queue.put(baris), loop
                )

                # Ini BLOCKS jika queue penuh - backpressure bekerja!
                # Timeout 30 detik untuk safety (bisa disesuaikan)
                try:
                    future.result(timeout=30)
                except Exception as e:
                    # Jika timeout atau error lain, simpan exception
                    exception_holder['exception'] = e
                    return False, total_bytes

                total_bytes += ukuran_byte

            return True, total_bytes

        except (IOError, FileNotFoundError) as e:
            # Bungkus galat I/O dalam tipe galat Fox Engine yang benar
            # untuk penanganan yang konsisten di lapisan atas.
            from .errors import IOKesalahan, FileTidakDitemukan
            if isinstance(e, FileNotFoundError):
                exception_holder['exception'] = FileTidakDitemukan(path=path)
            else:
                exception_holder['exception'] = IOKesalahan(pesan=str(e), path=path)
            return False, 0
        except Exception as e:
            # Tangkap semua galat tak terduga lainnya
            exception_holder['exception'] = e
            return False, 0

        finally:
            # Sinyal akhir stream
            try:
                asyncio.run_coroutine_threadsafe(
                    queue.put(None), loop
                ).result(timeout=5)
            except Exception:
                # Jika gagal mengirim sentinel, tidak masalah
                # Consumer akan timeout atau handle di try/except
                pass

    async def _placeholder():
        pass

    # Jalankan tugas I/O di latar belakang
    io_task = asyncio.create_task(mfox(
        nama,
        _placeholder,
        jenis_operasi=IOType.STREAM_BACA,
        io_handler=_io_handler_stream,
        **kwargs
    ))

    # Konsumsi dari queue di event loop
    try:
        while True:
            baris = await queue.get()
            if baris is None:
                break
            yield baris
    except Exception as e:
        # Cancel I/O task jika consumer error
        io_task.cancel()
        raise
    finally:
        # Pastikan tugas I/O selesai
        try:
            await io_task
        except asyncio.CancelledError:
            pass  # Expected jika kita cancel di atas

        # Propagate exception dari I/O thread jika ada
        if exception_holder['exception']:
            raise exception_holder['exception']

async def mfox_request_jaringan(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Menjalankan request jaringan non-blocking menggunakan kolam koneksi MiniFox.

    Args:
        nama (str): Nama unik untuk tugas.
        coro_func (Callable): Fungsi coroutine yang menerima objek sesi aiohttp
                              sebagai argumen pertamanya.
        *args: Argumen tambahan untuk `coro_func`.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        Any: Hasil dari coroutine.
    """
    return await mfox(
        nama,
        coro_func,
        *args,
        jenis_operasi=IOType.NETWORK_GENERIC,
        **kwargs
    )

async def mfox_kirim_data_jaringan(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Helper untuk tugas jaringan yang fokus pada pengiriman data (bytes_ditulis).

    Args:
        nama (str): Nama unik untuk tugas.
        coro_func (Callable): Fungsi coroutine yang melakukan operasi pengiriman.
        *args: Argumen tambahan untuk `coro_func`.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        Any: Hasil dari coroutine.
    """
    return await mfox(
        nama,
        coro_func,
        *args,
        jenis_operasi=IOType.NETWORK_KIRIM,
        **kwargs
    )

async def mfox_terima_data_jaringan(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Helper untuk tugas jaringan yang fokus pada penerimaan data (bytes_dibaca).

    Args:
        nama (str): Nama unik untuk tugas.
        coro_func (Callable): Fungsi coroutine yang melakukan operasi penerimaan.
        *args: Argumen tambahan untuk `coro_func`.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        Any: Hasil dari coroutine.
    """
    return await mfox(
        nama,
        coro_func,
        *args,
        jenis_operasi=IOType.NETWORK_TERIMA,
        **kwargs
    )

async def fox(nama: str, coro_func: Callable, *args, **kwargs) -> Any:
    """
    Mengirimkan tugas dengan pemilihan mode otomatis oleh ManajerFox.
    Manajer akan memilih strategi terbaik berdasarkan heuristik.
    """
    tugas_kwargs = {
        k: kwargs.pop(k) for k in
        ['prioritas', 'batas_waktu', 'estimasi_durasi', 'jalankan_segera', 'penundaan_mulai']
        if k in kwargs
    }
    tugas = TugasFox(
        nama=nama,
        coroutine_func=coro_func,
        coroutine_args=args,
        coroutine_kwargs=kwargs,
        mode=FoxMode.AUTO,
        **tugas_kwargs
    )
    return await dapatkan_manajer_fox().kirim(tugas)
