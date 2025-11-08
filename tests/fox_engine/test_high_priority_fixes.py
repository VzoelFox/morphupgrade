# tests/fox_engine/test_high_priority_fixes.py
"""
Suite tes terpusat untuk memvalidasi perbaikan kritis berprioritas tinggi
yang diimplementasikan di Fox Engine v1.0.1-fase1.

Ini mencakup:
- Pembersihan sesi jaringan saat terjadi galat.
- Inisialisasi executor yang aman antar-thread (thread-safe).
- Efisiensi memori streaming file (backpressure).
"""

import pytest
import aiohttp
import asyncio
from unittest.mock import patch, AsyncMock

from fox_engine.api import mfox_request_jaringan, dapatkan_manajer_fox
from fox_engine.errors import JaringanKesalahan
from fox_engine.strategies import MiniFoxStrategy
from fox_engine.core import TugasFox, FoxMode, IOType

import pytest_asyncio

# Tandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def manajer_fox_terisolasi():
    """Fixture untuk memastikan setiap tes mendapatkan instance ManajerFox yang bersih."""
    from fox_engine import api
    api._manajer_fox = None
    manajer = dapatkan_manajer_fox()
    yield manajer
    await manajer.shutdown()
    api._manajer_fox = None

class TestHighPriorityFixes:
    """Mengelompokkan tes validasi untuk perbaikan kritis."""

    async def test_network_session_cleanup_on_error(self, manajer_fox_terisolasi):
        """Memverifikasi sesi dikembalikan ke pool bahkan jika tugas jaringan gagal."""

        class PengecualianTesJaringan(Exception):
            pass

        async def coro_jaringan_gagal(sesi: aiohttp.ClientSession):
            """Coroutine palsu yang selalu melempar galat."""
            raise PengecualianTesJaringan("Kegagalan jaringan yang disengaja")

        # Temukan strategi MiniFox untuk mem-patch kolam koneksinya
        minifox_strategy = next(
            s for s in manajer_fox_terisolasi.strategi.values()
            if isinstance(s, MiniFoxStrategy)
        )

        with patch.object(minifox_strategy.kolam_koneksi, 'kembalikan_sesi', new_callable=AsyncMock) as mock_kembalikan:
            with pytest.raises(JaringanKesalahan):
                await mfox_request_jaringan("gagal-network-test", coro_jaringan_gagal)

            # Verifikasi paling penting: sesi dikembalikan MESKIPUN terjadi kegagalan.
            mock_kembalikan.assert_awaited_once()

    async def test_executor_concurrent_initialization(self, manajer_fox_terisolasi):
        """Memverifikasi inisialisasi executor hanya terjadi sekali di bawah beban konkuren."""

        strategy = MiniFoxStrategy(max_io_workers=2)

        # Patch kelas JalurUtamaMultiArah untuk memverifikasi konstruktornya dipanggil sekali
        with patch('fox_engine.strategies.minifox.JalurUtamaMultiArah') as mock_executor_class:

            num_concurrent_tasks = 50

            def dummy_io_handler():
                return "sukses", 10

            tasks_to_run = []
            for i in range(num_concurrent_tasks):
                tugas = TugasFox(
                    nama=f"init-race-test-{i}",
                    mode=FoxMode.MINIFOX,
                    jenis_operasi=IOType.FILE_BACA,
                    io_handler=dummy_io_handler
                )
                # `execute` akan memicu `_initialize_executor_sync` secara internal
                tasks_to_run.append(strategy.execute(tugas))

            await asyncio.gather(*tasks_to_run)

            # Verifikasi bahwa konstruktor JalurUtamaMultiArah hanya dipanggil SEKALI.
            mock_executor_class.assert_called_once()

        await strategy.shutdown()

    @pytest.mark.timeout(180)  # Izinkan 3 menit untuk tes file besar ini
    async def test_streaming_memory_efficiency(self, manajer_fox_terisolasi):
        """Memverifikasi backpressure mencegah penggunaan memori berlebih saat streaming file besar."""
        import tempfile
        import psutil
        import os
        from fox_engine.api import mfox_stream_file

        line_count_target = 100_000
        line_content = b"Baris ini untuk pengujian memori dan backpressure secara ekstensif.\n"

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            test_file = f.name
            for _ in range(line_count_target):
                f.write(line_content)

        try:
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / 1024 / 1024  # MB

            line_count_actual = 0
            async for _ in mfox_stream_file("test_stream_memori_efisiensi", test_file):
                line_count_actual += 1
                if line_count_actual % 1000 == 0:
                     await asyncio.sleep(0.001)

                if line_count_actual % 10_000 == 0:
                    mem_current = process.memory_info().rss / 1024 / 1024
                    mem_increase = mem_current - mem_before

                    assert mem_increase < 50, f"Peningkatan memori {mem_increase:.2f} MB melebihi batas"

            assert line_count_actual == line_count_target

        finally:
            os.unlink(test_file)
