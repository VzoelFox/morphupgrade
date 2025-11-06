# tests/fox_engine/test_shutdown_robustness.py
import asyncio
import pytest
from fox_engine.core import TugasFox, FoxMode
from fox_engine.manager import ManajerFox

@pytest.mark.asyncio
async def test_shutdown_cancels_lingering_tasks():
    """
    Memverifikasi bahwa ManajerFox.shutdown() membatalkan tugas yang berjalan
    lebih lama dari periode graceful shutdown.
    """
    manajer = ManajerFox()

    lingering_task_completed = asyncio.Event()

    async def long_running_coroutine():
        """Coroutine yang berjalan lebih lama dari batas waktu shutdown."""
        try:
            await asyncio.sleep(5)  # Jauh lebih lama dari timeout shutdown
            lingering_task_completed.set() # Ini seharusnya tidak pernah tercapai
        except asyncio.CancelledError:
            # Ini yang kita harapkan
            raise

    tugas = TugasFox("tugas_macet", long_running_coroutine, FoxMode.SIMPLEFOX)

    # Kirim tugas dan jangan tunggu (await)
    asyncio.create_task(manajer.kirim(tugas))

    # Beri waktu sedikit agar tugas mulai berjalan
    await asyncio.sleep(0.1)
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 1

    # Lakukan shutdown dengan timeout singkat
    await manajer.shutdown(timeout=0.2)

    # Verifikasi
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 0
    assert not lingering_task_completed.is_set(), "Tugas yang macet seharusnya tidak pernah selesai"

@pytest.mark.asyncio
async def test_shutdown_waits_for_normal_tasks():
    """
    Memverifikasi bahwa ManajerFox.shutdown() menunggu tugas yang selesai
    dalam periode graceful shutdown.
    """
    manajer = ManajerFox()

    normal_task_completed = asyncio.Event()

    async def normal_coroutine():
        """Coroutine yang selesai dengan cepat."""
        await asyncio.sleep(0.1)
        normal_task_completed.set()

    tugas = TugasFox("tugas_normal", normal_coroutine, FoxMode.SIMPLEFOX)

    # Kirim tugas
    asyncio.create_task(manajer.kirim(tugas))
    await asyncio.sleep(0.01) # Pastikan tugas terdaftar

    # Lakukan shutdown dengan timeout yang cukup
    await manajer.shutdown(timeout=1.0)

    # Verifikasi
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 0
    assert normal_task_completed.is_set(), "Tugas normal seharusnya selesai"
