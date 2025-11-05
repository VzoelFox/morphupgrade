# fox_engine/api.py
# PATCH-014D: Perbarui API untuk mendukung arsitektur io_handler.
# PATCH-014E: Tambahkan helper I/O untuk tulis, salin, dan hapus.
# TODO: Tambahkan validasi tipe argumen di helper I/O.
import os
import shutil
from .core import FoxMode, TugasFox
from .manager import ManajerFox
from typing import Callable, Optional, Any

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

async def tfox(nama: str, coro: Callable, prioritas: int = 1,
               batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode ThunderFox (AoT).
    Cocok untuk tugas-tugas yang berat secara komputasi.
    """
    tugas = TugasFox(
        nama=nama,
        coroutine=coro,
        mode=FoxMode.THUNDERFOX,
        prioritas=prioritas,
        batas_waktu=batas_waktu,
        estimasi_durasi=estimasi_durasi
    )
    return await dapatkan_manajer_fox().kirim(tugas)

async def wfox(nama: str, coro: Callable, prioritas: int = 1,
               batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode WaterFox (JIT).
    Cocok untuk operasi I/O atau tugas-tugas cepat.
    """
    tugas = TugasFox(
        nama=nama,
        coroutine=coro,
        mode=FoxMode.WATERFOX,
        prioritas=prioritas,
        batas_waktu=batas_waktu,
        estimasi_durasi=estimasi_durasi
    )
    return await dapatkan_manajer_fox().kirim(tugas)

async def sfox(nama: str, coro: Callable, prioritas: int = 1,
               batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode SimpleFox (async murni).
    Cocok untuk tugas-tugas yang sangat ringan dan latensi rendah.
    """
    tugas = TugasFox(
        nama=nama,
        coroutine=coro,
        mode=FoxMode.SIMPLEFOX,
        prioritas=prioritas,
        batas_waktu=batas_waktu,
        estimasi_durasi=estimasi_durasi
    )
    return await dapatkan_manajer_fox().kirim(tugas)

from .core import IOType

async def mfox(nama: str, coro: Callable, prioritas: int = 1,
               batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None,
               jenis_operasi: Optional[IOType] = None,
               io_handler: Optional[Callable] = None) -> Any:
    """
    Mengirimkan tugas untuk dieksekusi dalam mode MiniFox (spesialis I/O).
    Cocok untuk operasi file atau jaringan.
    """
    tugas = TugasFox(
        nama=nama,
        coroutine=coro,
        mode=FoxMode.MINIFOX,
        prioritas=prioritas,
        batas_waktu=batas_waktu,
        estimasi_durasi=estimasi_durasi,
        jenis_operasi=jenis_operasi,
        io_handler=io_handler
    )
    return await dapatkan_manajer_fox().kirim(tugas)


async def mfox_baca_file(nama: str, path: str, **kwargs) -> str:
    """
    Membaca konten file secara asinkron menggunakan MiniFox.

    Operasi I/O file yang bersifat blocking dijalankan di thread pool terpisah
    untuk mencegah pemblokan event loop utama.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path lengkap ke file yang akan dibaca.
        **kwargs: Argumen tambahan untuk `mfox` (misalnya, `batas_waktu`).

    Returns:
        str: Konten file sebagai string.

    Raises:
        FileNotFoundError: Jika file di `path` tidak ditemukan.
        asyncio.TimeoutError: Jika operasi melebihi `batas_waktu`.
    """
    def _io_handler_baca():
        """Handler I/O yang membaca file dan mengembalikan konten serta ukurannya."""
        with open(path, 'r', encoding='utf-8') as f:
            konten = f.read()
            # Mengembalikan hasil dan jumlah byte yang diproses
            return konten, len(konten.encode('utf-8'))

    async def _placeholder():
        pass

    return await mfox(
        nama=nama,
        coro=_placeholder,
        jenis_operasi=IOType.FILE,
        io_handler=_io_handler_baca,
        **kwargs
    )

async def mfox_tulis_file(nama: str, path: str, konten: str, **kwargs) -> int:
    """
    Menulis konten ke file secara asinkron menggunakan MiniFox.

    Args:
        nama (str): Nama unik untuk tugas.
        path (str): Path lengkap ke file yang akan ditulis.
        konten (str): Konten string yang akan ditulis ke file.
        **kwargs: Argumen tambahan untuk `mfox`.

    Returns:
        int: Jumlah byte yang berhasil ditulis.
    """
    def _io_handler_tulis():
        """Handler I/O yang menulis ke file dan mengembalikan jumlah byte."""
        byte_konten = konten.encode('utf-8')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(konten)
        jumlah_byte = len(byte_konten)
        return jumlah_byte, jumlah_byte

    async def _placeholder():
        pass

    return await mfox(
        nama=nama,
        coro=_placeholder,
        jenis_operasi=IOType.FILE,
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
        nama=nama,
        coro=_placeholder,
        jenis_operasi=IOType.FILE,
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
        nama=nama,
        coro=_placeholder,
        jenis_operasi=IOType.FILE,
        io_handler=_io_handler_hapus,
        **kwargs
    )


async def fox(nama: str, coro: Callable, prioritas: int = 1,
              batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None) -> Any:
    """
    Mengirimkan tugas dengan pemilihan mode otomatis oleh ManajerFox.
    Manajer akan memilih strategi terbaik berdasarkan heuristik.
    """
    tugas = TugasFox(
        nama=nama,
        coroutine=coro,
        mode=FoxMode.AUTO,
        prioritas=prioritas,
        batas_waktu=batas_waktu,
        estimasi_durasi=estimasi_durasi
    )
    return await dapatkan_manajer_fox().kirim(tugas)
