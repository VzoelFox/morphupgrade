# tests/fox_engine/test_minifox_robustness.py
import pytest
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock

from fox_engine.core import TugasFox, FoxMode, IOType
from fox_engine.strategies.minifox import MiniFoxStrategy
from fox_engine.manager import ManajerFox

# Menandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio

async def mock_coroutine():
    """Coroutine tiruan untuk memenuhi persyaratan TugasFox."""
    pass

def mock_network_handler():
    """Handler I/O palsu untuk simulasi operasi jaringan."""
    return "data jaringan", 1024

async def test_network_io_handled_by_minifox():
    """Memverifikasi tugas IOType.NETWORK dieksekusi oleh MiniFox, bukan SimpleFox."""
    strategy = MiniFoxStrategy(max_io_workers=1)
    tugas = TugasFox(
        nama="tugas_unduh_jaringan",
        coroutine=mock_coroutine,
        mode=FoxMode.MINIFOX,
        jenis_operasi=IOType.NETWORK,
        io_handler=mock_network_handler
    )

    with patch('fox_engine.strategies.simplefox.SimpleFoxStrategy.execute', new_callable=AsyncMock) as mock_simplefox:
        hasil = await strategy.execute(tugas)
        assert hasil == "data jaringan"
        assert tugas.bytes_processed == 1024
        mock_simplefox.assert_not_called()

    strategy.shutdown()

async def test_fallback_with_invalid_io_handler():
    """Memverifikasi fallback ke SimpleFox jika jenis I/O diset tetapi io_handler tidak valid."""
    strategy = MiniFoxStrategy(max_io_workers=1)
    tugas = TugasFox(
        nama="tugas_io_gagal",
        coroutine=mock_coroutine,
        mode=FoxMode.MINIFOX,
        jenis_operasi=IOType.FILE,
        io_handler=None  # Handler tidak valid
    )

    with patch('fox_engine.strategies.simplefox.SimpleFoxStrategy.execute', new_callable=AsyncMock) as mock_simplefox:
        mock_simplefox.return_value = "dari fallback"
        hasil = await strategy.execute(tugas)
        assert hasil == "dari fallback"
        mock_simplefox.assert_called_once()

    strategy.shutdown()

async def test_manager_shutdown_triggers_strategy_shutdown():
    """Memverifikasi ManajerFox.shutdown() memanggil MiniFoxStrategy.shutdown()."""
    # Gunakan ManajerFox asli
    manajer = ManajerFox()

    # Ganti strategi MiniFox di dalamnya dengan mock
    mock_minifox_strategy = MagicMock(spec=MiniFoxStrategy)
    # Mock metode shutdown-nya
    mock_minifox_strategy.shutdown = MagicMock()

    manajer.strategi[FoxMode.MINIFOX] = mock_minifox_strategy

    # Panggil shutdown pada manajer
    await manajer.shutdown(timeout=0.1)

    # Verifikasi bahwa metode shutdown pada strategi mock kita dipanggil
    mock_minifox_strategy.shutdown.assert_called_once()

async def test_logging_is_called(caplog):
    """Memverifikasi bahwa logging dipanggil pada titik-titik kunci."""
    strategy = MiniFoxStrategy(max_io_workers=1)
    tugas = TugasFox(
        nama="tugas_cek_log",
        coroutine=mock_coroutine,
        mode=FoxMode.MINIFOX,
        jenis_operasi=IOType.FILE,
        io_handler=lambda: ("data file", 512)
    )
    # Inisialisasi eksplisit untuk pengujian logging yang konsisten
    await strategy._initialize()

    with caplog.at_level(logging.INFO):
        caplog.clear()
        # Inisialisasi (sudah dipanggil, cek bahwa tidak ada log duplikat)
        await strategy.execute(tugas)
        assert "Menginisialisasi JalurUtamaMultiArah MiniFox" not in caplog.text

        # Shutdown
        strategy.shutdown()
        assert "Memulai proses shutdown untuk JalurUtamaMultiArah MiniFox" in caplog.text
        assert "JalurUtamaMultiArah MiniFox berhasil dimatikan" in caplog.text

    # Verifikasi log level DEBUG
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        await strategy.execute(tugas)
        assert f"Menjalankan tugas I/O '{tugas.nama}'" in caplog.text
        strategy.shutdown()
