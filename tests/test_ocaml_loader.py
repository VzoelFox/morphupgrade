# tests/test_ocaml_loader.py
"""
Test suite untuk OCaml AST Loader.
Memverifikasi deserialisasi dari skema JSON BARU ke Python AST.
"""

import pytest
import json
import tempfile
from pathlib import Path

from transisi.ocaml_loader import (
    load_compiled_ast,
    deserialize_ast,
    _json_to_token,
    _deserialize_expr,
    _deserialize_stmt,
    _json_to_konstanta,
    TOKEN_TYPE_MAP,
)
from transisi.absolute_sntx_morph import *
from transisi.morph_t import Token, TipeToken


# Helper untuk membuat struktur node JSON yang baru
def new_expr_node(desc: dict):
    return {"deskripsi": desc, "lokasi": {"mulai": {}, "akhir": {}}}

def new_stmt_node(desc: dict):
    return {"deskripsi": desc, "lokasi": {"mulai": {}, "akhir": {}}}

class TestTokenAndLiteralConversion:
    """Test konversi token dan literal dari JSON."""

    def test_token_conversion(self):
        """Test _json_to_token conversion for a simple token."""
        json_token = {"tipe": "PLUS", "nilai": None, "baris": 1, "kolom": 5}
        token = _json_to_token(json_token)
        assert isinstance(token, Token)
        assert token.tipe == TipeToken.TAMBAH
        assert token.nilai is None

    def test_token_map_completeness(self):
        """
        Test Patch 1.3: Memastikan semua token OCaml yang umum memiliki
        pemetaan di TOKEN_TYPE_MAP.
        """
        # Daftar ini harus disinkronkan dengan parser.mly di sisi OCaml
        expected_ocaml_tokens = {
            # Keywords
            "BIAR", "TETAP", "UBAH", "JIKA", "MAKA", "LAIN", "AKHIR",
            "SELAMA", "FUNGSI", "KEMBALI", "KEMBALIKAN", "TULIS",
            # Operators
            "PLUS", "MINUS", "BINTANG", "GARIS_MIRING", "PANGKAT", "PERSEN",
            "EQUAL", "SAMA_DENGAN", "TIDAK_SAMA", "KURANG_DARI", "KURANG_SAMA",
            "LEBIH_DARI", "LEBIH_SAMA", "DAN", "ATAU", "TIDAK",
            # Literals & Identifiers
            "ANGKA", "TEKS", "BENAR", "SALAH", "NIL", "NAMA",
            # Delimiters
            "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "KOMA", "TITIK_KOMA",
        }

        missing_tokens = expected_ocaml_tokens - set(TOKEN_TYPE_MAP.keys())

        assert not missing_tokens, (
            f"Token OCaml berikut hilang dari TOKEN_TYPE_MAP: {sorted(list(missing_tokens))}"
        )

    def test_konstanta_conversion(self):
        """Test _json_to_konstanta untuk semua tipe literal."""
        # Angka
        lit_angka = {"tipe": "angka", "nilai": 123.0}
        konst_angka = _json_to_konstanta(lit_angka)
        assert isinstance(konst_angka, Konstanta)
        assert konst_angka.token.tipe == TipeToken.ANGKA
        assert konst_angka.token.nilai == 123.0

        # Teks
        lit_teks = {"tipe": "teks", "nilai": "hello"}
        konst_teks = _json_to_konstanta(lit_teks)
        assert konst_teks.token.tipe == TipeToken.TEKS
        assert konst_teks.token.nilai == "hello"

        # Boolean
        lit_benar = {"tipe": "boolean", "nilai": True}
        konst_benar = _json_to_konstanta(lit_benar)
        assert konst_benar.token.tipe == TipeToken.BENAR
        assert konst_benar.token.nilai is True

        # Nil
        lit_nil = {"tipe": "nil", "nilai": None}
        konst_nil = _json_to_konstanta(lit_nil)
        assert konst_nil.token.tipe == TipeToken.NIL
        assert konst_nil.token.nilai is None


