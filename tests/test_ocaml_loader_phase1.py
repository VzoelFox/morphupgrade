# tests/test_ocaml_loader_phase1.py
import pytest
import json
import logging
from transisi.ocaml_loader import (
    _json_to_konstanta, _json_to_token,
    deserialize_ast, _validate_json_structure
)
from transisi.morph_t import TipeToken, Token


class TestNumericConversion:
    """Test Patch 1.1: Konversi tipe numerik yang kuat"""

    def test_integer_from_string(self):
        literal = {"tipe": "angka", "nilai": "42"}
        result = _json_to_konstanta(literal)
        assert result.token.nilai == 42
        assert isinstance(result.token.nilai, int)

    def test_float_from_string(self):
        literal = {"tipe": "angka", "nilai": "3.14"}
        result = _json_to_konstanta(literal)
        assert result.token.nilai == 3.14
        assert isinstance(result.token.nilai, float)

    def test_integer_direct(self):
        literal = {"tipe": "angka", "nilai": 100}
        result = _json_to_konstanta(literal)
        assert result.token.nilai == 100

    def test_float_direct(self):
        literal = {"tipe": "angka", "nilai": 2.718}
        result = _json_to_konstanta(literal)
        assert result.token.nilai == 2.718

    def test_zero_edge_cases(self):
        assert _json_to_konstanta({"tipe": "angka", "nilai": "0"}).token.nilai == 0
        assert _json_to_konstanta({"tipe": "angka", "nilai": 0}).token.nilai == 0
        assert _json_to_konstanta({"tipe": "angka", "nilai": 0.0}).token.nilai == 0
        assert _json_to_konstanta({"tipe": "angka", "nilai": "-0"}).token.nilai == 0

    def test_negative_numbers(self):
        assert _json_to_konstanta({"tipe": "angka", "nilai": "-5"}).token.nilai == -5
        assert _json_to_konstanta({"tipe": "angka", "nilai": -5}).token.nilai == -5

    def test_scientific_notation(self):
        literal = {"tipe": "angka", "nilai": "1.5e3"}
        result = _json_to_konstanta(literal)
        assert result.token.nilai == 1500.0

        literal_neg = {"tipe": "angka", "nilai": "1.23e-4"}
        result_neg = _json_to_konstanta(literal_neg)
        assert result_neg.token.nilai == 0.000123

    def test_invalid_numeric_format(self):
        with pytest.raises(ValueError, match="format tidak valid"):
            _json_to_konstanta({"tipe": "angka", "nilai": "not_a_number"})

    def test_invalid_numeric_type(self):
        with pytest.raises(TypeError, match="harus berupa number atau string"):
            _json_to_konstanta({"tipe": "angka", "nilai": ["list"]})

    def test_special_float_values(self, caplog):
        caplog.set_level(logging.WARNING)
        inf_literal = {"tipe": "angka", "nilai": "inf"}
        result_inf = _json_to_konstanta(inf_literal)
        assert result_inf.token.nilai == float('inf')
        assert "Nilai numerik khusus terdeteksi: inf" in caplog.text


class TestTokenMapping:
    """Test Patch 1.3: Pemetaan tipe token yang lengkap"""

    def test_basic_keyword_tokens(self):
        token = _json_to_token({"tipe": "BIAR", "nilai": "biar", "baris": 1, "kolom": 0})
        assert token.tipe == TipeToken.BIAR

    def test_operator_tokens(self):
        token = _json_to_token({"tipe": "PLUS", "nilai": "+", "baris": 1, "kolom": 5})
        assert token.tipe == TipeToken.TAMBAH

    def test_delimiter_tokens(self):
        token = _json_to_token({"tipe": "LPAREN", "nilai": "(", "baris": 2, "kolom": 10})
        assert token.tipe == TipeToken.KURUNG_BUKA

    def test_unknown_token_fallback(self, caplog):
        caplog.set_level(logging.INFO)
        # Harus fallback ke NAMA untuk token seperti identifier
        token_data = {"tipe": "UNKNOWN_TYPE", "nilai": "some_var", "baris": 1, "kolom": 0}
        token = _json_to_token(token_data)
        assert token.tipe == TipeToken.NAMA
        assert "memperlakukan 'UNKNOWN_TYPE' sebagai TipeToken.NAMA" in caplog.text

    def test_unknown_token_no_fallback(self):
        # Harus gagal untuk token non-identifier
        with pytest.raises(ValueError, match="tidak diketahui dan tidak bisa di-fallback"):
            _json_to_token({
                "tipe": "WEIRD_OPERATOR",
                "nilai": None,  # Tidak ada nilai string = tidak bisa fallback
                "baris": 1,
                "kolom": 0
            })


class TestLogging:
    """Test Patch 1.2: Infrastruktur logging"""

    def test_logger_exists(self):
        from transisi.log_setup import logger
        assert logger is not None
        assert logger.name == "morph"

    def test_log_level_from_env(self, monkeypatch, caplog):
        caplog.set_level(logging.DEBUG)
        monkeypatch.setenv("MORPH_LOG_LEVEL", "DEBUG")
        # Impor ulang untuk mengambil env var
        import importlib
        import transisi.log_setup
        importlib.reload(transisi.log_setup)

        from transisi.log_setup import logger
        assert logger.level == logging.DEBUG

        # Periksa apakah pesan inisialisasi tertangkap
        init_messages = [rec.message for rec in caplog.records if "diinisialisasi" in rec.message]
        assert len(init_messages) > 0
        assert "Logger diinisialisasi: level=DEBUG" in init_messages[0]


class TestStructuralValidation:
    """Test validasi struktur JSON dasar"""

    def test_valid_structure(self):
        data = {"program": {"body": []}}
        issues = _validate_json_structure(data)
        assert issues == []

    def test_missing_program_field(self):
        data = {"other": "stuff"}
        issues = _validate_json_structure(data)
        assert "program" in issues[0].lower()

    def test_missing_body_field(self):
        data = {"program": {"wrong_key": []}}
        issues = _validate_json_structure(data)
        assert "body" in issues[0].lower()

    def test_body_wrong_type(self):
        data = {"program": {"body": "not_a_list"}}
        issues = _validate_json_structure(data)
        assert "list" in issues[0].lower()


class TestIntegrationBasic:
    """Tes integrasi dasar untuk deserialisasi penuh"""

    def test_simple_variable_declaration(self):
        json_data = {
            "version": "0.1.0",
            "program": {
                "body": [
                    {
                        "lokasi": {},
                        "deskripsi": {
                            "node_type": "deklarasi_variabel",
                            "jenis_deklarasi": {"tipe": "BIAR", "nilai": "biar", "baris": 1, "kolom": 0},
                            "nama": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 5},
                            "nilai": {
                                "lokasi": {},
                                "deskripsi": {
                                    "node_type": "konstanta",
                                    "literal": {"tipe": "angka", "nilai": 42}
                                }
                            }
                        }
                    }
                ]
            }
        }

        ast = deserialize_ast(json_data)
        assert len(ast.daftar_pernyataan) == 1
        assert ast.daftar_pernyataan[0].nama.nilai == "x"
        assert ast.daftar_pernyataan[0].nilai.token.nilai == 42
