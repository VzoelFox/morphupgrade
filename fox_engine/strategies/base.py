# fox_engine/strategies/base.py
from typing import Any
from ..core import TugasFox
from ..internal.pecahan_kelas_abstrak import PecahanKelasAbstrak, metode_abstrak

class BaseStrategy(PecahanKelasAbstrak):
    """Kelas dasar abstrak untuk semua strategi eksekusi"""

    @metode_abstrak
    async def execute(self, tugas: TugasFox) -> Any:
        pass
