# tests/fox_engine/test_minifox_io.py
# PATCH-016E: Perbarui tes I/O untuk menangani bytes dan verifikasi bytes_processed.
# PATCH-016F: Perbaiki fixture untuk menangkap tugas yang selesai menggunakan patching.
# PATCH-018D: Tambahkan pengujian komprehensif untuk kolam koneksi jaringan.
import pytest
import pytest_asyncio
import os
import uuid
import aiohttp
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

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
from fox_engine.strategies import MiniFoxStrategy

# pytest.mark.asyncio digunakan untuk menandai test yang bersifat asynchronous
pytestmark = pytest.mark.asyncio

@pytest.fixture
def path_file_unik(tmp_path: Path) -> str:
    """Fixture untuk membuat path file unik di direktori temporer."""
    return str(tmp_path / f"test_file_{uuid.uuid4()}.txt")

@pytest_asyncio.fixture
async def manajer_fox_terisolasi():
    """
    Fixture untuk memastikan setiap test mendapatkan instance ManajerFox yang bersih
    dan melakukan shutdown setelah test selesai.
    """
    from fox_engine import api
    api._manajer_fox = None
    manajer = dapatkan_manajer_fox()
    yield manajer
    # Teardown: pastikan manajer dimatikan setelah test
    await manajer.shutdown()
    api._manajer_fox = None


async def test_tulis_dan_baca_file(path_file_unik: str, manajer_fox_terisolasi):
    """
    Memvalidasi fungsionalitas dasar tulis dan baca file menggunakan MiniFox.
    """
    konten_asli = b"Halo dari MiniFox! \xf0\x9f\xa6\x8a\nIni adalah baris kedua."
    byte_ditulis = await mfox_tulis_file("tugas-tulis-1", path=path_file_unik, konten=konten_asli)
    assert byte_ditulis == len(konten_asli)
    assert os.path.exists(path_file_unik)

    konten_dibaca = await mfox_baca_file("tugas-baca-1", path=path_file_unik)
    assert konten_dibaca == konten_asli

async def test_baca_file_tidak_ditemukan(path_file_unik: str, manajer_fox_terisolasi):
    """
    Memastikan FileTidakDitemukan dilempar saat mencoba membaca file yang tidak ada.
    """
    with pytest.raises(FileTidakDitemukan):
        await mfox_baca_file("tugas-baca-gagal", path=path_file_unik)

async def test_stream_file(path_file_unik: str, manajer_fox_terisolasi):
    """
    Memvalidasi fungsionalitas streaming file baris per baris.
    """
    baris_asli = [b"Ini adalah baris pertama.\n", b"Ini baris kedua.\n"]
    konten_penuh = b"".join(baris_asli)
    with open(path_file_unik, "wb") as f:
        f.write(konten_penuh)

    baris_diterima = []
    async for baris in mfox_stream_file("stream-tugas-1", path=path_file_unik):
        baris_diterima.append(baris)
    assert baris_diterima == baris_asli

async def test_jaringan_request_dan_penggunaan_ulang_sesi(manajer_fox_terisolasi: ManajerFox):
    """
    Memvalidasi bahwa API request jaringan menggunakan kolam koneksi dan menggunakan
    kembali sesi yang sama untuk beberapa panggilan.
    """
    sesi_yang_diterima = []
    hasil_palsu = {"status": "ok"}

    async def coro_jaringan(sesi: aiohttp.ClientSession):
        """Coroutine palsu yang menyimpan sesi yang diterimanya."""
        assert isinstance(sesi, aiohttp.ClientSession)
        sesi_yang_diterima.append(sesi)
        return hasil_palsu

    # Panggilan pertama
    hasil1 = await mfox_request_jaringan("api-call-1", coro=coro_jaringan)
    assert hasil1 == hasil_palsu
    assert len(sesi_yang_diterima) == 1

    # Panggilan kedua
    hasil2 = await mfox_request_jaringan("api-call-2", coro=coro_jaringan)
    assert hasil2 == hasil_palsu
    assert len(sesi_yang_diterima) == 2

    # Verifikasi bahwa objek sesi yang sama digunakan kembali
    assert sesi_yang_diterima[0] is sesi_yang_diterima[1]
    assert not sesi_yang_diterima[0].closed

async def test_kolam_koneksi_ditutup_saat_shutdown(manajer_fox_terisolasi: ManajerFox):
    """
    Memverifikasi bahwa sesi aiohttp ditutup dengan benar saat manajer dimatikan.
    """
    sesi_tercatat = None

    async def coro_jaringan(sesi: aiohttp.ClientSession):
        """Simpan sesi untuk inspeksi nanti."""
        nonlocal sesi_tercatat
        sesi_tercatat = sesi
        return "ok"

    await mfox_request_jaringan("api-call-shutdown-test", coro=coro_jaringan)

    # Pastikan sesi telah dibuat dan belum ditutup
    assert sesi_tercatat is not None
    assert isinstance(sesi_tercatat, aiohttp.ClientSession)
    assert not sesi_tercatat.closed

    # Matikan manajer
    await manajer_fox_terisolasi.shutdown()

    # Verifikasi bahwa sesi sekarang sudah ditutup
    assert sesi_tercatat.closed
