# tests/fox_engine/test_minifox_io.py
# PATCH-016E: Perbarui tes I/O untuk menangani bytes dan verifikasi bytes_processed.
# PATCH-016F: Perbaiki fixture untuk menangkap tugas yang selesai menggunakan patching.
import pytest
import pytest_asyncio
import os
import uuid
from pathlib import Path
from unittest.mock import patch

from unittest.mock import MagicMock
from fox_engine.api import (
    mfox_baca_file,
    mfox_tulis_file,
    mfox_stream_file,
    mfox_request_jaringan,
    dapatkan_manajer_fox
)
from fox_engine.core import MetrikFox, TugasFox, IOType
from fox_engine.errors import FileTidakDitemukan
from fox_engine.manager import ManajerFox

# pytest.mark.asyncio digunakan untuk menandai test yang bersifat asynchronous
pytestmark = pytest.mark.asyncio

@pytest.fixture
def path_file_unik(tmp_path: Path) -> str:
    """Fixture untuk membuat path file unik di direktori temporer."""
    return str(tmp_path / f"test_file_{uuid.uuid4()}.txt")

@pytest_asyncio.fixture(autouse=True)
async def manajer_fox_terisolasi():
    """
    Fixture untuk memastikan setiap test mendapatkan instance ManajerFox yang bersih
    dan melakukan shutdown setelah test selesai. Menggunakan patch untuk menangkap tugas.
    """
    from fox_engine import api
    api._manajer_fox = None
    manajer = dapatkan_manajer_fox()

    completed_tasks = []

    # Simpan metode asli
    original_method = manajer._catat_dan_perbarui_metrik_keberhasilan

    def patched_method(tugas: TugasFox, durasi: float):
        """Versi patched yang menyimpan tugas sebelum memanggil metode asli."""
        completed_tasks.append(tugas)
        original_method(tugas, durasi)

    # Terapkan patch
    with patch.object(manajer, '_catat_dan_perbarui_metrik_keberhasilan', side_effect=patched_method, autospec=True):
        # Berikan manajer yang telah dipatch ke tes
        manajer.completed_tasks = completed_tasks
        yield manajer

    # Teardown: pastikan manajer dimatikan setelah test
    await manajer.shutdown()
    api._manajer_fox = None


async def test_tulis_dan_baca_file(path_file_unik: str):
    """
    Memvalidasi fungsionalitas dasar tulis dan baca file menggunakan MiniFox.
    Sekarang menggunakan bytes.
    """
    konten_asli = b"Halo dari MiniFox! \xf0\x9f\xa6\x8a\nIni adalah baris kedua."

    # Tulis ke file
    byte_ditulis = await mfox_tulis_file(
        "tugas-tulis-1",
        path=path_file_unik,
        konten=konten_asli
    )

    assert byte_ditulis == len(konten_asli)
    assert os.path.exists(path_file_unik)

    # Baca dari file
    konten_dibaca = await mfox_baca_file("tugas-baca-1", path=path_file_unik)

    assert konten_dibaca == konten_asli

async def test_baca_file_tidak_ditemukan(path_file_unik: str):
    """
    Memastikan FileNotFoundError dilempar saat mencoba membaca file yang tidak ada.
    """
    path_tidak_ada = path_file_unik  # path ini belum dibuat

    with pytest.raises(FileTidakDitemukan):
        await mfox_baca_file("tugas-baca-gagal", path=path_tidak_ada)

async def test_metrik_diperbarui_setelah_operasi_io(path_file_unik: str, manajer_fox_terisolasi):
    """
    Memverifikasi bahwa metrik MiniFox (selesai, bytes_dibaca, bytes_ditulis)
    diperbarui dengan benar setelah operasi I/O.
    """
    konten = b"Data untuk pengujian metrik."
    byte_konten = len(konten)

    # Operasi tulis
    await mfox_tulis_file("tugas-tulis-metrik", path=path_file_unik, konten=konten)

    # Operasi baca
    await mfox_baca_file("tugas-baca-metrik", path=path_file_unik)

    metrik: MetrikFox = manajer_fox_terisolasi.dapatkan_metrik()

    assert metrik.tugas_mfox_selesai == 2
    assert metrik.tugas_mfox_gagal == 0
    assert metrik.bytes_ditulis == byte_konten
    assert metrik.bytes_dibaca == byte_konten
    assert metrik.avg_durasi_mfox > 0.0

