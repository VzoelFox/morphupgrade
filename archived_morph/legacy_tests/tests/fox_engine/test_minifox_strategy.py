# tests/fox_engine/test_minifox_strategy.py
# PATCH-016G: Perbaiki tipe data di tes strategi untuk menangani bytes.
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from fox_engine.core import TugasFox, FoxMode, IOType
from fox_engine.strategies.minifox import MiniFoxStrategy

# Menandai semua tes di file ini sebagai asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def temp_file(tmp_path):
    """Fixture untuk membuat file sementara untuk pengujian I/O."""
    file_path = tmp_path / "test_file.txt"
    content = b"Selamat datang di pengujian MiniFox!"  # Gunakan bytes
    file_path.write_bytes(content)
    return file_path, content


# Perbarui impor untuk menyertakan API helper
from fox_engine.api import mfox_baca_file, mfox_tulis_file

async def test_minifox_routes_file_io_correctly(temp_file):
    """
    Memverifikasi bahwa MiniFoxStrategy merutekan tugas I/O FILE
    ke executor I/O dan tidak ke SimpleFox.
    """
    file_path, expected_content = temp_file

    # Atur manajer global untuk menggunakan MiniFoxStrategy secara langsung
    # untuk pengujian terisolasi
    strategy = MiniFoxStrategy(max_io_workers=1)

    # Mock manajer untuk mengembalikan strategi MiniFox yang kita kontrol
    with patch('fox_engine.api.dapatkan_manajer_fox') as mock_get_manager:
        mock_manager = AsyncMock()

        # side_effect harus berupa fungsi async agar dapat meng-await
        # pemanggilan strategi yang sebenarnya.
        async def async_side_effect(tugas):
            return await strategy.execute(tugas)
        mock_manager.kirim.side_effect = async_side_effect

        mock_get_manager.return_value = mock_manager

        # Patch SimpleFoxStrategy.execute untuk memastikan ia TIDAK dipanggil
        with patch('fox_engine.strategies.simplefox.SimpleFoxStrategy.execute', new_callable=AsyncMock) as mock_simplefox_execute:
            # Panggil API helper yang menggunakan pola baru
            # Tulis file terlebih dahulu menggunakan bytes
            await mfox_tulis_file("test_tulis", str(file_path), expected_content)
            hasil = await mfox_baca_file("test_baca", str(file_path))

            # Verifikasi konten file dibaca dengan benar
            assert hasil == expected_content

            # Verifikasi bahwa SimpleFox TIDAK digunakan
            mock_simplefox_execute.assert_not_called()

    await strategy.shutdown()


async def test_minifox_initializer_is_thread_safe():
    """
    Memverifikasi bahwa _initialize_executor hanya dipanggil sekali
    bahkan ketika banyak tugas mencoba untuk menginisialisasi secara bersamaan.
    Ini secara khusus menguji race condition.
    """
    strategy = MiniFoxStrategy(max_io_workers=2)

    # Mock JalurUtamaMultiArah untuk melacak berapa kali ia diinisialisasi
    with patch('fox_engine.strategies.minifox.JalurUtamaMultiArah') as mock_executor_class:

        # Buat banyak tugas yang semuanya akan memicu inisialisasi
        num_concurrent_tasks = 20

        # io_handler dummy untuk tugas
        def dummy_io_handler():
            # Mensimulasikan pekerjaan I/O yang sebenarnya
            return "sukses", 10

        tasks_to_run = []
        for i in range(num_concurrent_tasks):
            tugas = TugasFox(
                nama=f"race_test_{i}",
                mode=FoxMode.MINIFOX,
                jenis_operasi=IOType.FILE_BACA,
                io_handler=dummy_io_handler
            )
            # Langsung panggil execute, yang akan memicu _initialize_executor
            tasks_to_run.append(strategy.execute(tugas))

        # Jalankan semua tugas secara bersamaan
        await asyncio.gather(*tasks_to_run)

        # Verifikasi bahwa executor hanya diinisialisasi SEKALI
        mock_executor_class.assert_called_once()
        assert strategy._initialized is True

    await strategy.shutdown()


async def test_minifox_falls_back_to_simplefox_for_non_io_tasks():
    """
    Memverifikasi bahwa MiniFoxStrategy mengalihkan tugas non-I/O
    ke SimpleFoxStrategy.
    """
    strategy = MiniFoxStrategy(max_io_workers=1)

    # Coroutine sederhana non-I/O
    async def simple_coro():
        return "hasil sederhana"

    tugas = TugasFox(
        nama="test_non_io",
        coroutine_func=simple_coro,
        mode=FoxMode.MINIFOX,
        jenis_operasi=None  # Tidak ditandai sebagai I/O
    )

    # Kita patch SimpleFoxStrategy.execute untuk memastikan ia DIPANGGIL
    with patch('fox_engine.strategies.simplefox.SimpleFoxStrategy.execute', new_callable=AsyncMock) as mock_simplefox_execute:
        mock_simplefox_execute.return_value = "dari simplefox"

        hasil = await strategy.execute(tugas)

        # Verifikasi hasilnya adalah dari mock
        assert hasil == "dari simplefox"

        # Verifikasi bahwa SimpleFox DIPANGGIL
        mock_simplefox_execute.assert_called_once()

    await strategy.shutdown()
