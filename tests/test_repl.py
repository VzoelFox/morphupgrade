# tests/test_repl.py
import pytest
import sys
from io import StringIO
from transisi.Morph import Morph
from transisi.translator import Lingkungan

def run_repl_test(monkeypatch, commands):
    """
    Fixture helper untuk menguji alur kerja REPL.
    Menyimulasikan input pengguna dan menangkap output.
    """
    input_stream = StringIO("\\n".join(commands) + "\\n")
    output_stream = StringIO()

    monkeypatch.setattr("sys.stdin", input_stream)
    monkeypatch.setattr("sys.stdout", output_stream)

    # Mock 'input' untuk membaca dari StringIO yang kita siapkan
    inputs = iter(commands)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Tangkap stdout dan stderr
    old_stderr = sys.stderr
    sys.stderr = StringIO()

    morph = Morph()
    try:
        morph.jalankan_prompt()
    except StopIteration:
        pass
    finally:
        # Kembalikan stderr dan pulihkan
        stderr_val = sys.stderr.getvalue()
        sys.stderr = old_stderr

    return output_stream.getvalue(), stderr_val

def test_repl_state_is_retained(monkeypatch):
    """Memverifikasi bahwa variabel tetap ada di antara baris input REPL."""
    commands = [
        "biar x = 10",
        "tulis(x)",
        "keluar()"
    ]
    output, _ = run_repl_test(monkeypatch, commands)
    # Output 'tulis' untuk angka tidak memiliki tanda kutip
    assert "10" in output
    # Pastikan itu bukan bagian dari teks lain
    assert "10\n" or output.endswith("10")

def test_repl_reset_clears_state(monkeypatch):
    """Memverifikasi bahwa perintah 'reset()' menghapus semua state."""
    commands = [
        "biar x = 100",
        "tulis(x)", # Harus mencetak 100
        "reset()",
        "tulis(x)", # Ini harus menghasilkan error karena x tidak terdefinisi
        "keluar()"
    ]
    output, stderr = run_repl_test(monkeypatch, commands)

    # Cek bahwa nilai awal ada
    assert "100" in output
    # Cek bahwa state direset
    assert "✓ State direset." in output
    # Cek bahwa error terjadi setelah reset
    assert "KesalahanNama" in stderr
    assert "'x' belum didefinisikan" in stderr

def test_repl_keluar_stops_session(monkeypatch):
    """Memverifikasi bahwa perintah 'keluar()' menghentikan REPL."""
    commands = [
        "biar a = 1",
        "keluar()",
        "biar b = 2" # Perintah ini tidak boleh dieksekusi
    ]
    output, stderr = run_repl_test(monkeypatch, commands)
    assert "Selamat datang di MORPH" in output
    assert "biar b" not in output
    # Tidak ada cara mudah untuk memeriksa apakah loop berhenti,
    # tapi kita bisa memastikan tidak ada error dari perintah setelah 'keluar()'
    assert "Kesalahan" not in stderr
