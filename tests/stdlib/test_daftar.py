# tests/stdlib/test_daftar.py
import pytest

@pytest.mark.usefixtures("run_morph_program")
class TestDaftarOperations:
    # Modul FFI baru yang akan diuji
    MODULE_PATH = "transisi.stdlib.wajib.ffi_daftar"

    def test_panjang(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [1, 2, 3]
        tulis(daftar.panjang(x))
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "3" in output

    def test_tambah(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [1]
        ubah x = daftar.tambah(x, 2)
        tulis(x[1])
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "2" in output

    def test_hapus(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [1, 2, 3]
        ubah x = daftar.hapus(x, 1) # Hapus '2'
        tulis(x[0], x[1])
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "1 3" in output

    def test_urut(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [3, 1, 2]
        biar y = daftar.urut(x)
        tulis(y[0], y[1], y[2])
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "1 2 3" in output

    def test_balik(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [1, 2, 3]
        biar y = daftar.balik(x)
        tulis(y[0], y[1], y[2])
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "3 2 1" in output

    def test_cari(self, run_morph_program):
        program = f"""
        pinjam "{self.MODULE_PATH}" sebagai daftar
        biar x = [10, 20, 30]
        tulis(daftar.cari(x, 20))
        tulis(daftar.cari(x, 99))
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "1" in output # Indeks dari 20
        assert "-1" in output # Tidak ditemukan
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert "1" in output # Indeks dari 20
        assert "-1" in output # Tidak ditemukan
        """
