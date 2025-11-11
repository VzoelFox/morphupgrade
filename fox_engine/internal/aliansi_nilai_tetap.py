# fox_engine/internal/aliansi_nilai_tetap.py
from enum import Enum, auto

class AliansiNilaiTetap(Enum):
    """
    Kelas dasar untuk enumerasi, menyediakan fungsionalitas dasar
    yang dibutuhkan oleh FoxMode dan kelas sejenisnya.
    """
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.value
