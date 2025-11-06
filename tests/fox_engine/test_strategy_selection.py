# tests/fox_engine/test_strategy_selection.py
import pytest
from fox_engine.core import TugasFox, FoxMode
from fox_engine.manager import ManajerFox

@pytest.fixture
def manajer():
    """Fixture untuk instance ManajerFox."""
    return ManajerFox()

def test_pilih_mode_tanpa_estimasi(manajer):
    """Harus memilih SIMPLEFOX jika tidak ada estimasi durasi."""
    tugas = TugasFox("tes", lambda: None, FoxMode.AUTO, estimasi_durasi=None)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.SIMPLEFOX

def test_pilih_mode_tugas_sangat_singkat(manajer):
    """Harus memilih SIMPLEFOX untuk tugas < 0.1 detik."""
    tugas = TugasFox("tes", lambda: None, FoxMode.AUTO, estimasi_durasi=0.05)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.SIMPLEFOX

def test_pilih_mode_io_heavy(manajer):
    """Harus memilih MINIFOX untuk tugas dengan kata kunci I/O."""
    tugas = TugasFox("unduh_file_besar", lambda: None, FoxMode.AUTO, estimasi_durasi=0.3)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.MINIFOX

def test_pilih_mode_cpu_heavy(manajer):
    """Harus memilih THUNDERFOX untuk tugas > 0.5 detik."""
    tugas = TugasFox("kalkulasi_kompleks", lambda: None, FoxMode.AUTO, estimasi_durasi=0.7)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.THUNDERFOX

def test_pilih_mode_waterfox_default(manajer):
    """Harus memilih WATERFOX untuk beban kerja seimbang."""
    tugas = TugasFox("tugas_normal", lambda: None, FoxMode.AUTO, estimasi_durasi=0.3)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.WATERFOX

def test_pilih_mode_aot_dinonaktifkan(manajer):
    """Harus fallback ke WATERFOX jika AOT dinonaktifkan."""
    manajer.aktifkan_aot = False
    tugas = TugasFox("kalkulasi_kompleks", lambda: None, FoxMode.AUTO, estimasi_durasi=0.7)
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(tugas, manajer.aktifkan_aot, 0, 10) == FoxMode.WATERFOX

def test_pilih_mode_downgrade_saat_beban_tinggi(manajer):
    """Harus turun dari THUNDERFOX ke WATERFOX saat beban kerja tinggi."""
    tugas_cpu_heavy = TugasFox("kalkulasi_kompleks", lambda: None, FoxMode.AUTO, estimasi_durasi=0.7)

    # Skenario 1: Beban rendah, harus memilih THUNDERFOX
    jumlah_tugas_aktif_rendah = 5
    ambang_batas = 10
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(
        tugas_cpu_heavy, manajer.aktifkan_aot, jumlah_tugas_aktif_rendah, ambang_batas
    ) == FoxMode.THUNDERFOX

    # Skenario 2: Beban tinggi (sama dengan ambang batas), harus turun ke WATERFOX
    jumlah_tugas_aktif_tinggi = 10
    assert manajer.kontrol_kualitas.pilih_strategi_optimal(
        tugas_cpu_heavy, manajer.aktifkan_aot, jumlah_tugas_aktif_tinggi, ambang_batas
    ) == FoxMode.WATERFOX
