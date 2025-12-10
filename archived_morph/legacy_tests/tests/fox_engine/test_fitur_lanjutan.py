# tests/fox_engine/test_fitur_lanjutan.py
import pytest
import asyncio
import logging
from fox_engine.api import dapatkan_manajer_fox, tfox, sfox
from fox_engine.core import TugasFox, FoxMode

@pytest.fixture
def manajer_baru():
    """Fixture untuk memastikan setiap tes mendapatkan instance ManajerFox yang baru."""
    import fox_engine.api
    fox_engine.api._manajer_global = None
    return dapatkan_manajer_fox()

class MockError(Exception):
    """Exception kustom untuk pengujian."""
    pass

async def tugas_yang_selalu_gagal(*args, **kwargs):
    """Tugas sederhana yang selalu melempar error."""
    raise MockError("Tugas ini sengaja dibuat gagal")

@pytest.mark.asyncio
async def test_logika_fallback_cerdas(manajer_baru, caplog):
    """
    Memverifikasi bahwa tugas yang gagal akan melalui rantai fallback:
    Mode Asli -> mfox -> sfox.
    """
    manajer_baru.pemutus_sirkuit.ambang_kegagalan = 99 # Nonaktifkan pemutus sirkuit untuk tes ini

    caplog.set_level(logging.INFO)

    # Buat instance tugas secara manual untuk memeriksa modifikasi state
    tugas = TugasFox("tugas_gagal_fallback", FoxMode.THUNDERFOX, tugas_yang_selalu_gagal)

    with pytest.raises(MockError):
        await manajer_baru.kirim(tugas)

    # Verifikasi bahwa mode tugas telah diubah selama proses fallback
    assert tugas.mode == FoxMode.SIMPLEFOX

    log_text = caplog.text
    # Cukup verifikasi bahwa log kritis terakhir ada
    assert "Semua fallback gagal untuk tugas 'tugas_gagal_fallback'" in log_text

@pytest.mark.asyncio
async def test_penundaan_dan_eksekusi_sekuensial(manajer_baru):
    """
    Memverifikasi bahwa `penundaan_mulai` dan `jalankan_segera=False` berfungsi.
    """
    waktu_selesai = []

    async def tugas_panjang():
        await asyncio.sleep(0.2)
        waktu_selesai.append(("panjang", asyncio.get_event_loop().time()))

    async def tugas_cepat():
        await asyncio.sleep(0.01)
        waktu_selesai.append(("cepat", asyncio.get_event_loop().time()))

    # Kirim tugas panjang pertama dan tunggu hingga selesai.
    await sfox("tugas_panjang", tugas_panjang)

    # Kirim tugas cepat kedua. Karena `jalankan_segera=False`, ia harus
    # dieksekusi setelah tugas panjang, meskipun dikirim setelahnya.
    await sfox(
        "tugas_cepat_sekuensial",
        tugas_cepat,
        jalankan_segera=False
    )

    assert len(waktu_selesai) == 2
    # Pastikan tugas panjang selesai lebih dulu
    assert waktu_selesai[0][0] == "panjang"
    assert waktu_selesai[1][0] == "cepat"

    # Verifikasi bahwa waktu selesai tugas cepat > waktu selesai tugas panjang
    waktu_selesai_panjang = waktu_selesai[0][1]
    waktu_selesai_cepat = waktu_selesai[1][1]
    assert waktu_selesai_cepat > waktu_selesai_panjang

@pytest.mark.asyncio
async def test_monitor_kesehatan_melaporkan_metrik_baru(manajer_baru, capsys):
    """
    Memverifikasi bahwa `cetak_laporan_metrik` menyertakan metrik kesehatan baru.
    """
    async def tugas_sample():
        await asyncio.sleep(0.01)

    await sfox("tugas_sample_1", tugas_sample)
    await sfox("tugas_sample_2", tugas_sample, penundaan_mulai=0.05)

    manajer_baru.cetak_laporan_metrik()

    captured = capsys.readouterr()
    output = captured.out

    assert "--- Kesehatan & Beban Sistem ---" in output
    assert "Avg. Waktu Tunggu" in output
    assert "Status Pemutus      : TERTUTUP" in output

    # Verifikasi bahwa waktu tunggu tercatat (lebih besar dari 0)
    import re
    match = re.search(r"Avg\. Waktu Tunggu\s+:\s+(\d+\.\d+)\s+ms", output)
    assert match is not None, "Format waktu tunggu tidak ditemukan di laporan"
    waktu_tunggu = float(match.group(1))
    assert waktu_tunggu > 0, "Waktu tunggu rata-rata seharusnya lebih besar dari nol"
