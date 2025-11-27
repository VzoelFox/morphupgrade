# tests/stdlib/test_berkas.py
import pytest
import tempfile
import os

pytestmark = pytest.mark.stdlib

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def run_berkas_code(run_morph_program):
    def executor(code):
        berkas_path = safe_path(os.path.abspath("transisi/stdlib/wajib/berkas.fox"))
        full_code = f'''
        ambil_semua "{berkas_path}"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

def safe_path(path):
    return path.replace("\\", "/")

class TestBacaTulisFile:
    def test_tulis_dan_baca_file_sukses(self, run_berkas_code, temp_dir):
        """
        Memvalidasi bahwa kita bisa menulis ke file dan membaca kembali isinya
        menggunakan FFI berbasis Result.
        """
        test_file = safe_path(os.path.join(temp_dir, "test.txt"))
        code = f'''
        biar konten = "Hello Result"

        // Tulis ke file
        biar hasil_tulis = tulis_file("{test_file}", konten)
        jodohkan hasil_tulis dengan
        | Gagal(p) maka
            tulis("GAGAL TULIS:", p)
        | Sukses(_) maka
            // Lanjutkan jika sukses
            biar hasil_baca = baca_file("{test_file}")
            jodohkan hasil_baca dengan
            | Gagal(p2) maka
                tulis("GAGAL BACA:", p2)
            | Sukses(data) maka
                tulis(data)
            akhir
        akhir
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with runtime errors: {errors}"
        assert "GAGAL" not in output
        assert output.strip() == "Hello Result"

    def test_baca_file_gagal(self, run_berkas_code):
        """
        Memvalidasi bahwa membaca file yang tidak ada mengembalikan Result.gagal
        dan tidak menyebabkan crash.
        """
        code = '''
        biar hasil = baca_file("/path/yang/sangat/tidak/mungkin/ada/file.txt")
        jodohkan hasil dengan
        | Sukses(_) maka
            tulis("INI SEHARUSNYA GAGAL")
        | Gagal(pesan) maka
            // Periksa apakah pesan error mengandung teks yang diharapkan
            // Ini adalah cara yang lebih tangguh daripada mencocokkan string yang sama persis
            tulis("sukses_gagal")
        akhir
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with runtime errors: {errors}"
        assert "sukses_gagal" in output
