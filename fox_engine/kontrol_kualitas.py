# fox_engine/kontrol_kualitas.py
# PATCH-020A: Inisialisasi kerangka dasar untuk komponen KontrolKualitasFox.
# PATCH-020B: Implementasikan logika validasi dasar untuk tugas I/O.
"""
Modul ini akan menjadi pusat validasi tugas pra-eksekusi dan
logika pemilihan strategi yang cerdas untuk ManajerFox.
"""
import asyncio
import logging
from .core import TugasFox, IOType, FoxMode

logger = logging.getLogger(__name__)

class KontrolKualitasFox:
    """
    Bertindak sebagai lapisan validasi dan optimisasi sebelum tugas dieksekusi.
    """

    def __init__(self):
        """Inisialisasi KontrolKualitasFox."""
        pass

    def validasi_tugas(self, tugas: TugasFox):
        """
        Memvalidasi konfigurasi tugas sebelum eksekusi.
        Memunculkan ValueError jika ditemukan konfigurasi yang tidak valid.
        """
        if tugas.jenis_operasi == IOType.FILE:
            if not tugas.io_handler or not callable(tugas.io_handler):
                raise ValueError(
                    f"Tugas I/O File '{tugas.nama}' harus memiliki 'io_handler' yang valid dan callable."
                )

        if tugas.jenis_operasi == IOType.NETWORK:
            if not asyncio.iscoroutinefunction(tugas.coroutine):
                raise ValueError(
                    f"Tugas Jaringan '{tugas.nama}' harus memiliki 'coroutine' yang merupakan fungsi async."
                )

    def pilih_strategi_optimal(
        self,
        tugas: TugasFox,
        aktifkan_aot: bool,
        jumlah_tugas_aktif: int,
        ambang_batas_beban: int,
    ) -> FoxMode:
        """Heuristik cerdas untuk pemilihan mode otomatis berbasis beban kerja."""
        # Aturan 1: Jika tidak ada estimasi durasi -> SimpleFox (pilihan aman default)
        if tugas.estimasi_durasi is None:
            return FoxMode.SIMPLEFOX

        # Aturan 2: Tugas yang sangat singkat (< 0.1 detik) -> SimpleFox
        if tugas.estimasi_durasi < 0.1:
            return FoxMode.SIMPLEFOX

        # Aturan 3: Tugas berat I/O (deteksi sederhana) -> MiniFox
        if self._is_io_heavy_task(tugas):
            return FoxMode.MINIFOX

        # Aturan 4: Tugas berat CPU (> 0.5 detik)
        if aktifkan_aot and tugas.estimasi_durasi > 0.5:
            # Aturan Cerdas: Turunkan ke WaterFox jika sistem sedang sibuk
            if jumlah_tugas_aktif >= ambang_batas_beban:
                logger.warning(
                    f"Beban kerja tinggi ({jumlah_tugas_aktif} tugas aktif), "
                    f"menurunkan tugas '{tugas.nama}' dari THUNDERFOX ke WATERFOX."
                )
                return FoxMode.WATERFOX
            return FoxMode.THUNDERFOX

        # Default: WaterFox untuk beban kerja seimbang
        return FoxMode.WATERFOX

    def _is_io_heavy_task(self, tugas: TugasFox) -> bool:
        """Deteksi sederhana untuk tugas berat I/O."""
        io_keywords = ['file', 'read', 'write', 'network', 'download', 'upload', 'io', 'socket']
        task_name_lower = tugas.nama.lower()
        return any(keyword in task_name_lower for keyword in io_keywords)
