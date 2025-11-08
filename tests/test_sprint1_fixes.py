# tests/test_sprint1_fixes.py
"""
Tests untuk memverifikasi semua fix dari Sprint 1.
Sesuai dengan 15 poin yang telah diidentifikasi tim analis.
"""
import pytest

class TestShortCircuitEvaluation:
    """Poin #8: Operator dan/atau logic"""

    def test_dan_prevents_division_by_zero(self, capture_output):
        code = "tulis(salah dan (1/0))"
        output = capture_output(code)
        assert output == "salah"

    def test_atau_prevents_division_by_zero(self, capture_output):
        code = "tulis(benar atau (1/0))"
        output = capture_output(code)
        assert output == "benar"

    def test_atau_returns_first_truthy(self, capture_output):
        code = "tulis(5 atau 10)"
        output = capture_output(code)
        assert output == "5"


class TestModuloOperator:
    """Poin #1: Operator modulo"""

    def test_modulo_basic(self, capture_output):
        assert capture_output("tulis(10 % 3)") == "1"

    def test_modulo_zero_remainder(self, capture_output):
        assert capture_output("tulis(10 % 5)") == "0"


class TestExponentOperator:
    """Poin #2: Operator pangkat"""

    def test_exponent_basic(self, capture_output):
        assert capture_output("tulis(2 ^ 3)") == "8"

    def test_exponent_right_associative(self, capture_output):
        """CRITICAL: 2^3^2 harus 512, bukan 64"""
        assert capture_output("tulis(2 ^ 3 ^ 2)") == "512"

    def test_exponent_precedence_over_multiplication(self, capture_output):
        """2 + 3^2 = 2 + 9 = 11"""
        assert capture_output("tulis(2 + 3 ^ 2)") == "11"


class TestConstEnforcement:
    """Poin #4: tetap immutability"""

    def test_tetap_prevents_reassignment(self, capture_output):
        code = """
tetap PI = 3.14
ubah PI = 3.14159
"""
        output = capture_output(code)
        assert "Tidak bisa mengubah konstanta" in output

    def test_tetap_in_function_scope(self, capture_output):
        code = """
tetap X = 10
fungsi ubah_x() maka
ubah X = 20
akhir
ubah_x()
"""
        output = capture_output(code)
        assert "Tidak bisa mengubah konstanta" in output


class TestDivisionTypeConsistency:
    """Poin #6: Division result type"""

    def test_division_returns_int_when_exact(self, capture_output):
        assert capture_output("tulis(10 / 5)") == "2"

    def test_division_returns_float_when_not_exact(self, capture_output):
        result = capture_output("tulis(10 / 3)")
        assert result.startswith("3.3333")


class TestStackTrace:
    """Poin #9: Stack trace untuk nested calls"""

    def test_stack_trace_shows_call_chain(self, capture_output):
        code = """
fungsi a() maka
kembalikan 1 / 0
akhir

fungsi b() maka
kembalikan a()
akhir

b()
"""
        output = capture_output(code)
        assert "Jejak Panggilan" in output or "fungsi 'a'" in output
