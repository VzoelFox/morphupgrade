# tests/fox_engine/test_long_running.py
import pytest
import asyncio
import time
import gc
from unittest.mock import patch

from fox_engine.api import sfox, dapatkan_manajer_fox
from fox_engine import api as fox_api

try:
    import psutil
    PSUTIL_TERSEDIA = True
except ImportError:
    PSUTIL_TERSEDIA = False

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

@pytest.mark.timeout(30)  # Tingkatkan batas waktu khusus untuk pengujian ini
@pytest.mark.skipif(not PSUTIL_TERSEDIA, reason="psutil tidak terinstal, pengujian stabilitas dilewati")
@pytest.mark.asyncio
async def test_accelerated_long_run_stability():
    """Mensimulasikan operasi jangka panjang untuk mendeteksi kebocoran memori."""
    manajer = dapatkan_manajer_fox()
    start_time = time.time()
    task_count = 0
    memory_samples = []

    # Ambil sampel memori awal
    process = psutil.Process()
    memory_samples.append(process.memory_info().rss)

    # Simulasikan 1 jam dalam waktu yang dipercepat (misalnya, 10 detik nyata)
    simulated_duration_hours = 1
    real_duration_seconds = 10

    end_time = start_time + real_duration_seconds
    while time.time() < end_time:
        # Jalankan beberapa tugas dalam satu iterasi
        tasks = []
        for i in range(50):
            task_count += 1
            tasks.append(sfox(f"long_run_{task_count}", lambda: asyncio.sleep(0.01)))

        await asyncio.gather(*tasks, return_exceptions=True)

        # Beri sedikit waktu agar event loop dapat memproses
        await asyncio.sleep(0.05)

    # Paksa pengumpulan sampah
    gc.collect()

    # Ambil sampel memori akhir
    memory_samples.append(process.memory_info().rss)

    # Verifikasi bahwa tidak ada tugas yang bocor
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 0, "Terdeteksi adanya tugas yang bocor (tidak selesai)"

    # Verifikasi stabilitas: pertumbuhan memori harus dalam batas wajar
    memory_growth = (memory_samples[-1] - memory_samples[0]) / memory_samples[0] if memory_samples[0] > 0 else 0

    print(f"Pertumbuhan Memori: {memory_growth:.2%}")
    print(f"Memori Awal: {memory_samples[0] / 1024**2:.2f} MB, Akhir: {memory_samples[-1] / 1024**2:.2f} MB")

    # Izinkan pertumbuhan memori hingga 50% (nilai yang sangat longgar)
    assert memory_growth < 0.5, f"Terdeteksi potensi kebocoran memori: pertumbuhan sebesar {memory_growth:.1%}"
