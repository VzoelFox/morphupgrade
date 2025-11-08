# fox_engine/strategies/simplefox.py
import asyncio
from typing import Any

from .base import BaseStrategy
from ..core import TugasFox

class SimpleFoxStrategy(BaseStrategy):
    """Strategi eksekusi async murni dengan overhead minimal."""

    async def execute(self, tugas: TugasFox) -> Any:
        """Eksekusi coroutine secara langsung dengan penanganan batas waktu."""
        coro = tugas.coroutine_func(*tugas.coroutine_args, **tugas.coroutine_kwargs)
        if tugas.batas_waktu:
            return await asyncio.wait_for(coro, timeout=tugas.batas_waktu)
        return await coro

    async def shutdown(self):
        """SimpleFox tidak memerlukan pembersihan sumber daya."""
        # Tetap kosong, tapi harus async biar konsisten dengan kontrak
        pass
