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

# PATCH-013C: Perbarui API untuk MiniFox (Perbaikan)
# TODO: Sederhanakan pola 'blocking_func' jika API TugasFox dapat diubah.
from .core import IOType

async def mfox(nama: str, coro: Callable, prioritas: int = 1,
               batas_waktu: Optional[float] = None, estimasi_durasi: Optional[float] = None,
               jenis_operasi: Optional[IOType] = None) -> Any:
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
        jenis_operasi=jenis_operasi
    )
    return await dapatkan_manajer_fox().kirim(tugas)


async def mfox_baca_file(nama: str, path: str, **kwargs) -> str:
    """
    Fungsi helper untuk membaca file menggunakan MiniFox.
    Ini membungkus operasi I/O file yang blocking agar dapat dijalankan
    secara aman di thread pool I/O khusus milik MiniFox.
    """
    # 1. Definisikan operasi blocking dalam fungsi sinkron biasa.
    def _blocking_read_sync():
        with open(path, mode='r', encoding='utf-8') as f:
            return f.read()

    # 2. Buat coroutine placeholder. Isinya tidak penting.
    async def _coro_placeholder():
        pass

    # 3. Lampirkan fungsi blocking ke coroutine.
    #    Ini adalah workaround agar MiniFoxStrategy dapat mengakses
    #    fungsi blocking tanpa mengubah struktur TugasFox.
    setattr(_coro_placeholder, 'blocking_func', _blocking_read_sync)

    return await mfox(
        nama=nama,
        coro=_coro_placeholder,
        jenis_operasi=IOType.FILE,
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
