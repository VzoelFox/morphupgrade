# tests/fox_engine/test_waterfox.py
"""
Tes khusus untuk WaterFoxStrategy, berfokus pada mekanisme
pembatasan konkurensi (semaphore).
"""
import pytest
import asyncio

from fox_engine.core import TugasFox, FoxMode
from fox_engine.strategies import WaterFoxStrategy
from fox_engine.internal.garis_tugas import GarisTugas

# Tandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio

async def test_waterfox_concurrency_limit():
    """Memverifikasi WaterFoxStrategy membatasi tugas konkuren sesuai dengan batas semaphore."""

    concurrency_limit = 2
    # Buat instance GarisTugas (semaphore) secara manual untuk tes
    semaphore = GarisTugas(concurrency_limit)
    strategy = WaterFoxStrategy(semafor_wfox=semaphore)

    num_tasks = 5
    tasks_running = 0
    max_concurrent_tasks_observed = 0

    # Kunci untuk melindungi akses ke variabel bersama
    lock = asyncio.Lock()

    async def slow_task():
        """Tugas lambat yang melacak konkurensi."""
        nonlocal tasks_running, max_concurrent_tasks_observed

        async with lock:
            tasks_running += 1
            max_concurrent_tasks_observed = max(max_concurrent_tasks_observed, tasks_running)

        await asyncio.sleep(0.1)  # Simulasikan pekerjaan

        async with lock:
            tasks_running -= 1

        return True

    # Buat dan jalankan tugas
    tasks_to_run = []
    for i in range(num_tasks):
        tugas = TugasFox(
            nama=f"waterfox-concurrency-test-{i}",
            coroutine_func=slow_task,
            mode=FoxMode.WATERFOX
        )
        tasks_to_run.append(strategy.execute(tugas))

    hasil = await asyncio.gather(*tasks_to_run)

    # Verifikasi semua tugas berhasil
    assert all(hasil)

    # Verifikasi paling penting: konkurensi tidak pernah melebihi batas.
    assert max_concurrent_tasks_observed == concurrency_limit

    await strategy.shutdown()
