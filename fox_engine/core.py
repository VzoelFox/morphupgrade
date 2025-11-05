# fox_engine/core.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Callable, Optional, Any, Dict
import time

class FoxMode(Enum):
    """Menentukan mode eksekusi untuk sebuah tugas."""
    THUNDERFOX = "tfox"    # AOT - komputasi berat
    WATERFOX = "wfox"      # JIT - tugas adaptif
    SIMPLEFOX = "sfox"     # Pure async - tugas ringan
    MINIFOX = "mfox"       # Spesialis I/O - operasi file/network
    AUTO = "auto"          # Pemilihan cerdas oleh manajer

# PATCH-013A: Tambahkan IOType dan `jenis_operasi` untuk MiniFox
# TODO: Gunakan ini di MiniFoxStrategy untuk routing tugas I/O
class IOType(Enum):
    """Mendefinisikan tipe spesifik dari operasi I/O."""
    FILE = "file"
    NETWORK = "network"
    STREAM = "stream"


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
    jenis_operasi: Optional[IOType] = None  # Spesifik untuk MiniFox
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
    tugas_sfox_selesai: int = 0
    tugas_mfox_selesai: int = 0
    kompilasi_aot: int = 0
    kompilasi_jit: int = 0
    tugas_gagal: int = 0
    avg_durasi_tfox: float = 0.0
    avg_durasi_wfox: float = 0.0
    avg_durasi_sfox: float = 0.0
    avg_durasi_mfox: float = 0.0
