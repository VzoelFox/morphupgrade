# tests/fitur_baru/test_pemanggilan_metode.py
import pytest

# Menandai semua tes di file ini sebagai fitur baru
pytestmark = pytest.mark.fitur_baru

class TestPemanggilanMetode:
    def test_pemanggilan_metode_sederhana_pada_string(self, run_morph_program):
        """
        Tes paling dasar untuk memastikan sintaks 'objek.metode()' berfungsi.
        """
        code = '''
        biar s = "halo"
        tulis(s.upper())
        '''
        output, errors = run_morph_program(code)
        assert not errors
        assert output.strip().replace('"', '') == "HALO"

    def test_pemanggilan_metode_berhasil(self, run_morph_program):
        """
        Tes ini untuk memvalidasi pemanggilan metode yang lebih kompleks.
        """
        code = '''
        biar s = "halo dunia"
        tulis(s.replace("dunia", "MORPH"))
        '''
        output, errors = run_morph_program(code)
        assert not errors
        assert output.strip().replace('"', '') == "halo MORPH"
