# tests/stdlib/test_daftar.py
import pytest

pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_daftar_code(run_morph_program):
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/daftar.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestFungsiDaftarDasar:
    def test_panjang(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(panjang([1, 2, 3]))')
        assert not errors
        assert int(output) == 3

    def test_tambah(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(tambah([1, 2], 3))')
        assert not errors
        assert output.strip() == "[1, 2, 3]"

    def test_hapus(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(hapus([1, 2, 3], 1))')
        assert not errors
        assert output.strip() == "[1, 3]"

        # Uji hapus di luar batas
        output, errors = run_daftar_code('tulis(hapus([1, 2, 3], 99))')
        assert not errors
        assert output.strip() == "[1, 2, 3]"

    def test_urut(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(urut([3, 1, 2]))')
        assert not errors
        assert output.strip() == "[1, 2, 3]"

    def test_balik(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(balik([1, 2, 3]))')
        assert not errors
        assert output.strip() == "[3, 2, 1]"

    def test_cari(self, run_daftar_code):
        output, errors = run_daftar_code('tulis(cari([10, 20, 30], 20))')
        assert not errors
        assert int(output) == 1

        # Uji cari item yang tidak ada
        output, errors = run_daftar_code('tulis(cari([10, 20, 30], 99))')
        assert not errors
        assert int(output) == -1
