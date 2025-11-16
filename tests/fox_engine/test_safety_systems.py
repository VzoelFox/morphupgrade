# tests/fox_engine/test_safety_systems.py
import pytest
import asyncio
import time

from fox_engine.api import dapatkan_manajer_fox, sfox, fox
from fox_engine import api as fox_api

@pytest.fixture(autouse=True)
def reset_manajer_global():
    """Memastikan setiap pengujian berjalan dengan instance manajer yang bersih."""
    fox_api._manajer_fox = None
    yield
    # Proses shutdown yang anggun setelah pengujian untuk membersihkan sumber daya
    manajer = dapatkan_manajer_fox()
    if manajer:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(manajer.shutdown(timeout=1))
    fox_api._manajer_fox = None

@pytest.mark.asyncio
async def test_duplicate_task_is_renamed_and_runs():
    """
    Menguji bahwa tugas dengan nama duplikat diganti namanya secara otomatis
    dan kedua tugas berjalan secara bersamaan tanpa error.
    """
    manajer = dapatkan_manajer_fox()
    hasil_bersama = []

    async def tugas_yang_dimodifikasi(id_tugas):
        await asyncio.sleep(0.1)
        hasil_bersama.append(id_tugas)

    # Kirim dua tugas dengan nama yang sama secara berurutan, jalankan di latar belakang
    tugas1_handle = asyncio.create_task(sfox("tugas_sama", lambda: tugas_yang_dimodifikasi(1)))
    tugas2_handle = asyncio.create_task(sfox("tugas_sama", lambda: tugas_yang_dimodifikasi(2)))

    # Pada satu titik, kedua tugas harus aktif
    # (Meskipun ini kondisi balapan, sleep kecil membuatnya sangat mungkin)
    await asyncio.sleep(0.05)
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 2

    # Tunggu kedua tugas selesai
    await asyncio.gather(tugas1_handle, tugas2_handle)

    # Verifikasi bahwa kedua tugas benar-benar berjalan
    assert len(hasil_bersama) == 2
    assert sorted(hasil_bersama) == [1, 2]
    # Verifikasi bahwa setelah selesai, tidak ada tugas yang aktif
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 0

@pytest.mark.asyncio
async def test_shutdown_waits_for_active_tasks():
    """Menguji bahwa shutdown menunggu tugas yang sedang berjalan untuk selesai."""
    manajer = dapatkan_manajer_fox()

    durasi_tugas = 0.2
    waktu_mulai = time.time()

    async def tugas_yang_berjalan():
        await asyncio.sleep(durasi_tugas)

    # Kirim tugas tanpa menunggunya selesai
    asyncio.create_task(sfox("tugas_aktif", tugas_yang_berjalan))
    await asyncio.sleep(0.01) # Pastikan tugas sudah dimulai

    # Panggil shutdown
    await manajer.shutdown(timeout=1)
    waktu_selesai = time.time()

    # Verifikasi bahwa waktu shutdown setidaknya selama durasi tugas
    assert (waktu_selesai - waktu_mulai) >= durasi_tugas
    # Verifikasi bahwa tidak ada lagi tugas yang aktif
    assert manajer.pencatat_tugas.dapatkan_jumlah_aktif() == 0

@pytest.mark.asyncio
async def test_submit_task_during_shutdown_is_rejected():
    """Menguji bahwa tugas baru ditolak saat proses shutdown sedang berlangsung."""
    manajer = dapatkan_manajer_fox()

    async def tugas_apapun():
        pass

    # Mulai proses shutdown di latar belakang
    proses_shutdown = asyncio.create_task(manajer.shutdown())
    await asyncio.sleep(0.01) # Beri waktu agar flag shutdown aktif

    # Coba kirim tugas baru
    with pytest.raises(RuntimeError, match="ManajerFox sedang dalam proses shutdown"):
        await sfox("tugas_baru", tugas_apapun)

    await proses_shutdown
