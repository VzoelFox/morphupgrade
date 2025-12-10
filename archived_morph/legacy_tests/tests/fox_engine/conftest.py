# tests/fox_engine/conftest.py
import pytest_asyncio
import asyncio

from fox_engine import api

@pytest_asyncio.fixture(autouse=True)
async def reset_manajer_global_otomatis():
    """
    Fixture autouse async untuk memastikan manajer global di-reset sebelum dan
    sesudah setiap pengujian. Menggunakan fixture async memastikan teardown
    dijalankan di dalam event loop yang sama dengan tes.
    """
    # Fase Setup: Pastikan tidak ada manajer sebelum pengujian dimulai
    api._manajer_fox = None

    yield  # Ini adalah titik di mana pengujian dijalankan

    # Fase Teardown: Dapatkan manajer (jika dibuat), matikan, dan reset
    manajer = api.dapatkan_manajer_fox_tanpa_inisialisasi()
    if manajer and not manajer._sedang_shutdown:
        try:
            # Karena fixture ini async, kita bisa langsung await shutdown.
            # Ini akan berjalan sebelum pytest-asyncio menutup event loop.
            await asyncio.wait_for(manajer.shutdown(timeout=1.5), timeout=2.0)
        except asyncio.TimeoutError:
            print("PERINGATAN: manajer.shutdown() timeout saat teardown.")

    api._manajer_fox = None
