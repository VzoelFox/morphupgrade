# tests/fox_engine/test_operasi_file.py
# PATCH-016C: Tambahkan unit test untuk modul operasi_file.
import os
import pytest
from fox_engine.internal.operasi_file import (
    baca_file_dengan_buffer,
    tulis_file_dengan_buffer,
    stream_file_per_baris,
    UKURAN_BUFFER_DEFAULT
)

@pytest.fixture
def file_test(tmp_path):
    """Fixture untuk membuat file teks sementara."""
    file_path = tmp_path / "test.txt"
    konten = b"baris 1\nbaris 2\nbaris ketiga"
    file_path.write_bytes(konten)
    return file_path, konten

def test_baca_file_dengan_buffer_berhasil(file_test):
    """Memastikan file dapat dibaca dengan benar menggunakan buffer."""
    file_path, konten_asli = file_test
    konten_dibaca, byte_dibaca = baca_file_dengan_buffer(str(file_path))

    assert konten_dibaca == konten_asli
    assert byte_dibaca == len(konten_asli)

def test_baca_file_dengan_buffer_ukuran_kecil(file_test):
    """Menguji pembacaan dengan ukuran buffer yang lebih kecil dari ukuran file."""
    file_path, konten_asli = file_test
    # Buffer kecil akan memaksa beberapa kali pembacaan
    konten_dibaca, byte_dibaca = baca_file_dengan_buffer(str(file_path), ukuran_buffer=5)

    assert konten_dibaca == konten_asli
    assert byte_dibaca == len(konten_asli)

def test_baca_file_tidak_ditemukan():
    """Memastikan FileNotFoundError dimunculkan saat file tidak ada."""
    with pytest.raises(FileNotFoundError):
        baca_file_dengan_buffer("path/yang/tidak/ada.txt")

def test_tulis_dan_baca_file_dengan_buffer(tmp_path):
    """Menguji penulisan dan pembacaan data biner."""
    file_path = tmp_path / "output.bin"
    data_asli = os.urandom(UKURAN_BUFFER_DEFAULT * 3 + 100)  # Data lebih besar dari buffer

    _, byte_ditulis = tulis_file_dengan_buffer(str(file_path), data_asli)
    assert byte_ditulis == len(data_asli)

    data_dibaca, byte_dibaca = baca_file_dengan_buffer(str(file_path))
    assert byte_dibaca == len(data_asli)
    assert data_dibaca == data_asli

def test_tulis_file_dengan_buffer_kosong(tmp_path):
    """Menguji penulisan data kosong ke file."""
    file_path = tmp_path / "output_kosong.bin"
    data_asli = b""

    _, byte_ditulis = tulis_file_dengan_buffer(str(file_path), data_asli)
    assert byte_ditulis == 0

    data_dibaca, _ = baca_file_dengan_buffer(str(file_path))
    assert data_dibaca == b""

def test_stream_file_per_baris_berhasil(file_test):
    """Memastikan streaming per baris bekerja dengan benar."""
    file_path, konten_asli = file_test
    baris_asli = konten_asli.splitlines(keepends=True)

    hasil_stream = list(stream_file_per_baris(str(file_path)))

    assert len(hasil_stream) == len(baris_asli)
    for (baris_stream, byte_stream), baris_kontrol in zip(hasil_stream, baris_asli):
        assert baris_stream == baris_kontrol
        assert byte_stream == len(baris_kontrol)

def test_stream_file_kosong(tmp_path):
    """Memastikan streaming pada file kosong tidak menghasilkan apa-apa."""
    file_path = tmp_path / "kosong.txt"
    file_path.write_bytes(b"")

    hasil_stream = list(stream_file_per_baris(str(file_path)))
    assert len(hasil_stream) == 0

def test_stream_file_tidak_ditemukan():
    """Memastikan FileNotFoundError dimunculkan saat streaming file yang tidak ada."""
    with pytest.raises(FileNotFoundError):
        # Kita perlu mengkonsumsi generator untuk memicu eksekusi
        list(stream_file_per_baris("path/yang/tidak/ada.txt"))
