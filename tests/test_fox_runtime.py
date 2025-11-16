# tests/test_fox_integration_fase1.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from transisi.runtime_fox import RuntimeMORPHFox
from transisi.translator import Penerjemah, Fungsi
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi.error_utils import FormatterKesalahan

# Helper untuk membuat fungsi Morph dari source code
def buat_fungsi_morph(source: str, lingkungan: "Lingkungan" = None) -> Fungsi:
    if lingkungan is None:
        formatter = FormatterKesalahan(source)
        penerjemah = Penerjemah(formatter)
        lingkungan = penerjemah.lingkungan_global

    leksikal = Leksikal(source, "<test>")
    tokens, _ = leksikal.buat_token()
    parser = Pengurai(tokens)
    program = parser.urai()
    if program is None:
        pytest.fail("Parser gagal mengurai source code.")

    # Asumsi fungsi adalah statement pertama
    fungsi_decl = program.daftar_pernyataan[0]

    return Fungsi(fungsi_decl, lingkungan)

@pytest.fixture
def setup_runtime():
    """Fixture untuk inisialisasi runtime dan interpreter."""
    formatter = FormatterKesalahan("")
    interpreter = Penerjemah(formatter)
    runtime = RuntimeMORPHFox(interpreter)
    interpreter.runtime = runtime
    return runtime, interpreter

@pytest.mark.asyncio
async def test_lightweight_function_uses_sfox(setup_runtime):
    """Fungsi ringan (< 10 statements) harus dieksekusi via SimpleFox."""
    runtime, _ = setup_runtime

    fungsi_code = """
    fungsi tambah(a, b) maka
        kembalikan a + b
    akhir
    """
    fungsi = buat_fungsi_morph(fungsi_code)

    # Mock 'sfox' untuk memverifikasi bahwa ia dipanggil
    with patch('transisi.runtime_fox.sfox', new_callable=AsyncMock) as mock_sfox:
        mock_sfox.return_value = 5 # Kembalikan nilai yang diharapkan

        hasil = await runtime.execute_function(fungsi, [2, 3])

        assert hasil == 5
        mock_sfox.assert_called_once()

@pytest.mark.asyncio
async def test_heavy_function_uses_wfox(setup_runtime):
    """Fungsi berat (>= 10 statements) harus dieksekusi via WaterFox."""
    runtime, _ = setup_runtime

    fungsi_code = """
    fungsi hitung_rumit(x) maka
        biar a = x * 2
        biar b = a + 5
        biar c = b / 1.5
        biar d = c - x
        biar e = d * d
        biar f = e + 1
        biar g = f * 3
        biar h = g - 2
        biar i = h / 2
        kembalikan i
    akhir
    """
    fungsi = buat_fungsi_morph(fungsi_code)

    # Mock 'wfox' untuk memverifikasi bahwa ia dipanggil
    with patch('transisi.runtime_fox.wfox', new_callable=AsyncMock) as mock_wfox:
        mock_wfox.return_value = 147.0 # Nilai yang diharapkan untuk input 10

        hasil = await runtime.execute_function(fungsi, [10])

        assert hasil == 147.0
        mock_wfox.assert_called_once()

@pytest.mark.asyncio
async def test_module_loading_uses_mfox(setup_runtime, tmp_path):
    """Pemuatan modul harus menggunakan mfox_baca_file untuk I/O."""
    runtime, interpreter = setup_runtime

    # Buat file modul dummy
    module_content = "tetap PI = 3.14159"
    module_file = tmp_path / "modul_tes.fox"
    module_file.write_text(module_content, encoding='utf-8')

    # Mock 'mfox_baca_file'
    with patch('transisi.runtime_fox.mfox_baca_file', new_callable=AsyncMock) as mock_mfox:
        # Harus mengembalikan konten sebagai bytes
        mock_mfox.return_value = module_content.encode('utf-8')

        # Panggil metode yang memicu pemuatan modul
        exports = await runtime.load_module(str(module_file))

        assert "PI" in exports
        assert exports["PI"] == 3.14159
        mock_mfox.assert_called_once_with(
            nama=f"load_module_{str(module_file)}",
            path=str(module_file)
        )

@pytest.mark.asyncio
async def test_jit_compilation_is_triggered_for_hot_function(setup_runtime):
    """Verifikasi bahwa kompilasi JIT dipicu setelah fungsi dipanggil beberapa kali."""
    runtime, _ = setup_runtime
    runtime.JIT_THRESHOLD = 3  # Turunkan ambang batas untuk tes

    fungsi_code = """
    fungsi hot_func() maka
        kembalikan 42
    akhir
    """
    fungsi = buat_fungsi_morph(fungsi_code)
    nama_fungsi = fungsi.deklarasi.nama.nilai

    with patch('transisi.runtime_fox.tfox', new_callable=AsyncMock) as mock_tfox:
        mock_tfox.return_value = f"morphc_bytecode_untuk_{nama_fungsi}"

        # Panggilan pertama dan kedua (seharusnya tidak memicu)
        await runtime.execute_function(fungsi, [])
        await runtime.execute_function(fungsi, [])
        mock_tfox.assert_not_called()
        assert nama_fungsi not in runtime.compiler_cache

        # Panggilan ketiga (seharusnya memicu kompilasi)
        await runtime.execute_function(fungsi, [])

        # Beri sedikit waktu agar tugas latar belakang bisa berjalan
        await asyncio.sleep(0.01)

        mock_tfox.assert_called_once()
        # Verifikasi bahwa cache sekarang berisi bytecode palsu
        assert runtime.compiler_cache[nama_fungsi] == f"morphc_bytecode_untuk_{nama_fungsi}"

