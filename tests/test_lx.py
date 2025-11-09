# tests/test_leksikal.py
"""
Unit tests untuk Leksikal (Lexer/Tokenizer).

Test Categories:
1. Basic Tokenization (keywords, identifiers, literals)
2. Operators & Punctuation
3. Number Parsing (integers, floats, edge cases)
4. String Parsing (escape sequences, multiline)
5. Comments
6. Error Handling (invalid characters, unterminated strings)
"""
import pytest
from transisi.lx import Leksikal
from transisi.morph_t import TipeToken


# ============================================================================
# 1. BASIC TOKENIZATION
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestBasicTokenization:
    """Test dasar tokenization untuk keywords, identifiers, dan literals."""

    def test_keywords_recognized(self):
        """Test bahwa semua keywords dikenali dengan benar."""
        source = "biar tetap tulis jika maka akhir fungsi kembalikan nil dan atau tidak benar salah"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        expected_types = [
            TipeToken.BIAR, TipeToken.TETAP, TipeToken.TULIS,
            TipeToken.JIKA, TipeToken.MAKA, TipeToken.AKHIR,
            TipeToken.FUNGSI, TipeToken.KEMBALIKAN, TipeToken.NIL,
            TipeToken.DAN, TipeToken.ATAU, TipeToken.TIDAK,
            TipeToken.BENAR, TipeToken.SALAH,
            TipeToken.ADS
        ]

        actual_types = [t.tipe for t in tokens]
        assert not errors
        assert actual_types == expected_types

    def test_identifier_simple(self):
        """Test identifier sederhana."""
        source = "nama_variabel x y123 _private"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.NAMA
        assert tokens[0].nilai == "nama_variabel"

        assert tokens[1].tipe == TipeToken.NAMA
        assert tokens[1].nilai == "x"

        assert tokens[2].tipe == TipeToken.NAMA
        assert tokens[2].nilai == "y123"

        assert tokens[3].tipe == TipeToken.NAMA
        assert tokens[3].nilai == "_private"

    def test_boolean_values(self):
        """Test bahwa boolean memiliki nilai Python yang benar."""
        source = "benar salah"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.BENAR
        assert tokens[0].nilai is True  # Python boolean, not string!

        assert tokens[1].tipe == TipeToken.SALAH
        assert tokens[1].nilai is False


# ============================================================================
# 2. OPERATORS & PUNCTUATION
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestOperatorsAndPunctuation:
    """Test untuk operator aritmatika, perbandingan, dan punctuation."""

    @pytest.mark.parametrize("operator,expected_type", [
        ("+", TipeToken.TAMBAH),
        ("-", TipeToken.KURANG),
        ("*", TipeToken.KALI),
        ("/", TipeToken.BAGI),
        ("%", TipeToken.MODULO),
        ("=", TipeToken.SAMADENGAN),
        ("==", TipeToken.SAMA_DENGAN),
        ("!=", TipeToken.TIDAK_SAMA),
        ("<", TipeToken.KURANG_DARI),
        (">", TipeToken.LEBIH_DARI),
        ("<=", TipeToken.KURANG_SAMA),
        (">=", TipeToken.LEBIH_SAMA),
    ])
    def test_operator_recognition(self, operator, expected_type):
        """Test bahwa setiap operator dikenali dengan tipe yang benar."""
        lexer = Leksikal(operator)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == expected_type
        assert tokens[0].nilai == operator

    def test_punctuation(self):
        """Test punctuation marks."""
        source = "( ) [ ] ,"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        expected_types = [
            TipeToken.KURUNG_BUKA,
            TipeToken.KURUNG_TUTUP,
            TipeToken.SIKU_BUKA,
            TipeToken.SIKU_TUTUP,
            TipeToken.KOMA,
            TipeToken.ADS
        ]

        actual_types = [t.tipe for t in tokens]
        assert not errors
        assert actual_types == expected_types


