# tests/fox_engine/test_minifox_io.py
import pytest
import pytest_asyncio
import asyncio
import os
import uuid
from pathlib import Path

from fox_engine.api import mfox_baca_file, mfox_tulis_file, dapatkan_manajer_fox
from fox_engine.core import MetrikFox

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
    dan melakukan shutdown setelah test selesai.
    """
    # Menggunakan implementasi internal untuk mereset manajer global
    # Ini penting untuk isolasi test, terutama untuk metrik.
    from fox_engine import api
    api._manajer_fox = None
    manajer = dapatkan_manajer_fox()

    yield manajer

    # Teardown: pastikan manajer dimatikan setelah test
    await manajer.shutdown()
    api._manajer_fox = None


async def test_tulis_dan_baca_file(path_file_unik: str):
    """
    Memvalidasi fungsionalitas dasar tulis dan baca file menggunakan MiniFox.
    """
    konten_asli = "Halo dari MiniFox! 🦊\nIni adalah baris kedua."

    # Tulis ke file
    byte_ditulis = await mfox_tulis_file(
        "tugas-tulis-1",
        path=path_file_unik,
        konten=konten_asli
    )

    assert byte_ditulis == len(konten_asli.encode('utf-8'))
    assert os.path.exists(path_file_unik)

    # Baca dari file
    konten_dibaca = await mfox_baca_file("tugas-baca-1", path=path_file_unik)

    assert konten_dibaca == konten_asli

async def test_baca_file_tidak_ditemukan(path_file_unik: str):
    """
    Memastikan FileNotFoundError dilempar saat mencoba membaca file yang tidak ada.
    """
    path_tidak_ada = path_file_unik  # path ini belum dibuat

    with pytest.raises(FileNotFoundError):
        await mfox_baca_file("tugas-baca-gagal", path=path_tidak_ada)

async def test_metrik_diperbarui_setelah_operasi_io(path_file_unik: str, manajer_fox_terisolasi):
    """
    Memverifikasi bahwa metrik MiniFox (selesai, bytes_dibaca, bytes_ditulis)
    diperbarui dengan benar setelah operasi I/O.
    """
    konten = "Data untuk pengujian metrik."
    byte_konten = len(konten.encode('utf-8'))

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

    with pytest.raises(FileNotFoundError):
        await mfox_baca_file("tugas-baca-gagal-metrik", path=path_tidak_ada)

    metrik: MetrikFox = manajer_fox_terisolasi.dapatkan_metrik()

    assert metrik.tugas_mfox_selesai == 0
    assert metrik.tugas_mfox_gagal == 1
    assert metrik.tugas_gagal == 1
    assert metrik.bytes_dibaca == 0
    assert metrik.bytes_ditulis == 0
