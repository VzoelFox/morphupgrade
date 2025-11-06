# tests/fox_engine/test_health_monitoring.py
# FASE-3A: Tes untuk fitur Health & Monitoring.
import pytest
import platform
from unittest.mock import patch, MagicMock
import asyncio

from fox_engine.manager import ManajerFox
from fox_engine.core import TugasFox, FoxMode, IOType

@pytest.fixture
def manajer():
    """Fixture untuk instance ManajerFox baru."""
    return ManajerFox()

def test_info_os_tercatat_saat_inisialisasi(manajer: ManajerFox):
    """
    Memverifikasi bahwa informasi sistem operasi dicatat dengan benar
    di dalam objek MetrikFox saat ManajerFox diinisialisasi.
    """
    info_os_expected = f"{platform.system()} {platform.release()} ({platform.machine()})"
    assert manajer.metrik.info_os == info_os_expected
    assert manajer.metrik.info_os != "Tidak diketahui"


@pytest.mark.asyncio
@patch('fox_engine.manager.psutil', autospec=True)
async def test_metrik_sumber_daya_tercatat_di_tugas(mock_psutil, manajer: ManajerFox):
    """
    Memverifikasi bahwa penggunaan CPU dan memori dicatat dengan benar
    dalam objek TugasFox setelah eksekusi.
    """
    # Konfigurasi mock untuk psutil.Process()
    mock_process = MagicMock()
    mock_psutil.Process.return_value = mock_process
    manajer._proses_saat_ini = mock_psutil.Process()

    # Simulasikan nilai sebelum dan sesudah eksekusi
    mock_process.cpu_times.side_effect = [MagicMock(user=10.0), MagicMock(user=15.5)]
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * 1024 * 1024),  # 100 MB
        MagicMock(rss=125 * 1024 * 1024)   # 125 MB
    ]

    async def tugas_kosong():
        await asyncio.sleep(0.01)

    tugas = TugasFox(
        nama="Tugas Tes Kesehatan",
        mode=FoxMode.THUNDERFOX,
        coroutine_func=tugas_kosong,
        jenis_operasi=None
    )

    await manajer.kirim(tugas)

    # Verifikasi bahwa metrik dicatat dengan benar di TugasFox
    assert tugas.penggunaan_cpu == pytest.approx(5.5)
    assert tugas.penggunaan_memori == 25 * 1024 * 1024  # 25 MB


@pytest.mark.asyncio
@patch('fox_engine.manager.psutil', autospec=True)
async def test_rata_rata_metrik_sumber_daya_diperbarui(mock_psutil, manajer: ManajerFox):
    """
    Memverifikasi bahwa ManajerFox menghitung rata-rata bergerak untuk
    penggunaan CPU dan memori dengan benar.
    """
    mock_process = MagicMock()
    mock_psutil.Process.return_value = mock_process
    manajer._proses_saat_ini = mock_psutil.Process()

    # Tugas 1: CPU 5.5s, Memori 25MB
    # Tugas 2: CPU 10.0s, Memori 50MB
    mock_process.cpu_times.side_effect = [
        MagicMock(user=10.0), MagicMock(user=15.5),
        MagicMock(user=20.0), MagicMock(user=30.0)
    ]
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * 1024 * 1024), MagicMock(rss=125 * 1024 * 1024),
        MagicMock(rss=200 * 1024 * 1024), MagicMock(rss=250 * 1024 * 1024)
    ]

    async def tugas_kosong():
        await asyncio.sleep(0.01)

    # Tugas 1
    tugas1 = TugasFox(nama="T1", mode=FoxMode.THUNDERFOX, coroutine_func=tugas_kosong, jenis_operasi=None)
    await manajer.kirim(tugas1)

    assert manajer.metrik.avg_cpu_tfox == pytest.approx(5.5)
    assert manajer.metrik.avg_mem_tfox == pytest.approx(25 * 1024 * 1024)
    assert manajer.metrik.tugas_tfox_selesai == 1

    # Tugas 2
    tugas2 = TugasFox(nama="T2", mode=FoxMode.THUNDERFOX, coroutine_func=tugas_kosong, jenis_operasi=None)
    await manajer.kirim(tugas2)

    # Rata-rata baru:
    # CPU: (5.5 * 1 + 10.0) / 2 = 7.75
    # Mem: (25 * 1 + 50) / 2 = 37.5
    expected_avg_cpu = ((5.5 * 1) + 10.0) / 2
    expected_avg_mem = ((25 * 1024 * 1024 * 1) + (50 * 1024 * 1024)) / 2

    assert manajer.metrik.avg_cpu_tfox == pytest.approx(expected_avg_cpu)
    assert manajer.metrik.avg_mem_tfox == pytest.approx(expected_avg_mem)
    assert manajer.metrik.tugas_tfox_selesai == 2


@pytest.mark.asyncio
@patch('fox_engine.manager.PSUTIL_TERSEDIA', False)
async def test_graceful_degradation_ketika_psutil_tidak_tersedia(manajer: ManajerFox):
    """
    Memverifikasi bahwa sistem berjalan tanpa error dan metrik sumber daya
    diatur ke 0 ketika psutil tidak tersedia.
    """
    async def tugas_kosong():
        await asyncio.sleep(0.01)

    tugas = TugasFox(
        nama="Tugas Tanpa Psutil",
        mode=FoxMode.THUNDERFOX,
        coroutine_func=tugas_kosong,
        jenis_operasi=None
    )

    # Eksekusi tugas
    await manajer.kirim(tugas)

    # Verifikasi bahwa tidak ada error dan metrik diatur ke 0
    assert tugas.penggunaan_cpu == 0
    assert tugas.penggunaan_memori == 0
    assert manajer.metrik.avg_cpu_tfox == 0
    assert manajer.metrik.avg_mem_tfox == 0
    assert manajer.metrik.tugas_tfox_selesai == 1