# ============================================================================
# 3. NUMBER PARSING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestNumberParsing:
    """Test parsing angka (integer dan float) termasuk edge cases."""

    def test_integer_basic(self):
        """Test integer sederhana."""
        source = "42 0 999"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 42
        assert isinstance(tokens[0].nilai, int)

        assert tokens[1].nilai == 0
        assert tokens[2].nilai == 999

    def test_float_basic(self):
        """Test float sederhana."""
        source = "3.14 0.5 99.99"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 3.14
        assert isinstance(tokens[0].nilai, float)

        assert tokens[1].nilai == 0.5
        assert tokens[2].nilai == 99.99

    def test_float_invalid_leading_dot_is_dot_token(self):
        """Test bahwa .123 dipindai sebagai TITIK dan ANGKA."""
        source = ".123"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.TITIK
        assert tokens[1].tipe == TipeToken.ANGKA
        assert tokens[1].nilai == 123

    def test_float_invalid_trailing_dot_is_angka_and_dot(self):
        """Test bahwa 123. dipindai sebagai ANGKA dan TITIK."""
        source = "123."
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert len(tokens) == 3 # ANGKA, TITIK, ADS
        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 123
        assert tokens[1].tipe == TipeToken.TITIK

    def test_float_multiple_dots(self):
        """Test bahwa 1.2.3 adalah ANGKA, TITIK, ANGKA, TITIK, ANGKA."""
        source = "1.2.3"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 1.2
        assert tokens[1].tipe == TipeToken.TITIK
        assert tokens[2].tipe == TipeToken.ANGKA
        assert tokens[2].nilai == 3


# ============================================================================
# 4. STRING PARSING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestStringParsing:
    """Test parsing string literals."""

    def test_string_basic(self):
        """Test string literal sederhana."""
        source = '"Hey Vzoel Fox\'s disini"'
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.TEKS
        assert tokens[0].nilai == "Hey Vzoel Fox's disini"

    def test_string_empty(self):
        """Test empty string."""
        source = '""'
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].tipe == TipeToken.TEKS
        assert tokens[0].nilai == ""

    def test_string_unterminated(self):
        """Test an unterminated string results in an error."""
        source = '"Hello, World'
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert len(errors) == 1
        assert "Teks tidak ditutup" in errors[0]['pesan']


# ============================================================================
# 5. COMMENTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestComments:
    """Test bahwa comments di-skip dengan benar."""

    def test_comment_single_line(self):
        """Test single-line comment."""
        source = """
        biar x = 5  # Ini komentar
        tulis(x)
        """
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        token_values = [t.nilai for t in tokens]
        assert "# Ini komentar" not in token_values
        assert "Ini komentar" not in token_values

    def test_comment_entire_line(self):
        """Test entire line as comment."""
        source = """
        # Ini baris komentar
        biar x = 5
        """
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        non_meta_tokens = [t for t in tokens if t.tipe not in (TipeToken.ADS, TipeToken.AKHIR_BARIS)]
        assert len(non_meta_tokens) == 4


# ============================================================================
# 6. ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
@pytest.mark.errors
class TestLexerErrors:
    """Test error handling untuk karakter invalid."""

    def test_invalid_character(self):
        """Test bahwa karakter invalid menghasilkan token TIDAK_DIKENAL dan error."""
        source = "biar x = 5 @ 10"
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert len(errors) == 1
        assert "Karakter '@' tidak dikenal" in errors[0]['pesan']

        unknown_token = next((t for t in tokens if t.tipe == TipeToken.TIDAK_DIKENAL), None)
        assert unknown_token is not None
        assert unknown_token.nilai == "@"

    def test_error_has_line_info(self):
        """Test bahwa error yang dilaporkan mengandung info baris dan kolom yang benar."""
        source = """
        biar x = 5
        biar y = @
        """
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert len(errors) == 1
        error_info = errors[0]
        assert error_info['baris'] == 3
        assert error_info['kolom'] is not None


# ============================================================================
# 7. EDGE CASES & WHITESPACE
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestEdgeCases:
    """Test edge cases dan whitespace handling."""

    def test_empty_source(self):
        """Test bahwa empty source code tidak crash."""
        source = ""
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert len(tokens) == 1
        assert tokens[0].tipe == TipeToken.ADS

    def test_whitespace_only(self):
        """Test bahwa whitespace-only source tidak crash."""
        source = "   \n\t  \n  "
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert all(t.tipe in (TipeToken.AKHIR_BARIS, TipeToken.ADS) for t in tokens)

    def test_newline_tracking(self):
        """Test bahwa baris dan kolom di-track dengan benar."""
        source = """biar x = 5
biar y = 10"""
        lexer = Leksikal(source)
        tokens, errors = lexer.buat_token()

        assert not errors
        assert tokens[0].baris == 1 # Token 'biar'

        second_biar = [t for t in tokens if t.tipe == TipeToken.BIAR][1]
        assert second_biar.baris == 2
