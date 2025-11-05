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
    assert manajer._pilih_mode(tugas) == FoxMode.SIMPLEFOX

def test_pilih_mode_tugas_sangat_singkat(manajer):
    """Harus memilih SIMPLEFOX untuk tugas < 0.1 detik."""
    tugas = TugasFox("tes", lambda: None, FoxMode.AUTO, estimasi_durasi=0.05)
    assert manajer._pilih_mode(tugas) == FoxMode.SIMPLEFOX

def test_pilih_mode_io_heavy(manajer):
    """Harus memilih MINIFOX untuk tugas dengan kata kunci I/O."""
    tugas = TugasFox("unduh_file_besar", lambda: None, FoxMode.AUTO, estimasi_durasi=0.3)
    assert manajer._pilih_mode(tugas) == FoxMode.MINIFOX

def test_pilih_mode_cpu_heavy(manajer):
    """Harus memilih THUNDERFOX untuk tugas > 0.5 detik."""
    tugas = TugasFox("kalkulasi_kompleks", lambda: None, FoxMode.AUTO, estimasi_durasi=0.7)
    assert manajer._pilih_mode(tugas) == FoxMode.THUNDERFOX

def test_pilih_mode_waterfox_default(manajer):
    """Harus memilih WATERFOX untuk beban kerja seimbang."""
    tugas = TugasFox("tugas_normal", lambda: None, FoxMode.AUTO, estimasi_durasi=0.3)
    assert manajer._pilih_mode(tugas) == FoxMode.WATERFOX

def test_pilih_mode_aot_dinonaktifkan(manajer):
    """Harus fallback ke WATERFOX jika AOT dinonaktifkan."""
    manajer.aktifkan_aot = False
    tugas = TugasFox("kalkulasi_kompleks", lambda: None, FoxMode.AUTO, estimasi_durasi=0.7)
    assert manajer._pilih_mode(tugas) == FoxMode.WATERFOX
