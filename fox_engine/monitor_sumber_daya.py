# fox_engine/monitor_sumber_daya.py
import warnings
from typing import Dict, Optional

from .batas_adaptif import BatasAdaptif

# Lakukan impor psutil secara aman (graceful degradation)
try:
    import psutil
    PSUTIL_TERSEDIA = True
except ImportError:
    psutil = None
    PSUTIL_TERSEDIA = False

class MonitorSumberDaya:
    """
    Melakukan pemantauan sumber daya sistem secara real-time.
    Jika psutil tidak tersedia, fitur pemantauan akan dinonaktifkan
    dan sistem akan beroperasi dengan batas default tanpa adaptasi.
    """

    def __init__(self, batas: BatasAdaptif):
        self.batas = batas
        if not PSUTIL_TERSEDIA:
            warnings.warn(
                "Peringatan: Pustaka 'psutil' tidak ditemukan. "
                "Fitur pemantauan sumber daya dan pembatasan adaptif dinonaktifkan."
            )

    def cek_kesehatan_sistem(self) -> Dict[str, float]:
        """
        Mengambil snapshot metrik kesehatan sistem saat ini.
        Jika psutil tidak tersedia, mengembalikan nilai nol yang aman.
        """
        if not PSUTIL_TERSEDIA or psutil is None:
            return {'persen_memori': 0.0, 'persen_cpu': 0.0}

        return {
            'persen_memori': psutil.virtual_memory().percent,
            'persen_cpu': psutil.cpu_percent(interval=0.1),
        }

    def sistem_kelebihan_beban(self, kesehatan: Optional[Dict[str, float]] = None) -> bool:
        """
        Menentukan apakah sistem sedang mengalami tekanan sumber daya (beban tinggi).
        Ini adalah sinyal untuk melakukan fallback dari tfox ke wfox.
        """
        if not PSUTIL_TERSEDIA:
            return False  # Jangan pernah throttle jika tidak bisa memantau

        kesehatan_cek = kesehatan or self.cek_kesehatan_sistem()
        return (kesehatan_cek.get('persen_memori', 0) > self.batas.ambang_memori_turun or
                kesehatan_cek.get('persen_cpu', 0) > self.batas.ambang_cpu_turun)

    def sistem_kritis(self, kesehatan: Optional[Dict[str, float]] = None) -> bool:
        """
        Menentukan apakah sistem berada dalam kondisi kritis.
        Ini adalah sinyal untuk menolak tugas baru sama sekali.
        """
        if not PSUTIL_TERSEDIA:
            return False  # Jangan pernah throttle jika tidak bisa memantau

        kesehatan_cek = kesehatan or self.cek_kesehatan_sistem()
        return (kesehatan_cek.get('persen_memori', 0) > self.batas.ambang_kritis_memori_persen or
                kesehatan_cek.get('persen_cpu', 0) > self.batas.ambang_kritis_cpu_persen)
