# tests/stdlib/test_waktu.py
import pytest
import datetime

pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_waktu_code(run_morph_program):
    """Fixture to execute MORPH code that uses the 'waktu' module."""
    def executor(code, **kwargs):
        # This executor can accept external Python objects to pass to the program
        return run_morph_program(code, external_objects=kwargs)
    return executor

class TestWaktuOperations:
    def test_tambah_hari(self, run_waktu_code):
        # Create a datetime object in Python
        start_date = datetime.datetime(2023, 1, 1)

        # The FFI will expose 'tgl_mulai' to the MORPH code
        code = '''
        ambil_semua "transisi/stdlib/wajib/waktu.fox"
        biar tgl_baru = tambah_hari(tgl_mulai, 5)
        tulis(tgl_baru.isoformat())
        '''
        output, errors = run_waktu_code(code, tgl_mulai=start_date)

        assert not errors, f"Test failed with errors: {errors}"
        # The output will be the string representation of the new datetime
        assert "2023-01-06" in output

    def test_selisih_hari(self, run_waktu_code):
        date1 = datetime.datetime(2023, 1, 10)
        date2 = datetime.datetime(2023, 1, 1)

        code = '''
        ambil_semua "transisi/stdlib/wajib/waktu.fox"
        biar selisih = selisih_hari(tgl1, tgl2)
        tulis(selisih)
        '''
        output, errors = run_waktu_code(code, tgl1=date1, tgl2=date2)
        assert not errors, f"Test failed with errors: {errors}"
        assert output.strip() == "9"

    def test_selisih_hari_negatif(self, run_waktu_code):
        date1 = datetime.datetime(2023, 1, 1)
        date2 = datetime.datetime(2023, 1, 10)

        code = '''
        ambil_semua "transisi/stdlib/wajib/waktu.fox"
        biar selisih = selisih_hari(tgl1, tgl2)
        tulis(selisih)
        '''
        output, errors = run_waktu_code(code, tgl1=date1, tgl2=date2)
        assert not errors, f"Test failed with errors: {errors}"
        assert output.strip() == "-9"
