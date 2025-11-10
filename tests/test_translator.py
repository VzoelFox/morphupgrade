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
    def test_simple_arithmetic(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 + 2 * 5 - 3)") # 10 + 10 - 3 = 17
        assert not errors
        assert output == "17"

    def test_modulo_operator(self, run_morph_program):
        output, errors = run_morph_program("tulis(10 % 3)")
        assert not errors
        assert output == "1"

    def test_exponent_operator(self, run_morph_program):
        output, errors = run_morph_program("tulis(2 ^ 3)")
        assert not errors
        assert output == "8"

    def test_precedence(self, run_morph_program):
        output, errors = run_morph_program("tulis((2 + 3) * 4)") # 5 * 4 = 20
        assert not errors
        assert output == "20"


class TestArithmeticErrors:
    def test_division_by_zero(self, run_morph_program):
        """Memastikan pembagian dengan nol menghasilkan pesan error yang benar."""
        output, errors = run_morph_program("tulis(1 / 0)")
        assert len(errors) == 1
        assert "Tidak bisa membagi dengan nol" in errors[0]

    def test_type_error_for_arithmetic(self, run_morph_program):
        """Memastikan operasi aritmetika pada tipe yang salah menghasilkan error."""
        output, errors = run_morph_program('tulis("a" + 1)')
        assert len(errors) == 1
        assert "Operan harus dua angka atau dua teks" in errors[0]


class TestVariablesAndScope:
    def test_variable_declaration_and_access(self, run_morph_program):
        program = """
        biar x = 10
        tulis(x)
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert output == "10"

    def test_reassignment(self, run_morph_program):
        program = """
        biar x = 10;
        ubah x = 20;
        tulis(x);
        """
        output, errors = run_morph_program(program)
        assert not errors
        assert output == "20"


class TestLoopProtection:
    def test_infinite_loop_is_terminated(self, run_morph_program):
        """Memverifikasi bahwa loop tak terbatas dihentikan oleh batas iterasi."""
        program = """
        selama benar maka
            // Loop ini akan berjalan selamanya jika tidak dihentikan
        akhir
        """
        output, errors = run_morph_program(program)

        assert len(errors) == 1, "Seharusnya ada satu error runtime"
        assert "KesalahanRuntime" in errors[0]
        assert "Loop melebihi batas iterasi maksimum" in errors[0]
        assert "(10000)" in errors[0] # Cek batas default

    def test_loop_limit_is_configurable(self, run_morph_program, monkeypatch):
        """Memverifikasi bahwa batas iterasi loop dapat dikonfigurasi melalui env var."""
        LIMIT = 50
        monkeypatch.setenv("MORPH_LOOP_LIMIT", str(LIMIT))

        program = f"""
        biar i = 0
        selama i <= {LIMIT} maka
            ubah i = i + 1
        akhir
        tulis("selesai")
        """
        output, errors = run_morph_program(program)

        assert len(errors) == 1, "Seharusnya ada satu error karena batas terlampaui"
        assert "KesalahanRuntime" in errors[0]
        assert f"Loop melebihi batas iterasi maksimum ({LIMIT})" in errors[0]
        assert "selesai" not in output, "Program seharusnya tidak mencapai akhir"

    def test_normal_loop_is_unaffected(self, run_morph_program):
        """Memverifikasi bahwa loop normal yang tidak melebihi batas berjalan dengan baik."""
        program = """
        biar i = 0
        biar total = 0
        selama i < 100 maka
            ubah total = total + i
            ubah i = i + 1
        akhir
        tulis(total)
        """
        output, errors = run_morph_program(program)

        assert not errors, f"Seharusnya tidak ada error, tapi mendapat: {errors}"
        expected_sum = sum(range(100))
        assert str(expected_sum) in output
