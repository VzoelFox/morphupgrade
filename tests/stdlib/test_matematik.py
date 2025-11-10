# tests/stdlib/test_matematik.py
import pytest
import math

# Menandai semua tes di file ini sebagai bagian dari 'stdlib'
pytestmark = pytest.mark.stdlib

# Fixture untuk mengurangi boilerplate kode impor
@pytest.fixture
def run_math_code(run_morph_program):
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/matematik.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestKonstantaMatematik:
    def test_pi(self, run_math_code):
        output, errors = run_math_code("tulis(PI)")
        assert not errors
        assert float(output) == pytest.approx(math.pi)

    def test_e(self, run_math_code):
        output, errors = run_math_code("tulis(E)")
        assert not errors
        assert float(output) == pytest.approx(math.e)

    def test_tau(self, run_math_code):
        output, errors = run_math_code("tulis(TAU)")
        assert not errors
        assert float(output) == pytest.approx(math.tau)

class TestFungsiDasar:
    @pytest.mark.parametrize("input_val, expected", [("5", "5"), ("-5", "5"), ("0", "0"), ("-12.34", "12.34")])
    def test_abs(self, run_math_code, input_val, expected):
        output, errors = run_math_code(f"tulis(abs({input_val}))")
        assert not errors
        assert output.strip() == expected

    @pytest.mark.parametrize("a, b, expected", [("10", "20", "20"), ("-5", "-10", "-5"), ("7.5", "7.4", "7.5")])
    def test_maks(self, run_math_code, a, b, expected):
        output, errors = run_math_code(f"tulis(maks({a}, {b}))")
        assert not errors
        assert output.strip() == expected

    @pytest.mark.parametrize("a, b, expected", [("10", "20", "10"), ("-5", "-10", "-10"), ("7.5", "7.6", "7.5")])
    def test_min(self, run_math_code, a, b, expected):
        output, errors = run_math_code(f"tulis(min({a}, {b}))")
        assert not errors
        assert output.strip() == expected

class TestFungsiPembulatan:
    @pytest.mark.parametrize("input_val, expected", [("3.14", "3"), ("3.6", "4"), ("-2.7", "-3"), ("5", "5")])
    def test_pembulatan(self, run_math_code, input_val, expected):
        output, errors = run_math_code(f"tulis(pembulatan({input_val}))")
        assert not errors
        assert output.strip() == expected

    @pytest.mark.parametrize("input_val, expected", [("3.99", "3"), ("-2.1", "-3"), ("5", "5")])
    def test_lantai(self, run_math_code, input_val, expected):
        output, errors = run_math_code(f"tulis(lantai({input_val}))")
        assert not errors
        assert output.strip() == expected

    @pytest.mark.parametrize("input_val, expected", [("3.01", "4"), ("-2.9", "-2"), ("5", "5")])
    def test_langit(self, run_math_code, input_val, expected):
        output, errors = run_math_code(f"tulis(langit({input_val}))")
        assert not errors
        assert output.strip() == expected

class TestFungsiLainnya:
    def test_akar(self, run_math_code):
        output, errors = run_math_code("tulis(akar(16))")
        assert not errors
        assert float(output) == 4.0

    def test_pangkat(self, run_math_code):
        output, errors = run_math_code("tulis(pangkat(2, 3))")
        assert not errors
        assert float(output) == 8.0

    def test_sin_cos_tan(self, run_math_code):
        # Uji sin(pi/2) = 1
        output, errors = run_math_code("tulis(sin(PI / 2))")
        assert not errors
        assert float(output) == pytest.approx(1.0)

        # Uji cos(pi) = -1
        output, errors = run_math_code("tulis(cos(PI))")
        assert not errors
        assert float(output) == pytest.approx(-1.0)

        # Uji tan(pi/4) = 1
        output, errors = run_math_code("tulis(tan(PI/4))")
        assert not errors
        assert float(output) == pytest.approx(1.0)
