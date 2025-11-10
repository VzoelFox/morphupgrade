# tests/test_sprint1_fixes.py
import pytest

class TestShortCircuitEvaluation:
    def test_dan_prevents_division_by_zero(self, run_morph_program):
        program = "tulis(salah dan (1/0))"
        output, errors = run_morph_program(program)
        if errors: print(errors)
        assert not errors
        assert output == "salah"

    def test_atau_prevents_division_by_zero(self, run_morph_program):
        program = "tulis(benar atau (1/0))"
        output, errors = run_morph_program(program)
        if errors: print(errors)
        assert not errors
        assert output == "benar"

    def test_atau_returns_first_truthy(self, run_morph_program):
        program = "tulis(5 atau 10)"
        output, errors = run_morph_program(program)
        if errors: print(errors)
        assert not errors
        assert output == "5"

class TestModuloOperator:
    def test_modulo_basic(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 % 3)")
        if errors: print(errors)
        assert not errors
        assert output == "1"

    def test_modulo_zero_remainder(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 % 5)")
        if errors: print(errors)
        assert not errors
        assert output == "0"

class TestExponentOperator:
    def test_exponent_basic(self, run_morph_program):
        output, errors = run_morph_program("tulis(2 ^ 3)")
        if errors: print(errors)
        assert not errors
        assert output == "8"

    def test_exponent_right_associative(self, run_morph_program):
        output, errors = run_morph_program("tulis(2 ^ 3 ^ 2)") # Harusnya 2 ^ 9 = 512
        if errors: print(errors)
        assert not errors
        assert output == "512"

    def test_exponent_precedence_over_multiplication(self, run_morph_program):
        output, errors = run_morph_program("tulis(2 + 3 ^ 2)") # Harusnya 2 + 9 = 11
        if errors: print(errors)
        assert not errors
        assert output == "11"

class TestConstEnforcement:
    def test_tetap_prevents_reassignment(self, run_morph_program):
        program = """
        tetap x = 10
        ubah x = 20
        """
        output, errors = run_morph_program(program)
        assert errors
        assert "Tidak bisa mengubah konstanta" in errors[0]

    def test_tetap_in_function_scope(self, run_morph_program):
        program = """
        fungsi coba() maka
            tetap y = 5
            ubah y = 10
        akhir
        coba()
        """
        output, errors = run_morph_program(program)
        assert errors
        assert "Tidak bisa mengubah konstanta" in errors[0]

class TestDivisionTypeConsistency:
    def test_division_returns_int_when_exact(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 / 5)")
        if errors: print(errors)
        assert not errors
        assert output == "2"

    def test_division_returns_float_when_not_exact(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 / 3)")
        if errors: print(errors)
        assert not errors
        assert output.startswith("3.3333")

class TestStackTrace:
    def test_stack_trace_shows_call_chain(self, run_morph_program):
        program = """
        fungsi c() maka
            biar x = 1 / 0
        akhir
        fungsi b() maka
            c()
        akhir
        fungsi a() maka
            b()
        akhir
        a()
        """
        output, errors = run_morph_program(program)
        assert errors
        assert "Jejak Panggilan" in errors[0]
        assert "fungsi 'c' dipanggil" in errors[0]
        assert "fungsi 'b' dipanggil" in errors[0]
        assert "fungsi 'a' dipanggil" in errors[0]
