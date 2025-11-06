# fox_engine/safety.py
import time
from typing import Set, Dict
from .core import TugasFox, StatusTugas
from .internal.kunci import Kunci

class PemutusSirkuit:
    """
    Mekanisme keamanan untuk mencegah eksekusi tugas ketika sistem
    terindikasi mengalami kelebihan beban atau kegagalan beruntun.
    """

    def __init__(self, ambang_kegagalan: int = 5, batas_waktu_reset: float = 60.0):
        self.ambang_kegagalan = ambang_kegagalan
        self.batas_waktu_reset = batas_waktu_reset
        self.jumlah_kegagalan = 0
        self.waktu_kegagalan_terakhir = 0
        self._kunci = Kunci()
        self._status = "TERTUTUP"  # TERTUTUP, TERBUKA, SETENGAH_TERBUKA

    def bisa_eksekusi(self) -> bool:
        """Memeriksa apakah sirkuit memperbolehkan eksekusi baru."""
        with self._kunci:
            if self._status == "TERBUKA":
                # Coba reset sirkuit setelah batas waktu terlewati
                if time.time() - self.waktu_kegagalan_terakhir > self.batas_waktu_reset:
                    self._status = "SETENGAH_TERBUKA"
                    return True
                return False
            return True

    def catat_kegagalan(self):
        """Mencatat sebuah kegagalan. Jika melebihi ambang, sirkuit akan terbuka."""
        with self._kunci:
            self.jumlah_kegagalan += 1
            self.waktu_kegagalan_terakhir = time.time()
            if self.jumlah_kegagalan >= self.ambang_kegagalan:
                self._status = "TERBUKA"

    def catat_keberhasilan(self):
        """Mencatat sebuah eksekusi yang berhasil dan mereset sirkuit."""
        with self._kunci:
            self.jumlah_kegagalan = 0
            self._status = "TERTUTUP"

import asyncio
from typing import Set, Dict, Optional

class PencatatTugas:
    """
    Mencatat semua tugas yang sedang aktif untuk mencegah duplikasi,
    memantau status, dan menghindari kebocoran memori.
    """

    def __init__(self):
        self._tugas_aktif: Dict[str, TugasFox] = {}
        self._tugas_asyncio: Dict[str, asyncio.Task] = {}
        self._status_tugas: Dict[str, StatusTugas] = {}
        self._kunci = Kunci()

    def daftarkan_tugas(self, tugas: TugasFox, tugas_asyncio: Optional[asyncio.Task] = None) -> bool:
        """Mendaftarkan tugas baru. Mengembalikan False jika nama tugas sudah ada."""
        with self._kunci:
            if tugas.nama in self._tugas_aktif:
                return False
            self._tugas_aktif[tugas.nama] = tugas
            if tugas_asyncio:
                self._tugas_asyncio[tugas.nama] = tugas_asyncio
            self._status_tugas[tugas.nama] = StatusTugas.BERJALAN
            return True

    def hapus_tugas(self, nama_tugas: str, status: StatusTugas = StatusTugas.SELESAI):
        """Menghapus tugas dari catatan setelah selesai atau gagal."""
        with self._kunci:
            if nama_tugas in self._tugas_aktif:
                del self._tugas_aktif[nama_tugas]
                self._status_tugas[nama_tugas] = status
            if nama_tugas in self._tugas_asyncio:
                del self._tugas_asyncio[nama_tugas]

    def apakah_tugas_aktif(self, nama_tugas: str) -> bool:
        """Memeriksa apakah tugas dengan nama tertentu sedang aktif."""
        with self._kunci:
            return nama_tugas in self._tugas_aktif

    def dapatkan_jumlah_aktif(self) -> int:
        """Mengembalikan jumlah tugas yang sedang aktif."""
        with self._kunci:
            return len(self._tugas_aktif)

    def dapatkan_semua_tugas_asyncio_aktif(self) -> list[asyncio.Task]:
        """Mengembalikan daftar semua objek asyncio.Task yang aktif."""
        with self._kunci:
            return list(self._tugas_asyncio.values())
