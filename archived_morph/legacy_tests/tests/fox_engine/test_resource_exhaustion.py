# tests/fox_engine/test_resource_exhaustion.py
import pytest
import asyncio
from unittest.mock import patch
import platform

from fox_engine.api import sfox, mfox, dapatkan_manajer_fox
from fox_engine import api as fox_api

# Coba impor psutil, lewati pengujian jika tidak tersedia
try:
    import psutil
    PSUTIL_TERSEDIA = True
except ImportError:
    PSUTIL_TERSEDIA = False

# Coba impor resource, hanya tersedia di Unix
try:
    import resource
    RESOURCE_TERSEDIA = True
except ImportError:
    RESOURCE_TERSEDIA = False

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

@pytest.mark.skipif(not PSUTIL_TERSEDIA, reason="psutil tidak terinstal, pengujian tekanan memori dilewati")
@pytest.mark.asyncio
async def test_memory_pressure_handling():
    """Menguji perilaku di bawah tekanan memori yang disimulasikan."""

    async def tugas_sederhana():
        await asyncio.sleep(0.01)
        return "sukses"

    # Jalankan tugas di bawah kondisi memori tinggi yang disimulasikan
    with patch('psutil.virtual_memory') as mock_mem:
        # Simulasikan penggunaan memori 95%
        mock_mem.return_value.percent = 95.0

        # Manajer harus tetap dapat menjalankan tugas sederhana
        hasil = await sfox("tugas_tekanan_memori", tugas_sederhana)
        assert hasil == "sukses"

@pytest.mark.skipif(platform.system() == "Windows" or not RESOURCE_TERSEDIA, reason="Modul resource tidak tersedia di Windows")
@pytest.mark.asyncio
async def test_file_descriptor_exhaustion_graceful_handling():
    """Menguji perilaku saat deskriptor berkas hampir habis."""

    # Dapatkan batas saat ini
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    try:
        # Kurangi batas sementara untuk mensimulasikan kehabisan
        # Atur ke nilai yang sangat rendah namun cukup untuk pytest berjalan
        batas_rendah = 30
        resource.setrlimit(resource.RLIMIT_NOFILE, (batas_rendah, hard))

        async def tugas_operasi_file():
            # Tugas ini harus gagal dengan anggun, bukan mogok
            try:
                # Coba buka lebih banyak file daripada batas yang diizinkan
                berkas_terbuka = [open(f"/tmp/test_fd_{i}.tmp", "w") for i in range(batas_rendah)]
                for f in berkas_terbuka:
                    f.close()
                return "sukses"
            except OSError as e:
                # Harapkan error "Too many open files"
                if "Too many open files" in str(e):
                    return "ditangani_dengan_anggun"
                raise

        # Manajer harus menangani kegagalan tugas ini tanpa mogok
        hasil = await mfox("tugas_fd_pressure", tugas_operasi_file)
        assert hasil == "ditangani_dengan_anggun"

    finally:
        # Kembalikan batas ke nilai semula
        resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
