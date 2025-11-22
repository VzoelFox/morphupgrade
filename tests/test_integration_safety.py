import pytest
import asyncio
from transisi.penerjemah import Penerjemah
from transisi.runtime_fox import RuntimeMORPHFox
from fox_engine.api import dapatkan_manajer_fox
from transisi.lx import Leksikal
from transisi.crusher import Pengurai

class MockFormatter:
    def format_runtime(self, error, stack, node=None):
        return f"ERROR: {str(error)}"

@pytest.mark.asyncio
async def test_circuit_breaker_stops_execution():
    # 1. Setup Runtime & Interpreter dengan MockFormatter
    formatter = MockFormatter()
    interpreter = Penerjemah(formatter=formatter)
    runtime = RuntimeMORPHFox(interpreter)

    # Pastikan integrasi berhasil
    assert interpreter.pemutus_sirkuit is not None
    assert interpreter.pemutus_sirkuit == runtime.manajer.pemutus_sirkuit

    # 2. Paksa Sirkuit Terbuka
    # Kita "trip" sirkuit dengan mencatat kegagalan berulang kali hingga ambang batas
    ambang = runtime.manajer.pemutus_sirkuit.ambang_kegagalan
    for _ in range(ambang + 1):
        runtime.manajer.pemutus_sirkuit.catat_kegagalan()

    assert not runtime.manajer.pemutus_sirkuit.bisa_eksekusi()

    # 3. Coba Eksekusi Kode Morph
    kode = 'tulis("Ini tidak boleh dicetak")'
    lexer = Leksikal(kode)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast = parser.urai()

    # 4. Verifikasi Kegagalan
    hasil = await interpreter.terjemahkan(ast)

    # Hasil harus berupa list error
    assert len(hasil) > 0
    error_msg = hasil[0]

    # Verifikasi pesan error dari MockFormatter
    assert "ERROR:" in error_msg
    assert "Pemutus Sirkuit" in error_msg
    assert "Sistem Kelebihan Beban" in error_msg
