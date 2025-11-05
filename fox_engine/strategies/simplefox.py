# fox_engine/strategies/simplefox.py
import asyncio
from typing import Any

from .base import BaseStrategy
from ..core import TugasFox

class SimpleFoxStrategy(BaseStrategy):
    """Strategi eksekusi async murni dengan overhead minimal."""

    async def execute(self, tugas: TugasFox) -> Any:
        """Eksekusi coroutine secara langsung dengan penanganan batas waktu."""
        if tugas.batas_waktu:
            return await asyncio.wait_for(tugas.coroutine(), timeout=tugas.batas_waktu)
        return await tugas.coroutine()
