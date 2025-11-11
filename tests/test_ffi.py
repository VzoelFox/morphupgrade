# tests/test_ffi.py
import pytest
import json
import os
from transisi.Morph import Morph

# Fixture `capture_output` sekarang akan otomatis diambil dari `tests/conftest.py`

class TestFFIBasicImport:
    """Test import module Python dasar."""

    def test_import_builtin_module_and_access_var(self, capture_output):
        """Test import module built-in Python (math) dan akses variabel."""
        code = """
        pinjam "math" sebagai m
        tulis(m.pi)
        """
        output = capture_output(code)
        assert "3.14159" in output

    def test_import_requires_alias_throws_error(self, capture_output):
        """Test bahwa import tanpa alias menghasilkan error."""
        code = 'pinjam "math"'
        output = capture_output(code)
        assert "KesalahanRuntime" in output
        assert "FFI import harus pakai alias" in output


class TestFFIFunctionCalls:
    """Test pemanggilan fungsi Python."""

    def test_call_function_with_one_arg(self, capture_output):
        """Test memanggil fungsi dengan satu argumen."""
        code = """
        pinjam "math" sebagai m
        tulis(m.sqrt(16))
        """
        output = capture_output(code)
        assert output == "4.0"

    def test_call_function_with_multiple_args(self, capture_output):
        """Test memanggil fungsi dengan beberapa argumen."""
        code = """
        pinjam "math" sebagai m
        tulis(m.pow(2, 3))
        """
        output = capture_output(code)
        assert output == "8.0"

    def test_string_argument_and_return(self, capture_output):
        """Test konversi tipe string."""
        code = """
        pinjam "os.path" sebagai path
        tulis(path.join("folder", "subfolder", "file.txt"))
        """
        expected = os.path.join("folder", "subfolder", "file.txt")
        output = capture_output(code)
        assert output == f'"{expected}"'


class TestFFITypeConversion:
    """Test konversi tipe data kompleks MORPH ↔ Python."""

    def test_morph_list_to_python_list(self, capture_output):
        """Test konversi Daftar MORPH ke list Python."""
        code = """
        pinjam "json" sebagai json
        biar data = [1, "dua", benar, 3.14, nil]
        tulis(json.dumps(data))
        """
        output = capture_output(code)
        parsed_output = json.loads(output.strip('"'))
        expected = [1, "dua", True, 3.14, None]
        assert parsed_output == expected

    def test_python_list_to_morph_list(self, capture_output):
        """Test konversi list Python ke Daftar MORPH."""
        code = """
        pinjam "json" sebagai json
        biar data_str = "[\\"satu\\", 2, true]"
        biar data_list = json.loads(data_str)
        tulis(data_list)
        tulis(data_list[0])
        """
        output = capture_output(code)
        assert output == '["satu", 2, benar]"satu"'


class TestFFIAdvanced:
    """Test fitur FFI advanced (class instantiation, methods)."""

    def test_class_instantiation(self, capture_output):
        """Test instansiasi kelas Python tanpa argumen."""
        code = """
        pinjam "datetime" sebagai dt
        biar now = dt.datetime.now()
        # Untuk saat ini, kita hanya pastikan tidak ada error
        tulis("sukses")
        """
        output = capture_output(code)
        assert output == '"sukses"'

    def test_method_call_on_instance(self, capture_output):
        """Test memanggil method pada instance objek Python."""
        code = """
        pinjam "datetime" sebagai dt
        biar now = dt.datetime.now()
        tulis(now.year)
        """
        import datetime
        current_year = str(datetime.datetime.now().year)
        output = capture_output(code)
        assert output == current_year


class TestFFIErrorHandling:
    """Test penanganan kesalahan di FFI."""

    def test_module_not_found(self, capture_output):
        """Test error saat modul Python tidak ditemukan."""
        code = 'pinjam "modul_yang_tidak_ada_sama_sekali" sebagai m'
        output = capture_output(code)
        assert "KesalahanImportFFI" in output
        assert "Gagal mengimpor modul Python" in output
        assert "modul_yang_tidak_ada_sama_sekali" in output
        # Cek apakah pesan error dari Python juga disertakan
        assert "ModuleNotFoundError" in output

    def test_attribute_not_found(self, capture_output):
        """Test error saat atribut tidak ditemukan di modul Python."""
        code = """
        pinjam "math" sebagai m
        tulis(m.atribut_tidak_jelas)
        """
        output = capture_output(code)
        assert "KesalahanAtributFFI" in output
        assert "Atribut 'atribut_tidak_jelas' tidak ditemukan" in output
        assert "AttributeError" in output

    def test_python_exception_on_call(self, capture_output):
        """Test error saat fungsi Python melempar exception."""
        code = """
        pinjam "math" sebagai m
        tulis(m.sqrt(-1))
        """
        output = capture_output(code)
        assert "KesalahanPanggilanFFI" in output
        assert "Terjadi error saat memanggil fungsi Python" in output
        assert "ValueError" in output


class TestFFIAsync:
    """Test fungsionalitas asinkron dengan FFI."""

    def test_await_on_ffi_async_function(self, capture_output):
        """Test `tunggu` pada hasil fungsi async dari FFI."""
        code = """
        pinjam "tests.fixtures.async_helper" sebagai helper
        asink fungsi utama() maka
            biar hasil = tunggu helper.async_add(5, 10)
            tulis(hasil)
        akhir
        tunggu utama()
        """
        output = capture_output(code)
        assert output == "15"
