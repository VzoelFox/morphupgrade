# fox_engine/api.py
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

def dapatkan_kesehatan_sistem() -> dict:
    """
    Mengembalikan snapshot kesehatan sistem saat ini dari monitor.
    Berguna untuk debugging atau pemantauan eksternal.
    """
    return dapatkan_manajer_fox().monitor.cek_kesehatan_sistem()

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

async def fox(nama: str, coro: Callable, prioritas: int = 1,
              batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None) -> Any:
    """
    Mengirimkan tugas dengan pemilihan mode otomatis oleh ManajerFox.
    Manajer akan memilih antara ThunderFox dan WaterFox berdasarkan heuristik.
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
