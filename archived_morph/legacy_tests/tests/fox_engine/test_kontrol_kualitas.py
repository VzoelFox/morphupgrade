# tests/fox_engine/test_kontrol_kualitas.py
import pytest
from fox_engine.core import TugasFox, FoxMode, IOType
from fox_engine.kontrol_kualitas import KontrolKualitasFox

@pytest.fixture
def kontrol_kualitas():
    """Fixture untuk instance KontrolKualitasFox."""
    return KontrolKualitasFox()

def test_validasi_tugas_valid(kontrol_kualitas):
    """Harus lolos validasi untuk tugas yang dikonfigurasi dengan benar."""
    tugas = TugasFox(nama="tugas_valid", mode=FoxMode.AUTO, coroutine_func=lambda: None)
    try:
        kontrol_kualitas.validasi_tugas(tugas)
    except ValueError:
        pytest.fail("validasi_tugas memunculkan ValueError yang tidak terduga.")

def test_validasi_estimasi_durasi_negatif(kontrol_kualitas):
    """Harus memunculkan ValueError untuk estimasi_durasi negatif."""
    tugas = TugasFox(nama="tugas_invalid", mode=FoxMode.AUTO, coroutine_func=lambda: None, estimasi_durasi=-1.0)
    with pytest.raises(ValueError, match="'estimasi_durasi' negatif"):
        kontrol_kualitas.validasi_tugas(tugas)

def test_validasi_batas_waktu_negatif(kontrol_kualitas):
    """Harus memunculkan ValueError untuk batas_waktu negatif."""
    tugas = TugasFox(nama="tugas_invalid", mode=FoxMode.AUTO, coroutine_func=lambda: None, batas_waktu=-1.0)
    with pytest.raises(ValueError, match="'batas_waktu' negatif"):
        kontrol_kualitas.validasi_tugas(tugas)

@pytest.mark.parametrize("prioritas", [0, 11, -1])
def test_validasi_prioritas_di_luar_rentang(kontrol_kualitas, prioritas):
    """Harus memunculkan ValueError untuk prioritas di luar rentang 1-10."""
    tugas = TugasFox(nama="tugas_invalid", mode=FoxMode.AUTO, coroutine_func=lambda: None, prioritas=prioritas)
    with pytest.raises(ValueError, match="'prioritas' di luar rentang"):
        kontrol_kualitas.validasi_tugas(tugas)

def test_validasi_tugas_file_tanpa_io_handler(kontrol_kualitas):
    """Harus memunculkan ValueError untuk tugas FILE tanpa io_handler."""
    tugas = TugasFox(nama="tugas_file_invalid", mode=FoxMode.AUTO, coroutine_func=lambda: None, jenis_operasi=IOType.FILE_GENERIC)
    with pytest.raises(ValueError, match="'io_handler' yang valid dan callable"):
        kontrol_kualitas.validasi_tugas(tugas)

async def dummy_coroutine():
    pass

def non_async_function():
    pass

def test_validasi_tugas_network_dengan_coroutine_salah(kontrol_kualitas):
    """Harus memunculkan ValueError untuk tugas NETWORK dengan coroutine non-async."""
    tugas = TugasFox(nama="tugas_network_invalid", mode=FoxMode.AUTO, coroutine_func=non_async_function, jenis_operasi=IOType.NETWORK_GENERIC)
    with pytest.raises(ValueError, match="'coroutine_func' yang merupakan fungsi async"):
        kontrol_kualitas.validasi_tugas(tugas)

def test_validasi_tugas_network_valid(kontrol_kualitas):
    """Tugas NETWORK dengan coroutine yang valid harus lolos."""
    tugas = TugasFox(nama="tugas_network_valid", mode=FoxMode.AUTO, coroutine_func=dummy_coroutine, jenis_operasi=IOType.NETWORK_GENERIC)
    try:
        kontrol_kualitas.validasi_tugas(tugas)
    except ValueError:
        pytest.fail("validasi_tugas memunculkan ValueError yang tidak terduga untuk tugas network yang valid.")
