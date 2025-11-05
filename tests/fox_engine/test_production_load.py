# tests/fox_engine/test_production_load.py
import pytest
import asyncio
from fox_engine.api import tfox, wfox, sfox, mfox, dapatkan_manajer_fox
from fox_engine import api as fox_api

@pytest.fixture(autouse=True)
def reset_manajer_global():
    """Memastikan setiap pengujian berjalan dengan instance manajer yang bersih."""
    fox_api._manajer_fox = None
    yield
    manajer = dapatkan_manajer_fox()
    if manajer and not manajer._sedang_shutdown:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(manajer.shutdown(timeout=1))
    fox_api._manajer_fox = None

@pytest.mark.asyncio
async def test_concurrent_mixed_workloads():
    """Mensimulasikan pola beban kerja produksi yang realistis."""
    # Beban Campuran: 60% SimpleFox, 20% MiniFox, 15% WaterFox, 5% ThunderFox
    workloads = [
        (sfox, "api_request", 0.01),      # SimpleFox: panggilan API cepat
        (sfox, "api_request", 0.01),
        (sfox, "api_request", 0.01),
        (sfox, "api_request", 0.01),
        (sfox, "api_request", 0.01),
        (sfox, "api_request", 0.01),
        (mfox, "file_read_op", 0.05),       # MiniFox: operasi file
        (mfox, "file_write_op", 0.05),
        (wfox, "db_query", 0.02),          # WaterFox: kueri basis data
        (wfox, "db_query", 0.02),
        (wfox, "db_query", 0.02),
        (tfox, "ml_inference", 0.1),      # ThunderFox: komputasi berat
    ]

    # Luncurkan 200 tugas konkuren dengan distribusi yang realistis
    # (Jumlah dikurangi dari 1000 untuk efisiensi pengujian)
    total_tasks = 200
    tasks = []
    for i in range(total_tasks):
        strategy, pattern, duration = workloads[i % len(workloads)]

        async def create_coro(d):
            await asyncio.sleep(d)

        tasks.append(strategy(f"{pattern}_{i}", lambda d=duration: create_coro(d)))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    failure_count = total_tasks - success_count

    print(f"Total Tugas: {total_tasks}, Berhasil: {success_count}, Gagal: {failure_count}")

    # Izinkan beberapa kegagalan karena beban, tetapi mayoritas harus berhasil
    success_rate = success_count / total_tasks
    assert success_rate > 0.95, f"Tingkat keberhasilan di bawah beban ({success_rate:.2%}) lebih rendah dari ambang batas 95%"

    manajer = dapatkan_manajer_fox()
    assert manajer.metrik.tugas_gagal <= (total_tasks * 0.05)