async def test_metrik_kegagalan_io(manajer_fox_terisolasi):
    """
    Memverifikasi metrik kegagalan diperbarui saat operasi I/O gagal.
    """
    path_tidak_ada = "/jalur/palsu/yang/tidak/ada/file.txt"

    with pytest.raises(FileTidakDitemukan):
        await mfox_baca_file("tugas-baca-gagal-metrik", path=path_tidak_ada)

    metrik: MetrikFox = manajer_fox_terisolasi.dapatkan_metrik()

    assert metrik.tugas_mfox_selesai == 0
    assert metrik.tugas_mfox_gagal == 1
    assert metrik.tugas_gagal == 1
    assert metrik.bytes_dibaca == 0
    assert metrik.bytes_ditulis == 0

async def test_bytes_processed_diatur_dengan_benar(path_file_unik: str, manajer_fox_terisolasi: ManajerFox):
    """
    Memverifikasi bahwa atribut `bytes_processed` pada objek TugasFox diatur
    dengan benar setelah operasi I/O selesai.
    """
    konten = b"Konten untuk verifikasi bytes_processed."
    ukuran_konten = len(konten)

    # Tulis, lalu baca
    await mfox_tulis_file("tulis-untuk-verifikasi", path=path_file_unik, konten=konten)
    await mfox_baca_file("baca-untuk-verifikasi", path=path_file_unik)

    assert len(manajer_fox_terisolasi.completed_tasks) == 2

    tugas_tulis = next(t for t in manajer_fox_terisolasi.completed_tasks if t.nama == "tulis-untuk-verifikasi")
    tugas_baca = next(t for t in manajer_fox_terisolasi.completed_tasks if t.nama == "baca-untuk-verifikasi")

    assert tugas_tulis.bytes_processed == ukuran_konten
    assert tugas_baca.bytes_processed == ukuran_konten


async def test_stream_file(path_file_unik: str):
    """
    Memvalidasi fungsionalitas streaming file baris per baris.
    """
    baris_asli = [
        b"Ini adalah baris pertama.\n",
        b"Ini baris kedua.\n",
        b"Dan baris ketiga, tanpa baris baru."
    ]
    konten_penuh = b"".join(baris_asli)

    # Tulis file referensi
    with open(path_file_unik, "wb") as f:
        f.write(konten_penuh)

    baris_diterima = []
    # Lakukan streaming dan kumpulkan hasilnya
    async for baris in mfox_stream_file("stream-tugas-1", path=path_file_unik):
        baris_diterima.append(baris)

    # Hapus newline dari baris pertama dan kedua untuk perbandingan yang akurat
    # karena `stream_file_per_baris` mempertahankannya.
    assert baris_diterima[0].strip() == baris_asli[0].strip()
    assert baris_diterima[1].strip() == baris_asli[1].strip()
    assert baris_diterima[2] == baris_asli[2] # Baris terakhir tidak memiliki newline
    assert len(baris_diterima) == len(baris_asli)


async def test_jaringan_request(manajer_fox_terisolasi: ManajerFox):
    """
    Memvalidasi bahwa API request jaringan dapat menjalankan io_handler
    dan mengembalikan hasilnya dengan benar.
    """
    # Siapkan mock untuk io_handler
    hasil_palsu = {"status": "ok", "data": [1, 2, 3]}
    byte_diproses_palsu = 512

    mock_io_handler = MagicMock(return_value=(hasil_palsu, byte_diproses_palsu))

    # Jalankan tugas jaringan
    hasil_aktual = await mfox_request_jaringan(
        "api-call-1",
        io_handler=mock_io_handler
    )

    # Verifikasi
    mock_io_handler.assert_called_once()
    assert hasil_aktual == hasil_palsu

    # Verifikasi metrik
    metrik = manajer_fox_terisolasi.dapatkan_metrik()
    assert metrik.tugas_mfox_selesai == 1

    # Verifikasi bytes_processed di objek TugasFox
    assert len(manajer_fox_terisolasi.completed_tasks) == 1
    tugas_selesai = manajer_fox_terisolasi.completed_tasks[0]
    assert tugas_selesai.nama == "api-call-1"
    assert tugas_selesai.jenis_operasi == IOType.NETWORK
    # Catatan: byte yang diproses untuk jaringan mungkin tidak selalu relevan,
    # tetapi kita memverifikasi bahwa sistem dapat melacaknya.
    # Karena handler kita mengembalikan 0, kita periksa itu.
    assert tugas_selesai.bytes_processed == byte_diproses_palsu
