# tests/fox_engine/test_manajer_intensif.py
import pytest
import asyncio
import fox_engine.api
from fox_engine.api import dapatkan_manajer_fox
from fox_engine.core import TugasFox, FoxMode

async def tugas_sederhana(durasi):
    """Tugas sederhana yang tidur selama durasi tertentu."""
    await asyncio.sleep(durasi)
    return durasi

@pytest.fixture
def manajer_baru():
    """Fixture untuk memastikan setiap tes mendapatkan instance ManajerFox yang baru."""
    # Reset singleton instance in the api module
    fox_engine.api._manajer_global = None
    return dapatkan_manajer_fox()

@pytest.mark.asyncio
async def test_pemutus_sirkuit_dengan_beban_normal(manajer_baru):
    """
    Menguji bahwa pemutus sirkuit TIDAK terbuka di bawah beban kerja normal dan berkelanjutan.
    Ini bertujuan untuk memeriksa apakah ambang batasnya terlalu rendah.
    """
    manajer_baru.pemutus_sirkuit.ambang_kegagalan = 5
    manajer_baru.pemutus_sirkuit.batas_waktu_reset = 1

    tasks = [manajer_baru.kirim(TugasFox(
        nama=f"tugas-{i}",
        mode=FoxMode.SIMPLEFOX,
        coroutine_func=tugas_sederhana,
        coroutine_args=(0.01,)
    )) for i in range(10)]

    try:
        hasil = await asyncio.gather(*tasks)
        assert len(hasil) == 10, "Tidak semua tugas berhasil diselesaikan"
    except RuntimeError as e:
        pytest.fail(f"Pemutus sirkuit seharusnya tidak terbuka di bawah beban normal: {e}")

    assert manajer_baru.pemutus_sirkuit._status == "TERTUTUP", "Pemutus sirkuit dilaporkan terbuka padahal seharusnya tidak"

@pytest.mark.asyncio
async def test_pemutus_sirkuit_terbuka_saat_kelebihan_beban(manajer_baru):
    """
    Menguji bahwa pemutus sirkuit terbuka ketika sistem dibanjiri dengan tugas
    yang menyebabkan kegagalan (misalnya, timeout atau error internal).
    """
    # Atur timeout tugas yang sangat singkat untuk mensimulasikan kegagalan
    manajer_baru.pemutus_sirkuit.ambang_kegagalan = 3
    manajer_baru.pemutus_sirkuit.batas_waktu_reset = 5

    async def tugas_gagal():
        await asyncio.sleep(0.1) # Lebih lama dari timeout individu
        raise asyncio.TimeoutError("Tugas sengaja dibuat timeout")

    # Kirim beberapa tugas yang dijamin gagal
    gagal_tasks = [manajer_baru.kirim(TugasFox(
        nama=f"gagal-{i}",
        mode=FoxMode.SIMPLEFOX,
        coroutine_func=tugas_gagal,
        batas_waktu=0.01
    )) for i in range(4)]

    # Kita harapkan beberapa tugas pertama gagal karena timeout, lalu sisanya karena pemutus sirkuit
    hasil = await asyncio.gather(*gagal_tasks, return_exceptions=True)

    runtime_errors = [res for res in hasil if isinstance(res, RuntimeError) and "Pemutus sirkuit terbuka" in str(res)]
    timeout_errors = [res for res in hasil if isinstance(res, asyncio.TimeoutError)]

    assert len(runtime_errors) > 0, "Pemutus sirkuit tidak terbuka dan menolak tugas"
    assert len(timeout_errors) > 0, "Tugas tidak gagal karena timeout seperti yang diharapkan"

    assert manajer_baru.pemutus_sirkuit._status == "TERBUKA", "Status pemutus sirkuit internal tidak TERBUKA"
    assert manajer_baru.pemutus_sirkuit.jumlah_kegagalan >= 3, "Jumlah kegagalan pada pemutus sirkuit tidak tercatat dengan benar"

@pytest.mark.asyncio
async def test_akurasi_laporan_metrik(manajer_baru):
    """
    Menguji akurasi laporan metrik setelah menjalankan beberapa tugas yang berhasil.
    """
    manajer_baru.pemutus_sirkuit.ambang_kegagalan = 5
    manajer_baru.pemutus_sirkuit.batas_waktu_reset = 1

    # Jalankan beberapa tugas dengan durasi yang diketahui
    tasks = [
        manajer_baru.kirim(TugasFox(nama="tugas-0.05", mode=FoxMode.SIMPLEFOX, coroutine_func=tugas_sederhana, coroutine_args=(0.05,))),
        manajer_baru.kirim(TugasFox(nama="tugas-0.10", mode=FoxMode.SIMPLEFOX, coroutine_func=tugas_sederhana, coroutine_args=(0.10,))),
        manajer_baru.kirim(TugasFox(nama="tugas-0.15", mode=FoxMode.SIMPLEFOX, coroutine_func=tugas_sederhana, coroutine_args=(0.15,)))
    ]
    await asyncio.gather(*tasks)

    # Beri sedikit waktu agar metrik sempat diproses
    await asyncio.sleep(0.1)

    metrik = manajer_baru.dapatkan_metrik()

    total_selesai = metrik.tugas_sfox_selesai + metrik.tugas_wfox_selesai + metrik.tugas_tfox_selesai + metrik.tugas_mfox_selesai
    assert total_selesai == 3, "Jumlah tugas selesai tidak akurat"
    assert metrik.tugas_gagal == 0, "Jumlah tugas gagal tidak akurat"

    # Periksa apakah waktu eksekusi rata-rata berada dalam rentang yang wajar
    # Rata-rata sebenarnya: (0.05 + 0.10 + 0.15) / 3 = 0.1
    avg_waktu_eksekusi = metrik.avg_durasi_sfox
    assert 0.09 < avg_waktu_eksekusi < 0.15, f"Waktu eksekusi rata-rata ({avg_waktu_eksekusi}s) di luar ekspektasi"
