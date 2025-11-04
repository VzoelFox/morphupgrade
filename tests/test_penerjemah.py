# tests/test_penerjemah.py
import pytest
from morph_engine.leksikal import Leksikal
from morph_engine.pengurai import Pengurai
from morph_engine.penerjemah import Penerjemah, KesalahanRuntime

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
            interpreter = Penerjemah(ast)
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
        assert "Tidak bisa modulo dengan nol" in str(exc_info.value)

    def test_division_by_zero(self, run_morph):
        """Test that division by zero raises a runtime error."""
        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph("tulis(10 / 0)")
        assert "Tidak bisa membagi dengan nol" in str(exc_info.value)

    def test_type_error_for_arithmetic(self, run_morph):
        """Test that arithmetic on non-numbers raises a runtime error."""
        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph('tulis("a" + 5)')
        assert "Operasi '+' tidak dapat digunakan antara" in str(exc_info.value)

        with pytest.raises(KesalahanRuntime) as exc_info:
            run_morph("tulis(benar ^ 2)")
        assert "Operasi aritmatika '^' hanya dapat digunakan pada tipe angka" in str(exc_info.value)
