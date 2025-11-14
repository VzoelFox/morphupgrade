# tests/stdlib/test_teks.py
import pytest

pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_teks_code(run_morph_program):
    """Fixture to execute MORPH code that uses the 'teks' module."""
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/teks.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestTeksOperations:
    def test_pisah(self, run_teks_code):
        code = '''
        biar hasil = pisah("a,b,c", ",")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', "'") == "['a', 'b', 'c']"

    def test_gabung(self, run_teks_code):
        code = '''
        biar hasil = gabung(["a", "b", "c"], "-")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', '') == "a-b-c"

    def test_potong_spasi(self, run_teks_code):
        code = '''
        biar hasil = potong_spasi("  hello  ")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', '') == "hello"

    def test_huruf_besar(self, run_teks_code):
        code = '''
        biar hasil = huruf_besar("hello")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', '') == "HELLO"

    def test_huruf_kecil(self, run_teks_code):
        code = '''
        biar hasil = huruf_kecil("HELLO")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', '') == "hello"

    def test_ganti(self, run_teks_code):
        code = '''
        biar hasil = ganti("hello world", "world", "morph")
        tulis(hasil)
        '''
        output, errors = run_teks_code(code)
        assert not errors
        assert output.strip().replace('"', '') == "hello morph"

    def test_mulai_dengan(self, run_teks_code):
        code = '''
        tulis(mulai_dengan("hello world", "hello"))
        tulis(";")
        tulis(mulai_dengan("hello world", "world"))
        '''
        output, errors = run_teks_code(code)
        assert not errors
        parts = output.strip().replace('"', '').split(';')
        assert parts[0] == "benar"
        assert parts[1] == "salah"

    def test_berakhir_dengan(self, run_teks_code):
        code = '''
        tulis(berakhir_dengan("hello world", "world"))
        tulis(";")
        tulis(berakhir_dengan("hello world", "hello"))
        '''
        output, errors = run_teks_code(code)
        assert not errors
        parts = output.strip().replace('"', '').split(';')
        assert parts[0] == "benar"
        assert parts[1] == "salah"
