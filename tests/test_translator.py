# tests/test_translator.py
import pytest
from transisi.crusher import Pengurai
from transisi.lx import Leksikal
from transisi.translator import Penerjemah
from transisi.kesalahan import KesalahanRuntime

# Helper sederhana untuk menjalankan kode dan mendapatkan hasil atau error
def jalankan_kode(kode):
    try:
        lexer = Leksikal(kode)
        tokens, _ = lexer.buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()
        # Asumsi Penerjemah tidak lagi butuh Formatter di init-nya
        # Jika butuh, fixture/mock perlu dibuat.
        penerjemah = Penerjemah()
        hasil = penerjemah.terjemahkan(ast)
        return hasil
    except KesalahanRuntime as e:
        return f"Kesalahan Runtime: {e.args[0]}"
    except Exception as e:
        # Menangkap error lain untuk debugging
        return f"Error Tak Terduga: {e}"

class TestArithmeticOperators:
    def test_simple_arithmetic(self, capture_output):
        output = capture_output("tulis(10 + 2 * 5 - 3)") # 10 + 10 - 3 = 17
        assert output == "17"

    def test_modulo_operator(self, capture_output):
        output = capture_output("tulis(10 % 3)")
        assert output == "1"

    def test_exponent_operator(self, capture_output):
        output = capture_output("tulis(2 ^ 3)")
        assert output == "8"

    def test_precedence(self, capture_output):
        output = capture_output("tulis((2 + 3) * 4)") # 5 * 4 = 20
        assert output == "20"


class TestArithmeticErrors:
    def test_division_by_zero(self, capture_output):
        """Memastikan pembagian dengan nol menghasilkan pesan error yang benar."""
        output = capture_output("tulis(1 / 0)")
        assert "Tidak bisa membagi dengan nol" in output

    def test_type_error_for_arithmetic(self, capture_output):
        """Memastikan operasi aritmetika pada tipe yang salah menghasilkan error."""
        output = capture_output('tulis("a" + 1)')
        assert "Operan harus dua angka atau dua teks" in output


class TestVariablesAndScope:
    def test_variable_declaration_and_access(self, capture_output):
        program = """
        biar x = 10
        tulis(x)
        """
        output = capture_output(program)
        assert output == "10"

    def test_reassignment(self, capture_output):
        program = """
        biar x = 10;
        ubah x = 20;
        tulis(x);
        """
        output = capture_output(program)
        assert output == "20"
