# tests/fox_engine/test_simplefox.py
import pytest
import asyncio
from fox_engine.strategies.simplefox import SimpleFoxStrategy
from fox_engine.core import TugasFox, FoxMode

@pytest.mark.asyncio
async def test_simple_execution():
    """Menguji eksekusi tugas sederhana."""
    strategy = SimpleFoxStrategy()

    async def coro_sederhana():
        await asyncio.sleep(0.01)
        return "success"

    tugas = TugasFox(
        nama="test_simple",
        coroutine_func=coro_sederhana,
        mode=FoxMode.SIMPLEFOX
    )

    hasil = await strategy.execute(tugas)
    assert hasil == "success"

@pytest.mark.asyncio
async def test_timeout_handling():
    """Menguji perilaku batas waktu."""
    strategy = SimpleFoxStrategy()

    async def coro_lama():
        await asyncio.sleep(1.0)

    tugas = TugasFox(
        nama="test_timeout",
        coroutine_func=coro_lama,
        mode=FoxMode.SIMPLEFOX,
        batas_waktu=0.1  # Batas waktu singkat
    )

    with pytest.raises(asyncio.TimeoutError):
        await strategy.execute(tugas)
