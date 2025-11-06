# tests/test_leksikal.py
"""
Unit tests untuk Leksikal (Lexer/Tokenizer).
"""
import pytest
from morph_engine.lx import Leksikal, LeksikalKesalahan
from morph_engine.morph_t import TipeToken


# ============================================================================
# 1. BASIC TOKENIZATION
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestBasicTokenization:
    """Test dasar tokenization untuk keywords, identifiers, dan literals."""

    def test_keywords_recognized(self, lexer_factory):
        """Test bahwa semua keywords dikenali dengan benar."""
        source = "biar tetap tulis jika maka akhir fungsi kembalikan nil dan atau tidak benar salah"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        expected_types = [
            TipeToken.BIAR, TipeToken.TETAP, TipeToken.TULIS,
            TipeToken.JIKA, TipeToken.MAKA, TipeToken.AKHIR,
            TipeToken.FUNGSI, TipeToken.KEMBALIKAN, TipeToken.NIL,
            TipeToken.DAN, TipeToken.ATAU, TipeToken.TIDAK,
            TipeToken.BENAR, TipeToken.SALAH,
            TipeToken.ADS
        ]

        actual_types = [t.tipe for t in tokens]
        assert actual_types == expected_types

    def test_identifier_simple(self, lexer_factory):
        """Test identifier sederhana."""
        source = "nama_variabel x y123 _private"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == TipeToken.PENGENAL
        assert tokens[0].nilai == "nama_variabel"

        assert tokens[1].tipe == TipeToken.PENGENAL
        assert tokens[1].nilai == "x"

        assert tokens[2].tipe == TipeToken.PENGENAL
        assert tokens[2].nilai == "y123"

        assert tokens[3].tipe == TipeToken.PENGENAL
        assert tokens[3].nilai == "_private"

    def test_boolean_values(self, lexer_factory):
        """Test bahwa boolean memiliki nilai Python yang benar."""
        source = "benar salah"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

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
        ("=", TipeToken.SAMA_DENGAN),
        ("==", TipeToken.SAMA_DENGAN_SAMA),
        ("!=", TipeToken.TIDAK_SAMA),
        ("<", TipeToken.LEBIH_KECIL),
        (">", TipeToken.LEBIH_BESAR),
        ("<=", TipeToken.LEBIH_KECIL_SAMA),
        (">=", TipeToken.LEBIH_BESAR_SAMA),
    ])
    def test_operator_recognition(self, lexer_factory, operator, expected_type):
        """Test bahwa setiap operator dikenali dengan tipe yang benar."""
        lexer = lexer_factory(operator)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == expected_type
        assert tokens[0].nilai == operator

    def test_punctuation(self, lexer_factory):
        """Test punctuation marks."""
        source = "( ) [ ] ,"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        expected_types = [
            TipeToken.BUKA_KURUNG,
            TipeToken.TUTUP_KURUNG,
            TipeToken.KURUNG_SIKU_BUKA,
            TipeToken.KURUNG_SIKU_TUTUP,
            TipeToken.KOMA,
            TipeToken.ADS
        ]

        actual_types = [t.tipe for t in tokens]
        assert actual_types == expected_types


# ============================================================================
# 3. NUMBER PARSING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestNumberParsing:
    """Test parsing angka (integer dan float) termasuk edge cases."""

    def test_integer_basic(self, lexer_factory):
        """Test integer sederhana."""
        source = "42 0 999"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 42
        assert isinstance(tokens[0].nilai, int)

        assert tokens[1].nilai == 0
        assert tokens[2].nilai == 999

    def test_float_basic(self, lexer_factory):
        """Test float sederhana."""
        source = "3.14 0.5 99.99"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == TipeToken.ANGKA
        assert tokens[0].nilai == 3.14
        assert isinstance(tokens[0].nilai, float)

        assert tokens[1].nilai == 0.5
        assert tokens[2].nilai == 99.99

    def test_float_invalid_leading_dot(self, lexer_factory):
        """Test bahwa .123 tidak valid."""
        source = ".123"
        lexer = lexer_factory(source)

        with pytest.raises(LeksikalKesalahan) as exc_info:
            lexer.buat_token()

        assert "tidak valid" in str(exc_info.value).lower()

    def test_float_invalid_trailing_dot(self, lexer_factory):
        """Test bahwa 123. tidak valid."""
        source = "123."
        lexer = lexer_factory(source)

        with pytest.raises(LeksikalKesalahan) as exc_info:
            lexer.buat_token()

        assert "tidak valid" in str(exc_info.value).lower()

    def test_float_multiple_dots(self, lexer_factory):
        """Test bahwa 1.2.3 tidak valid."""
        source = "1.2.3"
        lexer = lexer_factory(source)

        with pytest.raises(LeksikalKesalahan) as exc_info:
            lexer.buat_token()

        assert "multiple" in str(exc_info.value).lower() or "tidak valid" in str(exc_info.value).lower()


