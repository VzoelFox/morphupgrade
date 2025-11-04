# fox_engine/core.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Callable, Optional, Any, Dict
import time

class FoxMode(Enum):
    """Menentukan mode eksekusi untuk sebuah tugas."""
    THUNDERFOX = "tfox"  # Mode AoT (Ahead-of-Time) - untuk tugas berat
    WATERFOX = "wfox"    # Mode JIT (Just-in-Time) - untuk tugas ringan
    AUTO = "auto"        # ManajerFox akan memilih mode secara otomatis

class StatusTugas(Enum):
    """Mewakili status siklus hidup dari sebuah TugasFox."""
    MENUNGGU = auto()
    BERJALAN = auto()
    SELESAI = auto()
    GAGAL = auto()
    DIBATALKAN = auto()

@dataclass
class TugasFox:
    """
    Mewakili satu unit pekerjaan yang akan dieksekusi oleh ManajerFox.
    """
    nama: str
    coroutine: Callable
    mode: FoxMode
    prioritas: int = 1
    batas_waktu: Optional[float] = None  # dalam detik
    dibuat_pada: float = None
    estimasi_durasi: Optional[float] = None # dalam detik

    def __post_init__(self):
        if self.dibuat_pada is None:
            self.dibuat_pada = time.time()

@dataclass
class MetrikFox:
    """
    Menyimpan metrik operasional dari ManajerFox untuk pemantauan.
    """
    tugas_tfox_selesai: int = 0
    tugas_wfox_selesai: int = 0
    kompilasi_aot: int = 0
    kompilasi_jit: int = 0
    tugas_gagal: int = 0
    avg_durasi_tfox: float = 0.0
    avg_durasi_wfox: float = 0.0