class TestBasicExpressions:
    """Test deserialisasi ekspresi sederhana dengan skema baru."""

    def test_konstanta_number(self):
        json_expr = new_expr_node({
            "node_type": "konstanta",
            "literal": {"tipe": "angka", "nilai": 123.0}
        })
        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, Konstanta)
        assert expr.token.nilai == 123.0

    def test_identitas(self):
        json_expr = new_expr_node({
            "node_type": "identitas",
            "token": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 1}
        })
        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, Identitas)
        assert expr.token.nilai == "x"

    def test_binary_operation(self):
        json_expr = new_expr_node({
            "node_type": "fox_binary",
            "kiri": new_expr_node({"node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 10.0}}),
            "operator": {"tipe": "PLUS"},
            "kanan": new_expr_node({"node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 20.0}})
        })
        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, FoxBinary)
        assert isinstance(expr.kiri, Konstanta)
        assert isinstance(expr.kanan, Konstanta)
        assert expr.op.tipe == TipeToken.TAMBAH

class TestStatements:
    """Test deserialisasi pernyataan dengan skema baru."""

    def test_variable_declaration(self):
        json_stmt = new_stmt_node({
            "node_type": "deklarasi_variabel",
            "jenis_deklarasi": {"tipe": "BIAR"},
            "nama": {"tipe": "NAMA", "nilai": "x"},
            "nilai": new_expr_node({"node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 10.0}})
        })
        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, DeklarasiVariabel)
        assert stmt.nama.nilai == "x"
        assert isinstance(stmt.nilai, Konstanta)

    def test_tulis_statement(self):
        json_stmt = new_stmt_node({
            "node_type": "tulis",
            "argumen": [
                new_expr_node({"node_type": "identitas", "token": {"tipe": "NAMA", "nilai": "x"}})
            ]
        })
        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, Tulis)
        assert len(stmt.argumen) == 1
        assert isinstance(stmt.argumen[0], Identitas)


class TestIntegration:
    """Test deserialisasi program lengkap."""

    def test_deserialize_ast_from_dict(self):
        json_data = {
            "version": "0.1.0",
            "program": {
                "body": [
                    new_stmt_node({
                        "node_type": "deklarasi_variabel",
                        "jenis_deklarasi": {"tipe": "BIAR"},
                        "nama": {"tipe": "NAMA", "nilai": "hasil"},
                        "nilai": new_expr_node({
                            "node_type": "fox_binary",
                            "kiri": new_expr_node({"node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 5.0}}),
                            "operator": {"tipe": "BINTANG"},
                            "kanan": new_expr_node({"node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 3.0}})
                        })
                    })
                ]
            }
        }

        ast_root = deserialize_ast(json_data)
        assert isinstance(ast_root, Bagian)
        assert len(ast_root.daftar_pernyataan) == 1
        stmt = ast_root.daftar_pernyataan[0]
        assert isinstance(stmt, DeklarasiVariabel)
        assert stmt.nama.nilai == "hasil"


class TestErrorHandling:
    """Test kasus error dan kondisi tepi (regresi dasar)."""

    def test_token_unknown_type_error_legacy(self):
        """Memastikan error dinaikkan jika fallback gagal."""
        with pytest.raises(ValueError, match="tidak diketahui dan tidak bisa di-fallback"):
            # Token ini tidak bisa fallback karena nilainya bukan string
            _json_to_token({"tipe": "INVALID_TOKEN", "nilai": None})

    def test_missing_program_field_legacy(self):
        """Test validasi struktur JSON dasar."""
        with pytest.raises(ValueError, match="Struktur JSON tidak valid"):
            deserialize_ast({})

    def test_unknown_node_type_legacy(self):
        """Memastikan error yang jelas untuk node yang tidak diimplementasikan."""
        json_expr = new_expr_node({"node_type": "TipeNodeTidakDikenal"})
        with pytest.raises(NotImplementedError, match="belum diimplementasikan"):
            _deserialize_expr(json_expr)

    def test_numeric_conversion_edge_cases(self, subtests):
        """Test Patch 1.1: Memverifikasi semua kasus konversi numerik."""
        cases = {
            "String Integer": {"tipe": "angka", "nilai": "42"},
            "String Float": {"tipe": "angka", "nilai": "3.14"},
            "String Zero": {"tipe": "angka", "nilai": "0"},
            "String Negative": {"tipe": "angka", "nilai": "-5"},
            "Direct Integer": {"tipe": "angka", "nilai": 100},
            "Direct Float": {"tipe": "angka", "nilai": -20.5},
        }

        expected_values = {
            "String Integer": 42,
            "String Float": 3.14,
            "String Zero": 0,
            "String Negative": -5,
            "Direct Integer": 100,
            "Direct Float": -20.5,
        }

        for name, json_input in cases.items():
            with subtests.test(msg=name):
                konstanta = _json_to_konstanta(json_input)
                assert konstanta.token.nilai == expected_values[name]
                assert isinstance(konstanta.token.nilai, (int, float))
