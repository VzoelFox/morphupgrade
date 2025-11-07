# tests/fox_engine/test_manager_integration.py
import pytest
import asyncio

# Impor modul api untuk mengakses dan me-reset manajer global
from fox_engine import api
from fox_engine.api import sfox, mfox, fox, dapatkan_manajer_fox


@pytest.mark.asyncio
async def test_sfox_api_call():
    """Menguji panggilan API sfox() terintegrasi dengan benar."""

    async def tugas_cepat():
        return "sfox_success"

    # Panggil fungsi API secara langsung
    hasil = await sfox("tugas_sfox", tugas_cepat, estimasi_durasi=0.05)
    assert hasil == "sfox_success"

    # Dapatkan manajer global yang benar untuk verifikasi
    manajer_global = dapatkan_manajer_fox()
    assert manajer_global.metrik.tugas_sfox_selesai == 1
    assert manajer_global.metrik.tugas_gagal == 0

@pytest.mark.asyncio
async def test_auto_mode_selects_simplefox():
    """Menguji mode AUTO memilih SimpleFox untuk tugas singkat."""

    async def tugas_sangat_singkat():
        return "auto_sfox"

    # Panggil fungsi API secara langsung
    hasil = await fox("tugas_auto_sfox", tugas_sangat_singkat, estimasi_durasi=0.05)
    assert hasil == "auto_sfox"

    # Dapatkan manajer global yang benar untuk verifikasi
    manajer_global = dapatkan_manajer_fox()
    assert manajer_global.metrik.tugas_sfox_selesai == 1
    assert manajer_global.metrik.tugas_wfox_selesai == 0

# TODO: Tambahkan lebih banyak pengujian integrasi untuk semua mode di Fase 2

from unittest.mock import patch
from fox_engine.core import TugasFox, FoxMode, IOType

@pytest.mark.asyncio
async def test_metrics_updated_once_for_minifox():
    """
    BLOCKER-4 VALIDATION:
    Memastikan _perbarui_metrik_keberhasilan hanya dipanggil sekali per tugas.
    """
    manajer = dapatkan_manajer_fox()

    async def dummy_coro():
        return "data"

    def dummy_io_handler():
        return "data", 128

    tugas = TugasFox(
        nama="tugas_uji_io_metrics",
        coroutine_func=dummy_coro,
        mode=FoxMode.MINIFOX,
        jenis_operasi=IOType.FILE_GENERIC,
        io_handler=dummy_io_handler
    )

    with patch.object(manajer, '_ManajerFox__perbarui_metrik_keberhasilan', wraps=manajer._ManajerFox__perbarui_metrik_keberhasilan) as spy_update_metrics:
        await manajer.kirim(tugas)
        spy_update_metrics.assert_called_once()
