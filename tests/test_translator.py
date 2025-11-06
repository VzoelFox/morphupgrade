# tests/test_translator.py
import pytest
from morph_engine.lx import Leksikal
from morph_engine.crusher import Pengurai
from morph_engine.translator import Translator, KesalahanRuntime

@pytest.fixture
def run_morph():
    def _run_morph(source_code):
        lexer = Leksikal(source_code)
        tokens = lexer.buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()
        if parser.daftar_kesalahan:
            # For simplicity in testing, raise the first parser error
            raise parser.daftar_kesalahan[0]

        # Capture stdout to check 'tulis' output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            interpreter = Translator(ast)
            interpreter.interpretasi()

        return f.getvalue().strip()

    return _run_morph

# ============================================================================
# 1. Arithmetic Operator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.interpreter
class TestArithmeticOperators:

    def test_modulo_operator(self, run_morph):
        """Test the modulo operator (%) for basic cases."""
        result = run_morph("tulis(10 % 3)")
        assert result == "1"

        result = run_morph("tulis(10 % 2)")
        assert result == "0"

    def test_exponent_operator(self, run_morph):
        """Test the exponentiation operator (^) for basic cases."""
        result = run_morph("tulis(2 ^ 8)")
        assert result == "256"

        result = run_morph("tulis(3 ^ 3)")
        assert result == "27"

    def test_precedence(self, run_morph):
        """Test operator precedence: ^ > */% > +-"""
        result = run_morph("tulis(2 + 3 * 4)")
        assert result == "14"

        result = run_morph("tulis(2 * 3 ^ 2)") # 2 * 9
        assert result == "18"

        result = run_morph("tulis(10 % 3 * 2)") # (10 % 3) * 2
        assert result == "2"

    def test_right_associativity_for_exponent(self, run_morph):
        """Test right-associativity for the exponent operator."""
        # Should be calculated as 2 ^ (3 ^ 2) = 2 ^ 9 = 512
        result = run_morph("tulis(2 ^ 3 ^ 2)")
        assert result == "512"

# ============================================================================
# 2. Error Handling Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.interpreter
@pytest.mark.errors
class TestArithmeticErrors:

    def test_modulo_by_zero(self, run_morph):
        """Test that modulo by zero raises a runtime error."""
        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph("tulis(10 % 0)")
        assert "misteri" in str(exc_info.value)

    def test_division_by_zero(self, run_morph):
        """Test that division by zero raises a runtime error."""
        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph("tulis(10 / 0)")
        assert "tak terhingga" in str(exc_info.value)

    def test_type_error_for_arithmetic(self, run_morph):
        """Test that arithmetic on non-numbers raises a runtime error."""
        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph('tulis("a" + 5)')
        assert "Dua dunia tak dapat menyatu" in str(exc_info.value)

        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph("tulis(benar ^ 2)")
        assert "menari dalam tarian" in str(exc_info.value)

# ============================================================================
# 3. Execution Limits Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.interpreter
class TestExecutionLimits:
    """Tes untuk batas eksekusi (waktu, rekursi)."""

    def test_execution_timeout(self, monkeypatch):
        """
        BLOCKER-2 VALIDATION:
        Memastikan interpreter berhenti jika waktu eksekusi terlampaui.
        Menggunakan rekursi tak terbatas untuk mensimulasikan proses yang berjalan lama.
        """
        # Atur batas waktu ke 0 untuk memicu kesalahan pada panggilan pertama.
        # Ini secara definitif membuktikan bahwa mekanisme pengecekan waktu aktif.
        monkeypatch.setattr("morph_engine.translator.MAX_EXECUTION_TIME", 0.0)
        # Naikkan batas rekursi untuk memastikan kesalahan yang terjadi adalah
        # timeout, bukan recursion error.
        monkeypatch.setattr("morph_engine.translator.RECURSION_LIMIT", 5000)

        source_code = """
        fungsi putaran_tak_terbatas() maka
            putaran_tak_terbatas()
        akhir

        putaran_tak_terbatas()
        """

        lexer = Leksikal(source_code)
        tokens = lexer.buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()
        interpreter = Translator(ast)

        with pytest.raises(KesalahanRuntime) as exc_info:
            interpreter.interpretasi()

        assert "Sang waktu tak lagi berpihak" in str(exc_info.value)