@pytest.mark.asyncio
async def test_compiled_function_executes_correctly(setup_runtime):
    """
    Verifikasi bahwa fungsi yang dikompilasi JIT menghasilkan output yang benar.
    Ini adalah tes end-to-end untuk alur kompilasi dan eksekusi.
    """
    runtime, _ = setup_runtime
    runtime.JIT_THRESHOLD = 1  # Langsung kompilasi pada panggilan pertama

    fungsi_code = """
    fungsi tambah_dan_kali(a, b) maka
        biar c = a + b
        kembalikan c * 2
    akhir
    """
    fungsi = buat_fungsi_morph(fungsi_code)

    # Panggilan pertama akan menjalankan interpreter dan memicu kompilasi JIT
    hasil_interpretasi = await runtime.execute_function(fungsi, [10, 5])
    assert hasil_interpretasi == 30 # (10 + 5) * 2

    # Beri waktu untuk kompilasi latar belakang selesai
    await asyncio.sleep(0.2)

    # Verifikasi bahwa kompilasi berhasil
    assert fungsi.deklarasi.nama.nilai in runtime.compiler_cache
    assert isinstance(runtime.compiler_cache[fungsi.deklarasi.nama.nilai], type((lambda: None).__code__))

    # Panggilan kedua seharusnya menjalankan bytecode yang sudah dikompilasi
    hasil_kompilasi = await runtime.execute_function(fungsi, [10, 5])
    assert hasil_kompilasi == 30

@pytest.mark.asyncio
async def test_jit_factorial_function_with_loop_and_if(setup_runtime):
    """Tes end-to-end JIT dengan fungsi faktorial yang menggunakan loop dan if."""
    runtime, _ = setup_runtime
    runtime.JIT_THRESHOLD = 1

    fungsi_code = """
    fungsi faktorial(n) maka
        biar hasil = 1
        selama n > 1 maka
            ubah hasil = hasil * n
            ubah n = n - 1
        akhir
        kembalikan hasil
    akhir
    """
    fungsi = buat_fungsi_morph(fungsi_code)

    # Panggilan pertama (interpretasi + JIT)
    hasil1 = await runtime.execute_function(fungsi, [5])
    assert hasil1 == 120  # 5! = 120

    await asyncio.sleep(0.2) # Tunggu kompilasi

    # Panggilan kedua (terkompilasi)
    hasil2 = await runtime.execute_function(fungsi, [6])
    assert hasil2 == 720 # 6! = 720

@pytest.mark.asyncio
async def test_jit_ffi_function_executes_correctly(setup_runtime):
    """Tes end-to-end JIT untuk fungsi yang memanggil FFI."""
    runtime, interpreter = setup_runtime
    runtime.JIT_THRESHOLD = 1

    # 1. Siapkan lingkungan dengan alias FFI
    ffi_lingkungan = interpreter.lingkungan_global
    # Pastikan ada baris baru di akhir untuk parser
    pinjam_stmt = "pinjam 'math' sebagai math_py\n"
    leksikal = Leksikal(pinjam_stmt, "<test-ffi>")
    tokens, _ = leksikal.buat_token()
    parser = Pengurai(tokens)
    program_pinjam = parser.urai()
    if program_pinjam is None:
        pytest.fail("Parser gagal mengurai pernyataan 'pinjam'.")
    await interpreter.terjemahkan(program_pinjam, "<test-ffi>")

    # 2. Definisikan fungsi Morph yang menggunakan alias FFI
    fungsi_code = """
    fungsi hitung_akar(x) maka
        kembalikan math_py.sqrt(x)
    akhir
    """
    # Teruskan lingkungan yang sudah berisi 'math_py'
    fungsi = buat_fungsi_morph(fungsi_code, ffi_lingkungan)

    # 3. Jalankan dan verifikasi
    # Panggilan pertama (interpretasi + JIT)
    hasil1 = await runtime.execute_function(fungsi, [16])
    assert hasil1 == 4.0

    await asyncio.sleep(0.2) # Tunggu kompilasi

    # Panggilan kedua (terkompilasi)
    hasil2 = await runtime.execute_function(fungsi, [25])
    assert hasil2 == 5.0
