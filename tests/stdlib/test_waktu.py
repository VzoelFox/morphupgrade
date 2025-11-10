# tests/stdlib/test_waktu.py
import pytest
import time
import datetime

# Menandai semua tes di file ini sebagai bagian dari 'stdlib'
pytestmark = pytest.mark.stdlib

@pytest.fixture
def run_waktu_code(run_morph_program):
    def executor(code):
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/waktu.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

class TestFungsiWaktu:
    def test_sekarang(self, run_waktu_code):
        output, errors = run_waktu_code("tulis(sekarang())")
        assert not errors
        timestamp = float(output)
        assert timestamp == pytest.approx(time.time(), abs=2) # Toleransi 2 detik

    def test_format_waktu(self, run_waktu_code):
        # Timestamp untuk 1 Januari 2024, 15:30:00 GMT
        ts = 1704123000
        format_str = "YYYY-MM-DD HH:mm:ss"
        expected = "2024-01-01 15:30:00"

        output, errors = run_waktu_code(f'tulis(format_waktu({ts}, "{format_str}"))')
        assert not errors
        assert output.strip().replace('"', '') == expected

    def test_tambah_hari(self, run_waktu_code):
        ts_awal = 1704123000 # 1 Jan 2024 15:30:00
        # Tambah 10 hari
        output, errors = run_waktu_code(f"tulis(tambah_hari({ts_awal}, 10))")
        assert not errors

        ts_hasil = float(output)
        expected_ts = ts_awal + (10 * 24 * 60 * 60)
        assert ts_hasil == pytest.approx(expected_ts)

    def test_selisih_hari(self, run_waktu_code):
        ts1 = 1704987000 # 11 Jan 2024 15:30:00
        ts2 = 1704123000 # 1 Jan 2024 15:30:00

        output, errors = run_waktu_code(f"tulis(selisih_hari({ts1}, {ts2}))")
        assert not errors
        assert int(output) == 10

    def test_hari_ini(self, run_waktu_code):
        output, errors = run_waktu_code("tulis(hari_ini())")
        assert not errors

        hari_ini_py = datetime.datetime.today().strftime('%A')
        peta_hari = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }
        expected_hari = peta_hari[hari_ini_py]
        assert output.strip().replace('"', '') == expected_hari