# ============================================================================
# 4. STRING PARSING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestStringParsing:
    """Test parsing string literals dengan escape sequences."""

    def test_string_basic(self, lexer_factory):
        """Test string literal sederhana."""
        source = '"Hey Vzoel Fox\'s disini"'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == TipeToken.TEKS
        assert tokens[0].nilai == "Hey Vzoel Fox's disini"

    def test_string_empty(self, lexer_factory):
        """Test empty string."""
        source = '""'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].tipe == TipeToken.TEKS
        assert tokens[0].nilai == ""

    def test_string_escape_quote(self, lexer_factory):
        """Test escape sequence: \\\" """
        source = r'"Dia berkata, \"Halo\""'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].nilai == 'Dia berkata, "Halo"'

    def test_string_escape_backslash(self, lexer_factory):
        """Test escape sequence: \\\\ """
        source = r'"Path: C:\\Users\\nama"'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].nilai == r'Path: C:\Users\nama'

    def test_string_escape_newline(self, lexer_factory):
        """Test escape sequence: \\n """
        source = r'"Baris 1\nBaris 2"'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert tokens[0].nilai == "Baris 1\nBaris 2"

    def test_string_unterminated(self, lexer_factory):
        """Test an unterminated string results in an UNKNOWN token."""
        source = '"Hello, World'
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()
        assert len(tokens) == 2  # UNKNOWN and ADS
        assert tokens[0].tipe == TipeToken.TIDAK_DIKENAL
        assert tokens[0].nilai == '"Hello, World'


# ============================================================================
# 5. COMMENTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestComments:
    """Test bahwa comments di-skip dengan benar."""

    def test_comment_single_line(self, lexer_factory):
        """Test single-line comment."""
        source = """
        biar x = 5  # Ini komentar
        tulis(x)
        """
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Comment tidak boleh menghasilkan token
        token_values = [t.nilai for t in tokens if t.tipe != TipeToken.ADS and t.tipe != TipeToken.AKHIR_BARIS]
        assert "# Ini komentar" not in token_values
        assert "Ini komentar" not in token_values

    def test_comment_entire_line(self, lexer_factory):
        """Test entire line as comment."""
        source = """
        # Ini baris komentar
        biar x = 5
        """
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Hanya biar, x, =, 5 yang harus ada
        non_meta_tokens = [t for t in tokens if t.tipe not in (TipeToken.ADS, TipeToken.AKHIR_BARIS)]
        assert len(non_meta_tokens) == 4


# ============================================================================
# 6. ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
@pytest.mark.errors
class TestLexerErrors:
    """Test error handling untuk karakter invalid dan format error."""

    def test_invalid_character(self, lexer_factory):
        """Test bahwa karakter invalid menghasilkan token TIDAK_DIKENAL."""
        source = "biar x = 5 @ 10"
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Cari token yang tidak dikenal
        unknown_token = next((t for t in tokens if t.tipe == TipeToken.TIDAK_DIKENAL), None)

        assert unknown_token is not None, "Token TIDAK_DIKENAL tidak ditemukan."
        assert unknown_token.nilai == "@"

    def test_error_has_line_info(self, lexer_factory):
        """Test bahwa token TIDAK_DIKENAL mengandung info baris dan kolom yang benar."""
        source = """
        biar x = 5
        biar y = @
        """
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        unknown_token = next((t for t in tokens if t.tipe == TipeToken.TIDAK_DIKENAL), None)

        assert unknown_token is not None, "Token TIDAK_DIKENAL tidak ditemukan."
        assert unknown_token.baris == 3
        assert unknown_token.kolom is not None # Kolom bisa bervariasi


# ============================================================================
# 7. EDGE CASES & WHITESPACE
# ============================================================================

@pytest.mark.unit
@pytest.mark.lexer
class TestEdgeCases:
    """Test edge cases dan whitespace handling."""

    def test_empty_source(self, lexer_factory):
        """Test bahwa empty source code tidak crash."""
        source = ""
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Hanya ADS token
        assert len(tokens) == 1
        assert tokens[0].tipe == TipeToken.ADS

    def test_whitespace_only(self, lexer_factory):
        """Test bahwa whitespace-only source tidak crash."""
        source = "   \n\t  \n  "
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Hanya AKHIR_BARIS dan ADS tokens
        assert all(t.tipe in (TipeToken.AKHIR_BARIS, TipeToken.ADS) for t in tokens)

    def test_newline_tracking(self, lexer_factory):
        """Test bahwa baris dan kolom di-track dengan benar."""
        source = """biar x = 5
biar y = 10"""
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        # Token 'biar' pertama harus di baris 1
        assert tokens[0].baris == 1

        # Token 'biar' kedua harus di baris 2
        # Cari token 'biar' kedua
        second_biar = [t for t in tokens if t.tipe == TipeToken.BIAR][1]
        assert second_biar.baris == 2

    def test_robustness_whitespace_only_source_returns_valid_list(self, lexer_factory):
        """
        BLOCKER-1 VALIDATION:
        Memastikan input yang hanya berisi spasi/newline mengembalikan list yang valid.
        """
        source = "   \t\n  \n "
        lexer = lexer_factory(source)
        tokens = lexer.buat_token()

        assert isinstance(tokens, list), "Hasil dari input spasi harus berupa list"

        # Harus ada 2 token AKHIR_BARIS dan 1 token ADS
        token_types = [t.tipe for t in tokens]
        assert token_types.count(TipeToken.AKHIR_BARIS) == 2
        assert token_types.count(TipeToken.ADS) == 1
        assert len(tokens) == 3

    def test_robustness_no_return_value_bug(self):
        """
        BLOCKER-1 VALIDATION:
        Test case eksplisit untuk memastikan tidak ada 'return' kosong.
        Ini adalah tes langsung terhadap laporan analis.
        """
        lexer = Leksikal("")
        # Memanggil metode secara langsung
        result = lexer.buat_token()
        # Jika ada 'return' tanpa nilai, result akan menjadi None
        assert result is not None, "buat_token() seharusnya tidak pernah mengembalikan None"
