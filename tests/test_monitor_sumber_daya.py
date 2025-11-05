# tests/test_monitor_sumber_daya.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock

# Perlu setup path agar bisa impor fox_engine, mirip conftest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fox_engine.monitor_sumber_daya import MonitorSumberDaya
from fox_engine.batas_adaptif import BatasAdaptif
from fox_engine.manager import ManajerFox
from fox_engine.core import TugasFox, FoxMode

# Fixture untuk membuat instance monitor baru untuk setiap tes
@pytest.fixture
def monitor():
    batas = BatasAdaptif()
    return MonitorSumberDaya(batas)

# Fixture untuk membuat instance manajer baru untuk setiap tes
@pytest.fixture
def manajer_fox():
    # Pastikan manajer di-shutdown setelah tes selesai
    manager = ManajerFox()
    yield manager
    # Teardown: jalankan shutdown secara non-blocking
    asyncio.run(manager.shutdown())


@patch('fox_engine.monitor_sumber_daya.psutil')
def test_sistem_kelebihan_beban_karena_memori(mock_psutil, monitor):
    """Memverifikasi deteksi beban berlebih saat penggunaan memori tinggi."""
    mock_psutil.virtual_memory.return_value.percent = 85.0
    mock_psutil.cpu_percent.return_value = 50.0

    kesehatan = monitor.cek_kesehatan_sistem()
    assert monitor.sistem_kelebihan_beban(kesehatan) is True
    assert monitor.sistem_kritis(kesehatan) is False

@patch('fox_engine.monitor_sumber_daya.psutil')
def test_sistem_kelebihan_beban_karena_cpu(mock_psutil, monitor):
    """Memverifikasi deteksi beban berlebih saat penggunaan CPU tinggi."""
    mock_psutil.virtual_memory.return_value.percent = 50.0
    mock_psutil.cpu_percent.return_value = 90.0

    kesehatan = monitor.cek_kesehatan_sistem()
    assert monitor.sistem_kelebihan_beban(kesehatan) is True
    assert monitor.sistem_kritis(kesehatan) is False

@patch('fox_engine.monitor_sumber_daya.psutil')
def test_sistem_kondisi_kritis(mock_psutil, monitor):
    """Memverifikasi deteksi kondisi kritis saat penggunaan sumber daya sangat tinggi."""
    mock_psutil.virtual_memory.return_value.percent = 96.0
    mock_psutil.cpu_percent.return_value = 50.0

    kesehatan = monitor.cek_kesehatan_sistem()
    assert monitor.sistem_kelebihan_beban(kesehatan) is True
    assert monitor.sistem_kritis(kesehatan) is True

@patch('fox_engine.monitor_sumber_daya.psutil')
def test_sistem_kondisi_normal(mock_psutil, monitor):
    """Memverifikasi tidak ada deteksi beban saat penggunaan sumber daya normal."""
    mock_psutil.virtual_memory.return_value.percent = 50.0
    mock_psutil.cpu_percent.return_value = 50.0

    kesehatan = monitor.cek_kesehatan_sistem()
    assert monitor.sistem_kelebihan_beban(kesehatan) is False
    assert monitor.sistem_kritis(kesehatan) is False

@pytest.mark.asyncio
@patch('fox_engine.monitor_sumber_daya.psutil')
async def test_manajer_fox_fallback_saat_beban_tinggi(mock_psutil, manajer_fox, capsys):
    """Memverifikasi ManajerFox mengalihkan tugas tfox ke wfox saat beban tinggi."""
    mock_psutil.virtual_memory.return_value.percent = 88.0
    mock_psutil.cpu_percent.return_value = 50.0

    async def tugas_dummy():
        await asyncio.sleep(0.01)

    tugas = TugasFox("tugas_berat", tugas_dummy, FoxMode.THUNDERFOX, estimasi_durasi=1.0)

    # Ganti _eksekusi_waterfox agar kita bisa tahu itu dipanggil
    with patch.object(manajer_fox, '_eksekusi_waterfox', wraps=manajer_fox._eksekusi_waterfox) as mock_wfox:
        await manajer_fox.kirim(tugas)
        mock_wfox.assert_called_once()

    # Verifikasi pesan peringatan tercetak
    captured = capsys.readouterr()
    assert "Mengalihkan tugas" in captured.out
    assert "ke mode WaterFox" in captured.out


@pytest.mark.asyncio
@patch('fox_engine.monitor_sumber_daya.psutil')
async def test_manajer_fox_tolak_tugas_saat_kritis(mock_psutil, manajer_fox):
    """Memverifikasi ManajerFox menolak tugas baru saat sistem dalam kondisi kritis."""
    mock_psutil.virtual_memory.return_value.percent = 98.0
    mock_psutil.cpu_percent.return_value = 50.0

    async def tugas_dummy():
        pass

    tugas = TugasFox("tugas_apapun", tugas_dummy, FoxMode.AUTO)

    with pytest.raises(RuntimeError, match="Sistem dalam kondisi kritis"):
        await manajer_fox.kirim(tugas)

@patch('fox_engine.monitor_sumber_daya.PSUTIL_TERSEDIA', False)
def test_graceful_degradation_saat_psutil_tidak_ada():
    """Memverifikasi monitor tidak melakukan throttling jika psutil tidak tersedia."""
    batas = BatasAdaptif()
    # Peringatan harusnya muncul saat inisialisasi
    with pytest.warns(UserWarning, match="Pustaka 'psutil' tidak ditemukan"):
        monitor = MonitorSumberDaya(batas)

    # Dalam mode degradasi, monitor harus selalu mengembalikan False
    assert monitor.sistem_kelebihan_beban() is False
    assert monitor.sistem_kritis() is False

@pytest.mark.asyncio
@patch('fox_engine.monitor_sumber_daya.psutil')
async def test_penyesuaian_pool_dinamis(mock_psutil, manajer_fox):
    """Memverifikasi bahwa ukuran pool disesuaikan saat beban sistem berubah."""

    async def tugas_dummy():
        pass

    tugas = TugasFox("tugas_skala", tugas_dummy, FoxMode.AUTO)

    with patch.object(manajer_fox, '_sesuaikan_ukuran_pool', wraps=manajer_fox._sesuaikan_ukuran_pool) as mock_penyesuaian:
        # 1. Simulasikan beban tinggi untuk memicu scale down
        mock_psutil.virtual_memory.return_value.percent = 90.0
        mock_psutil.cpu_percent.return_value = 50.0

        await manajer_fox.kirim(tugas)

        mock_penyesuaian.assert_called_once()
        assert manajer_fox.batas_adaptif.maks_pekerja_tfox < manajer_fox.batas_adaptif.MAKS_PEKERJA_TFOX_AWAL

        # Hapus tugas agar bisa dikirim lagi
        manajer_fox.pencatat_tugas.hapus_tugas("tugas_skala")

        # 2. Simulasikan beban rendah untuk memicu scale up
        mock_psutil.virtual_memory.return_value.percent = 40.0
        mock_psutil.cpu_percent.return_value = 40.0

        await manajer_fox.kirim(tugas)

        # Harusnya dipanggil total 2 kali sekarang
        assert mock_penyesuaian.call_count == 2
        assert manajer_fox.batas_adaptif.maks_pekerja_tfox == manajer_fox.batas_adaptif.MAKS_PEKERJA_TFOX_AWAL
