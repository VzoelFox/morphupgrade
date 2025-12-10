# tests/fitur_baru/test_pattern_matching.py
import pytest

# Menggunakan fixture 'capture_output' dari conftest.py

class TestJodohkanDaftar:
    def test_destrukturisasi_daftar_tetap(self, capture_output):
        code = """
        biar data = [10, 20, 30]
        jodohkan data dengan
            | [a, b, c] maka
                tulis(a, b, c)
            | _ maka
                tulis("gagal")
        akhir
        """
        output = capture_output(code)
        assert output == "10 20 30"

    def test_destrukturisasi_daftar_dengan_wildcard(self, capture_output):
        code = """
        biar data = ["penting", "abaikan", "penting lagi"]
        jodohkan data dengan
            | [x, _, z] maka
                tulis(x, z)
            | _ maka
                tulis("gagal")
        akhir
        """
        output = capture_output(code)
        assert output == '"penting" "penting lagi"'

    def test_destrukturisasi_daftar_dengan_pola_sisa(self, capture_output):
        code = """
        biar data = [1, 2, 3, 4, 5]
        jodohkan data dengan
            | [pertama, kedua, ...sisa] maka
                tulis(pertama, kedua, sisa)
            | _ maka
                tulis("gagal")
        akhir
        """
        output = capture_output(code)
        assert output == '1 2 [3, 4, 5]'

    def test_destrukturisasi_daftar_dengan_pola_sisa_kosong(self, capture_output):
        code = """
        biar data = [1, 2]
        jodohkan data dengan
            | [pertama, kedua, ...sisa] maka
                tulis(pertama, kedua, sisa)
            | _ maka
                tulis("gagal")
        akhir
        """
        output = capture_output(code)
        assert output == '1 2 []'


class TestJodohkanJaga:
    def test_pattern_guard_yang_berhasil(self, capture_output):
        code = """
        tipe Respon = Data(nilai)
        biar r = Data(100)
        jodohkan r dengan
            | Data(x) ketika x > 50 maka
                tulis("lebih besar dari 50")
            | Data(x) maka
                tulis("kurang dari atau sama dengan 50")
        akhir
        """
        output = capture_output(code)
        assert output == '"lebih besar dari 50"'

    def test_pattern_guard_yang_gagal(self, capture_output):
        code = """
        tipe Respon = Data(nilai)
        biar r = Data(10)
        jodohkan r dengan
            | Data(x) ketika x > 50 maka
                tulis("lebih besar dari 50")
            | Data(x) maka
                tulis("kurang dari atau sama dengan 50")
        akhir
        """
        output = capture_output(code)
        assert output == '"kurang dari atau sama dengan 50"'
