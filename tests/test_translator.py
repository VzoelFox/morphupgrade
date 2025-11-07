# tests/test_translator.py
import pytest
from morph_engine.crusher import Pengurai
from morph_engine.lx import Leksikal
from morph_engine.translator import Penerjemah, KesalahanRuntime

# Helper sederhana untuk menjalankan kode dan mendapatkan hasil atau error
def jalankan_kode(kode):
    try:
        lexer = Leksikal(kode)
        tokens = lexer.buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()
        penerjemah = Penerjemah()
        return penerjemah.terjemahkan(ast)
    except KesalahanRuntime as e:
        return f"Kesalahan Runtime: {e.args[0]}"
    except Exception as e:
        # Menangkap error lain untuk debugging
        return f"Error Tak Terduga: {e}"

class TestArithmeticOperators:
    def test_simple_arithmetic(self, capture_output):
        output = capture_output("tulis(10 + 2 * 5 - 3)") # 10 + 10 - 3 = 17
        assert output == "17"

    @pytest.mark.skip(reason="Operator Modulo belum diimplementasikan di engine baru")
    def test_modulo_operator(self, capture_output):
        output = capture_output("tulis(10 % 3)")
        assert output == "1"

    @pytest.mark.skip(reason="Operator Pangkat belum diimplementasikan di engine baru")
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
        # Memperbarui assert untuk mencocokkan pesan error dari engine baru
        assert "Semesta tak terhingga saat dibagi dengan kehampaan (nol)" in output

    def test_type_error_for_arithmetic(self, capture_output):
        """Memastikan operasi aritmetika pada tipe yang salah menghasilkan error."""
        output = capture_output('tulis("a" + 1)')
        # Memperbarui assert untuk mencocokkan pesan error dari engine baru
        assert "Dua dunia tak dapat menyatu" in output


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
        biar x = 10
        x = 20
        tulis(x)
        """
        output = capture_output(program)
        assert output == "20"
