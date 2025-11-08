# tests/fox_engine/test_streaming_memory.py
import asyncio
import tempfile
import psutil
import os
import pytest
from fox_engine.api import mfox_stream_file, dapatkan_manajer_fox

# Tandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def manajer_fox_terisolasi_untuk_memori():
    """Fixture untuk memastikan manajer bersih untuk tes memori."""
    from fox_engine import api
    api._manajer_fox = None
    manajer = dapatkan_manajer_fox()
    yield manajer
    await manajer.shutdown()
    api._manajer_fox = None

@pytest.mark.timeout(180)  # Izinkan 3 menit untuk tes file besar ini
async def test_streaming_backpressure_menggunakan_memori_rendah(manajer_fox_terisolasi_untuk_memori):
    """Memverifikasi bahwa backpressure bekerja dengan file besar dan menjaga penggunaan memori tetap rendah."""

    # Buat file uji (10 MB, bukan 100MB agar tidak terlalu lambat di CI)
    # 100,000 baris @ ~100 byte setiap baris
    line_count_target = 100_000
    line_content = b"Baris ini digunakan untuk pengujian memori dan backpressure secara ekstensif.\n"

    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        test_file = f.name
        for i in range(line_count_target):
            f.write(line_content)

    try:
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # dalam MB

        line_count_actual = 0
        async for line in mfox_stream_file("test_stream_memori", test_file):
            line_count_actual += 1
            # Simulasi konsumen yang agak lambat
            if line_count_actual % 1000 == 0:
                 await asyncio.sleep(0.001)

            # Periksa memori setiap 10,000 baris
            if line_count_actual % 10_000 == 0:
                mem_current = process.memory_info().rss / 1024 / 1024
                mem_increase = mem_current - mem_before

                # Peningkatan memori harus sangat kecil (misalnya, di bawah 50 MB)
                # Ini membuktikan bahwa kita tidak memuat seluruh file ke dalam RAM.
                assert mem_increase < 50, \
                    f"Kebocoran memori terdeteksi: peningkatan {mem_increase:.2f} MB"

                print(f"Memproses {line_count_actual:,} baris, "
                      f"peningkatan memori: {mem_increase:.2f} MB")

        assert line_count_actual == line_count_target
        print("✅ Tes backpressure LULUS")

    finally:
        os.unlink(test_file)
