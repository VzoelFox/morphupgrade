# tests/stdlib/test_teks.py
import pytest

pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_teks_code(run_morph_program):
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/teks.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestFungsiTeks:
    def test_pisah(self, run_teks_code):
        output, errors = run_teks_code('tulis(pisah("satu,dua,tiga", ","))')
        assert not errors
        assert output.strip() == '["satu", "dua", "tiga"]'

    def test_gabung(self, run_teks_code):
        output, errors = run_teks_code('tulis(gabung(["a", "b", "c"], "-"))')
        assert not errors
        assert output.strip().replace('"', '') == "a-b-c"

    def test_potong_spasi(self, run_teks_code):
        output, errors = run_teks_code('tulis(potong_spasi("   morph   "))')
        assert not errors
        assert output.strip().replace('"', '') == "morph"

    def test_huruf_besar(self, run_teks_code):
        output, errors = run_teks_code('tulis(huruf_besar("morph"))')
        assert not errors
        assert output.strip().replace('"', '') == "MORPH"

    def test_huruf_kecil(self, run_teks_code):
        output, errors = run_teks_code('tulis(huruf_kecil("MORPH"))')
        assert not errors
        assert output.strip().replace('"', '') == "morph"

    def test_ganti(self, run_teks_code):
        output, errors = run_teks_code('tulis(ganti("halo dunia", "dunia", "morph"))')
        assert not errors
        assert output.strip().replace('"', '') == "halo morph"

    def test_mulai_dengan(self, run_teks_code):
        output, errors = run_teks_code('tulis(mulai_dengan("morph lang", "morph"))')
        assert not errors
        assert output.strip() == "benar"

        output, errors = run_teks_code('tulis(mulai_dengan("morph lang", "python"))')
        assert not errors
        assert output.strip() == "salah"

    def test_berakhir_dengan(self, run_teks_code):
        output, errors = run_teks_code('tulis(berakhir_dengan("gambar.jpg", ".jpg"))')
        assert not errors
        assert output.strip() == "benar"

        output, errors = run_teks_code('tulis(berakhir_dengan("gambar.jpg", ".png"))')
        assert not errors
        assert output.strip() == "salah"
