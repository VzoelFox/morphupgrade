# fox_engine/strategies/base.py
from abc import ABC, abstractmethod
from typing import Any
from ..core import TugasFox

class BaseStrategy(ABC):
    """Abstract base class untuk semua execution strategies"""

    @abstractmethod
    async def execute(self, tugas: TugasFox) -> Any:
        pass
