# fox_engine/batas_adaptif.py
from typing import Dict

class BatasAdaptif:
    """
    Mengelola ambang batas untuk sumber daya sistem secara dinamis.
    Logika ini menyesuaikan kapasitas worker pool berdasarkan beban sistem saat ini.
    """

    def __init__(self, maks_pekerja_tfox_awal: int = 2, maks_konkuren_wfox_awal: int = 10):
        # --- Konfigurasi Awal (Baseline) ---
        self.MAKS_PEKERJA_TFOX_AWAL = maks_pekerja_tfox_awal
        self.MAKS_KONKUREN_WFOX_AWAL = maks_konkuren_wfox_awal

        # --- Batas Bawah (Safety Floor) ---
        self.MIN_PEKERJA_TFOX = 1
        self.MIN_KONKUREN_WFOX = 5

        # --- Batas Saat Ini (Dinamis) ---
        self.maks_pekerja_tfox: int = self.MAKS_PEKERJA_TFOX_AWAL
        self.maks_konkuren_wfox: int = self.MAKS_KONKUREN_WFOX_AWAL

        # --- Ambang Batas untuk Pengambilan Keputusan ---
        self.ambang_memori_turun: float = 80.0
        self.ambang_cpu_turun: float = 85.0
        self.ambang_memori_naik: float = 50.0  # Naikkan kapasitas jika memori < 50%
        self.ambang_cpu_naik: float = 60.0    # Naikkan kapasitas jika CPU < 60%

        self.ambang_kritis_memori_persen: float = 95.0
        self.ambang_kritis_cpu_persen: float = 98.0

    def perbarui_berdasarkan_metrik(self, metrik_kesehatan: Dict[str, float]) -> bool:
        """
        Menyesuaikan batas operasional berdasarkan metrik kesehatan sistem.
        Mengembalikan True jika ada perubahan pada batas, False jika tidak.
        """
        persen_memori = metrik_kesehatan.get('persen_memori', 0)
        persen_cpu = metrik_kesehatan.get('persen_cpu', 0)

        batas_lama_tfox = self.maks_pekerja_tfox
        batas_lama_wfox = self.maks_konkuren_wfox

        # --- Logika Penurunan Kapasitas (Scale Down) ---
        if persen_memori > self.ambang_memori_turun or persen_cpu > self.ambang_cpu_turun:
            self.maks_pekerja_tfox = max(self.MIN_PEKERJA_TFOX, self.maks_pekerja_tfox - 1)
            self.maks_konkuren_wfox = max(self.MIN_KONKUREN_WFOX, self.maks_konkuren_wfox - 2)

        # --- Logika Peningkatan Kapasitas (Scale Up) ---
        elif persen_memori < self.ambang_memori_naik and persen_cpu < self.ambang_cpu_naik:
            self.maks_pekerja_tfox = min(self.MAKS_PEKERJA_TFOX_AWAL, self.maks_pekerja_tfox + 1)
            self.maks_konkuren_wfox = min(self.MAKS_KONKUREN_WFOX_AWAL, self.maks_konkuren_wfox + 2)

        return (self.maks_pekerja_tfox != batas_lama_tfox or
                self.maks_konkuren_wfox != batas_lama_wfox)
