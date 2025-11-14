# tests/stdlib/test_daftar.py
import pytest

pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_daftar_code(run_morph_program):
    """Fixture to execute MORPH code that uses the 'daftar' module."""
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/daftar.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestDaftarOperations:
    def test_panjang(self, run_daftar_code):
        code = '''
        biar hasil = panjang([1, 2, 3])
        tulis(hasil)
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        assert output.strip() == "3"

    def test_tambah(self, run_daftar_code):
        code = '''
        biar d = [1, 2]
        ubah d = tambah(d, 3)
        tulis(d)
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        assert output.strip() == "[1, 2, 3]"

    def test_hapus(self, run_daftar_code):
        code = '''
        biar d = [1, 2, 3]
        ubah d = hapus(d, 1)
        tulis(d)
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        assert output.strip() == "[1, 3]"

    def test_urut(self, run_daftar_code):
        code = '''
        biar hasil = urut([3, 1, 2])
        tulis(hasil)
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        assert output.strip() == "[1, 2, 3]"

    def test_balik(self, run_daftar_code):
        code = '''
        biar hasil = balik([1, 2, 3])
        tulis(hasil)
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        assert output.strip() == "[3, 2, 1]"

    def test_cari(self, run_daftar_code):
        code = '''
        tulis(cari([1, 2, 3], 2))
        tulis(";")
        tulis(cari([1, 2, 3], 4))
        '''
        output, errors = run_daftar_code(code)
        assert not errors
        parts = output.strip().replace('"', '').split(';')
        assert parts[0] == "1"
        assert parts[1] == "-1"
