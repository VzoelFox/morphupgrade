# tests/fox_engine/test_error_handling.py
import pytest
import asyncio
from unittest.mock import patch
import time

from fox_engine import sfox
from fox_engine.api import dapatkan_manajer_fox
from fox_engine import api as fox_api

# Fixture untuk me-reset manajer global sebelum setiap pengujian
@pytest.fixture(autouse=True)
def reset_manajer_global():
    """Memastikan setiap pengujian berjalan dengan instance manajer yang bersih."""
    fox_api._manajer_fox = None
    yield
    fox_api._manajer_fox = None

@pytest.mark.asyncio
async def test_error_propagation_to_caller():
    """Menguji bahwa exception di dalam tugas dipropagasi dengan benar ke pemanggil."""
    async def tugas_gagal():
        raise ValueError("Tugas gagal seperti yang diharapkan")

    with pytest.raises(ValueError, match="Tugas gagal seperti yang diharapkan"):
        await sfox("tugas_gagal", tugas_gagal)

    # Verifikasi bahwa kegagalan dicatat
    manajer = dapatkan_manajer_fox()
    assert manajer.metrik.tugas_gagal == 1
    assert manajer.metrik.tugas_sfox_selesai == 0

@pytest.mark.asyncio
async def test_circuit_breaker_trips_after_failures():
    """Menguji bahwa pemutus sirkuit terbuka setelah beberapa kegagalan."""
    manajer = dapatkan_manajer_fox()
    # Atur ambang batas yang lebih rendah untuk pengujian yang lebih cepat
    manajer.pemutus_sirkuit.ambang_kegagalan = 3
    manajer.pemutus_sirkuit.batas_waktu_reset = 60 # Waktu reset yang panjang

    async def tugas_gagal_selalu():
        raise ZeroDivisionError("Gagal!")

    # Picu beberapa kegagalan untuk membuka sirkuit
    for i in range(manajer.pemutus_sirkuit.ambang_kegagalan):
        with pytest.raises(ZeroDivisionError):
            await sfox(f"gagal_{i}", tugas_gagal_selalu)

    # Verifikasi bahwa sirkuit sekarang terbuka
    assert not manajer.pemutus_sirkuit.bisa_eksekusi()

    # Verifikasi bahwa tugas berikutnya ditolak tanpa dieksekusi
    with pytest.raises(RuntimeError, match="Pemutus sirkuit terbuka"):
        await sfox("tugas_yang_ditolak", tugas_gagal_selalu)

@pytest.mark.asyncio
async def test_circuit_breaker_resets_after_timeout():
    """Menguji bahwa pemutus sirkuit di-reset setelah batas waktu."""
    manajer = dapatkan_manajer_fox()
    manajer.pemutus_sirkuit.ambang_kegagalan = 2
    manajer.pemutus_sirkuit.batas_waktu_reset = 10 # detik

    async def tugas_gagal():
        raise ValueError("Gagal")

    # Buka sirkuit
    with pytest.raises(ValueError):
        await sfox("gagal_1", tugas_gagal)
    with pytest.raises(ValueError):
        await sfox("gagal_2", tugas_gagal)

    assert not manajer.pemutus_sirkuit.bisa_eksekusi()

    # Gunakan mock untuk "memajukan" waktu
    waktu_sekarang = time.time()
    with patch('time.time', return_value=waktu_sekarang + manajer.pemutus_sirkuit.batas_waktu_reset + 1):
        # Verifikasi bahwa sirkuit sekarang tertutup kembali
        assert manajer.pemutus_sirkuit.bisa_eksekusi()

    # Tugas berikutnya harus berhasil (atau setidaknya dieksekusi)
    async def tugas_sukses():
        return "sukses"

    hasil = await sfox("tugas_sukses_setelah_reset", tugas_sukses)
    assert hasil == "sukses"
    # Verifikasi bahwa penghitung kegagalan di-reset
    assert manajer.pemutus_sirkuit.jumlah_kegagalan == 0
