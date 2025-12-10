# tests/fox_engine/test_thunderfox.py
"""
Tes khusus untuk ThunderFoxStrategy, berfokus pada eksekusi
tugas di thread pool.
"""
import pytest
import asyncio
import threading

from fox_engine.core import TugasFox, FoxMode
from fox_engine.strategies import ThunderFoxStrategy
from fox_engine.internal.jalur_utama_multi_arah import JalurUtamaMultiArah

# Tandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio

async def test_thunderfox_executes_in_thread_pool():
    """Memverifikasi ThunderFoxStrategy mengeksekusi tugas di thread yang berbeda."""

    # Buat instance JalurUtamaMultiArah (executor) secara manual untuk tes
    executor = JalurUtamaMultiArah(maks_pekerja=1, nama_prefiks_jalur="thunderfox-test")
    strategy = ThunderFoxStrategy(eksekutor_tfox=executor)

    main_thread_id = threading.current_thread().ident
    task_thread_id = None

    def cpu_bound_work():
        """Pekerjaan sinkron dan berat yang sebenarnya."""
        nonlocal task_thread_id
        task_thread_id = threading.current_thread().ident
        sum(i*i for i in range(10**4))
        return True

    async def async_wrapper_for_sync_task():
        """Membungkus pekerjaan sinkron dalam coroutine."""
        return cpu_bound_work()

    tugas = TugasFox(
        nama="thunderfox-thread-test",
        # Strategi mengharapkan coroutine, yang kemudian dijalankan di thread lain
        coroutine_func=async_wrapper_for_sync_task,
        mode=FoxMode.THUNDERFOX
    )

    hasil = await strategy.execute(tugas)

    # Verifikasi tugas berhasil
    assert hasil is True

    # Verifikasi paling penting: ID thread tugas tidak sama dengan ID thread utama.
    assert task_thread_id is not None
    assert task_thread_id != main_thread_id

    await strategy.shutdown()
