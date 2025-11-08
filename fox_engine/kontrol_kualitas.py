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
        # Validasi batas waktu
        if tugas.batas_waktu is not None and tugas.batas_waktu < 0:
            raise ValueError(
                f"Tugas '{tugas.nama}' memiliki 'batas_waktu' negatif: {tugas.batas_waktu}. "
                "Batas waktu harus bernilai positif."
            )

        # Validasi prioritas
        if not 1 <= tugas.prioritas <= 10:
            raise ValueError(
                f"Tugas '{tugas.nama}' memiliki 'prioritas' di luar rentang (1-10): {tugas.prioritas}."
            )

        # Validasi estimasi durasi
        if tugas.estimasi_durasi is not None and tugas.estimasi_durasi < 0:
            raise ValueError(
                f"Tugas '{tugas.nama}' memiliki 'estimasi_durasi' negatif: {tugas.estimasi_durasi}. "
                "Estimasi durasi harus bernilai positif."
            )

        # Validasi spesifik untuk jenis I/O
        # Semua jenis I/O file harus memiliki io_handler
        if tugas.jenis_operasi in [IOType.FILE_BACA, IOType.FILE_TULIS, IOType.FILE_GENERIC]:
            if not tugas.io_handler or not callable(tugas.io_handler):
                raise ValueError(
                    f"Tugas I/O File '{tugas.nama}' harus memiliki 'io_handler' yang valid dan callable."
                )

        # Semua jenis I/O jaringan harus memiliki coroutine
        if tugas.jenis_operasi in [IOType.NETWORK_KIRIM, IOType.NETWORK_TERIMA, IOType.NETWORK_GENERIC]:
            if not asyncio.iscoroutinefunction(tugas.coroutine_func):
                raise ValueError(
                    f"Tugas Jaringan '{tugas.nama}' harus memiliki 'coroutine_func' yang merupakan fungsi async."
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

        # Aturan 3: Tugas berat I/O (deteksi eksplisit) -> MiniFox
        is_io_task_by_type = tugas.jenis_operasi in [
            IOType.FILE_BACA, IOType.FILE_TULIS, IOType.FILE_GENERIC,
            IOType.NETWORK_KIRIM, IOType.NETWORK_TERIMA, IOType.NETWORK_GENERIC,
            IOType.STREAM_BACA, IOType.STREAM_TULIS, IOType.STREAM_GENERIC
        ]
        is_io_task_by_handler = tugas.io_handler is not None

        if is_io_task_by_type or is_io_task_by_handler:
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
