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
    """Test kasus error dan kondisi tepi."""

    def test_unknown_token_type(self):
        json_token = {"tipe": "TOKEN_TIDAK_DIKENAL"}
        with pytest.raises(ValueError, match="Tipe token tidak diketahui"):
            _json_to_token(json_token)

    def test_unknown_node_type(self):
        json_expr = new_expr_node({"node_type": "TipeNodeTidakDikenal"})
        with pytest.raises(NotImplementedError, match="belum diimplementasikan"):
            _deserialize_expr(json_expr)
