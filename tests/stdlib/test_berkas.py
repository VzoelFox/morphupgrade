# tests/stdlib/test_berkas.py
import pytest
import tempfile
import os
from pathlib import Path

# Since this test is for a stdlib module, we mark it.
pytestmark = pytest.mark.stdlib

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def run_berkas_code(run_morph_program):
    """Fixture to execute MORPH code that uses the 'berkas' module."""
    def executor(code):
        # Automatically prepend the import statement for convenience.
        full_code = f'''
        ambil_semua "transisi/stdlib/wajib/berkas.fox"
        ambil_semua "transisi/stdlib/wajib/daftar.fox"
        {code}
        '''
        return run_morph_program(full_code)
    return executor

def safe_path(path):
    """Sanitizes a path for use in a MORPH string literal."""
    return path.replace("\\", "/")

class TestBacaTulisFile:
    def test_tulis_dan_baca_file(self, run_berkas_code, temp_dir):
        test_file = safe_path(os.path.join(temp_dir, "test.txt"))
        code = f'''
        biar konten = "Hello MORPH"
        tulis_file("{test_file}", konten)
        biar hasil = baca_file("{test_file}")
        tulis(hasil)
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        assert output.strip().replace('"', '') == "Hello MORPH"

    def test_baca_file_tidak_ada(self, run_berkas_code):
        code = '''
        baca_file("/path/yang/sangat/tidak/mungkin/ada/file.txt")
        '''
        output, errors = run_berkas_code(code)
        assert errors, "Expected an error but got none."
        assert "tidak ditemukan" in errors[0].lower()

    def test_baca_sebuah_direktori(self, run_berkas_code, temp_dir):
        path = safe_path(temp_dir)
        code = f'''
        baca_file("{path}")
        '''
        output, errors = run_berkas_code(code)
        assert errors, "Expected an error when reading a directory."
        assert "adalah direktori" in errors[0].lower()


class TestDirectoryOperations:
    def test_buat_dan_cek_direktori(self, run_berkas_code, temp_dir):
        new_dir = safe_path(os.path.join(temp_dir, "folder_baru", "sub_folder"))
        code = f'''
        buat_direktori("{new_dir}")
        tulis(ada_file("{new_dir}"))
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        assert output.strip() == "benar"

    def test_daftar_file(self, run_berkas_code, temp_dir):
        # Create test files and a directory
        Path(temp_dir, "file1.txt").touch()
        Path(temp_dir, "file2.log").touch()
        Path(temp_dir, "sub").mkdir()

        path = safe_path(temp_dir)
        code = f'''
        biar files = daftar_file("{path}")
        tulis(panjang(files))
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        assert int(output.strip()) == 3

    def test_daftar_file_pada_file(self, run_berkas_code, temp_dir):
        test_file = safe_path(os.path.join(temp_dir, "test.txt"))
        Path(test_file).touch()
        code = f'''
        daftar_file("{test_file}")
        '''
        output, errors = run_berkas_code(code)
        assert errors, "Expected an error when listing a file."
        assert "bukan direktori" in errors[0].lower()

class TestFileManagement:
    def test_salin_file(self, run_berkas_code, temp_dir):
        src = safe_path(os.path.join(temp_dir, "src.txt"))
        dst = safe_path(os.path.join(temp_dir, "dst.txt"))

        code = f'''
        tulis_file("{src}", "konten asli")
        salin_file("{src}", "{dst}")
        biar hasil = baca_file("{dst}")
        tulis(hasil)
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        assert "konten asli" in output

    def test_hapus_file(self, run_berkas_code, temp_dir):
        test_file = safe_path(os.path.join(temp_dir, "hapus.txt"))

        code = f'''
        tulis_file("{test_file}", "test")
        tulis(ada_file("{test_file}"))
        tulis(";")
        hapus_file("{test_file}")
        tulis(ada_file("{test_file}"))
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        cleaned_output = output.strip().replace('"', '')
        parts = cleaned_output.split(';')
        assert parts[0] == "benar"
        assert parts[1] == "salah"

    def test_pindah_file(self, run_berkas_code, temp_dir):
        src = safe_path(os.path.join(temp_dir, "asal.txt"))
        dst = safe_path(os.path.join(temp_dir, "tujuan.txt"))
        code = f'''
        tulis_file("{src}", "pindah")
        tulis(ada_file("{src}"))
        tulis(";")
        pindah_file("{src}", "{dst}")
        tulis(ada_file("{src}"))
        tulis(";")
        tulis(ada_file("{dst}"))
        tulis(";")
        tulis(baca_file("{dst}"))
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        cleaned_output = output.strip().replace('"', '')
        parts = cleaned_output.split(';')
        assert parts[0] == "benar"
        assert parts[1] == "salah"
        assert parts[2] == "benar"
        assert "pindah" in parts[3]

    def test_hapus_file_tidak_ada(self, run_berkas_code):
        """Verify deleting a non-existent file raises an error."""
        code = '''
        hapus_file("/path/yang/pasti/tidak/ada/file.txt")
        '''
        output, errors = run_berkas_code(code)
        assert errors, "Expected an error but got none."
        assert "tidak ditemukan" in errors[0].lower()

class TestPathOperations:
    def test_path_absolut(self, run_berkas_code):
        # We can't know the exact absolute path, but we can check if it's plausible.
        code = '''
        biar abs = path_absolut(".")
        tulis(panjang(abs) > 1) # Should be longer than "./"
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        assert output.strip() == "benar"

    def test_gabung_path(self, run_berkas_code):
        # This test verifies that multiple path components can be joined.
        code = '''
        biar parts = ["folder1", "folder2", "file.txt"]
        biar path = gabung_path(parts)
        tulis(path)
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        expected = safe_path(os.path.join("folder1", "folder2", "file.txt"))
        assert output.strip().replace('"', '') == expected

class TestInfoFile:
    def test_info_file(self, run_berkas_code, temp_dir):
        test_file = safe_path(os.path.join(temp_dir, "info.txt"))
        content = "12345"
        Path(test_file).write_text(content)
        code = f'''
        biar info = info_file("{test_file}")
        tulis(info["ukuran"])
        tulis(";")
        tulis(info["adalah_file"])
        tulis(";")
        tulis(info["adalah_direktori"])
        '''
        output, errors = run_berkas_code(code)
        assert not errors, f"Test failed with errors: {errors}"
        cleaned_output = output.strip().replace('"', '')
        parts = cleaned_output.split(';')
        assert int(parts[0]) == len(content)
        assert parts[1] == "benar"
        assert parts[2] == "salah"
