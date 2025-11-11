# tests/test_ocaml_loader.py
"""
Test suite untuk OCaml AST Loader.
Memverifikasi deserialisasi JSON ke Python AST.
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
    _deserialize_stmt
)
from transisi.absolute_sntx_morph import *
from transisi.morph_t import Token, TipeToken


class TestTokenMapping:
    """Test TOKEN_TYPE_MAP completeness."""

    def test_all_basic_tokens_mapped(self):
        """Verify semua token dasar ada di mapping."""
        from transisi.ocaml_loader import TOKEN_TYPE_MAP

        required_tokens = [
            "BIAR", "TETAP", "UBAH", "JIKA", "MAKA", "LAIN",
            "FUNGSI", "KELAS", "KEMBALI", "TULIS", "ANGKA", "NAMA"
        ]

        for token_str in required_tokens:
            assert token_str in TOKEN_TYPE_MAP, f"Token '{token_str}' tidak ada di map"

    def test_token_conversion(self):
        """Test _json_to_token conversion."""
        json_token = {
            "tipe": "ANGKA",
            "nilai": 42,
            "baris": 1,
            "kolom": 5
        }

        token = _json_to_token(json_token)
        assert isinstance(token, Token)
        assert token.tipe == TipeToken.ANGKA
        assert token.nilai == 42
        assert token.baris == 1
        assert token.kolom == 5


class TestBasicExpressions:
    """Test deserialisasi ekspresi sederhana."""

    def test_konstanta_number(self):
        """Test literal number."""
        json_expr = {
            "node_type": "Konstanta",
            "token": {
                "tipe": "ANGKA",
                "nilai": 123,
                "baris": 1,
                "kolom": 1
            }
        }

        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, Konstanta)
        assert expr.nilai == 123

    def test_identitas(self):
        """Test variable identifier."""
        json_expr = {
            "node_type": "Identitas",
            "token": {
                "tipe": "NAMA",
                "nilai": "x",
                "baris": 1,
                "kolom": 1
            }
        }

        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, Identitas)
        assert expr.nama == "x"

    def test_binary_operation(self):
        """Test binary arithmetic operation."""
        json_expr = {
            "node_type": "FoxBinary",
            "kiri": {
                "node_type": "Konstanta",
                "token": {"tipe": "ANGKA", "nilai": 10, "baris": 1, "kolom": 1}
            },
            "operator": {
                "tipe": "PLUS",
                "nilai": "+",
                "baris": 1,
                "kolom": 3
            },
            "kanan": {
                "node_type": "Konstanta",
                "token": {"tipe": "ANGKA", "nilai": 20, "baris": 1, "kolom": 5}
            }
        }

        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, FoxBinary)
        assert isinstance(expr.kiri, Konstanta)
        assert isinstance(expr.kanan, Konstanta)
        assert expr.op.tipe == TipeToken.TAMBAH

    def test_unary_operation(self):
        """Test unary operation (negation)."""
        json_expr = {
            "node_type": "FoxUnary",
            "operator": {"tipe": "MINUS", "nilai": "-", "baris": 1, "kolom": 1},
            "kanan": {
                "node_type": "Konstanta",
                "token": {"tipe": "ANGKA", "nilai": 5, "baris": 1, "kolom": 2}
            }
        }
        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, FoxUnary)
        assert expr.op.tipe == TipeToken.KURANG
        assert isinstance(expr.kanan, Konstanta)

    def test_daftar_literal(self):
        """Test list literal [1, "dua"]."""
        json_expr = {
            "node_type": "Daftar",
            "elemen": [
                {"node_type": "Konstanta", "token": {"tipe": "ANGKA", "nilai": 1, "baris": 1, "kolom": 2}},
                {"node_type": "Konstanta", "token": {"tipe": "TEKS", "nilai": "dua", "baris": 1, "kolom": 5}}
            ]
        }
        expr = _deserialize_expr(json_expr)
        assert isinstance(expr, Daftar)
        assert len(expr.elemen) == 2
        assert isinstance(expr.elemen[0], Konstanta)
        assert expr.elemen[1].nilai == "dua"


class TestStatements:
    """Test deserialisasi pernyataan."""

    def test_variable_declaration(self):
        """Test 'biar x = 10'."""
        json_stmt = {
            "node_type": "DeklarasiVariabel",
            "jenis_deklarasi": {
                "tipe": "BIAR",
                "nilai": "biar",
                "baris": 1,
                "kolom": 1
            },
            "nama": {
                "tipe": "NAMA",
                "nilai": "x",
                "baris": 1,
                "kolom": 6
            },
            "nilai": {
                "node_type": "Konstanta",
                "token": {"tipe": "ANGKA", "nilai": 10, "baris": 1, "kolom": 10}
            }
        }

        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, DeklarasiVariabel)
        assert stmt.nama.nilai == "x"
        assert isinstance(stmt.nilai, Konstanta)

    def test_tulis_statement(self):
        """Test 'tulis(x, y)'."""
        json_stmt = {
            "node_type": "Tulis",
            "argumen": [
                {
                    "node_type": "Identitas",
                    "token": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 7}
                },
                {
                    "node_type": "Identitas",
                    "token": {"tipe": "NAMA", "nilai": "y", "baris": 1, "kolom": 10}
                }
            ]
        }

        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, Tulis)
        assert len(stmt.argumen) == 2

    def test_assignment(self):
        """Test 'ubah x = 20'."""
        json_stmt = {
            "node_type": "Assignment",
            "nama": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 6},
            "nilai": {
                "node_type": "Konstanta",
                "token": {"tipe": "ANGKA", "nilai": 20, "baris": 1, "kolom": 10}
            }
        }
        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, Assignment)
        assert stmt.nama.nilai == "x"
        assert isinstance(stmt.nilai, Konstanta)


class TestControlFlow:
    """Test control flow structures."""

    def test_if_statement_full(self):
        """Test if-then-elif-else."""
        json_stmt = {
            "node_type": "JikaMaka",
            "kondisi": {"node_type": "Konstanta", "token": {"tipe": "SALAH", "nilai": False, "baris": 1, "kolom": 5}},
            "blok_maka": {"body": []},
            "rantai_lain_jika": [
                {
                    "kondisi": {"node_type": "Konstanta", "token": {"tipe": "BENAR", "nilai": True, "baris": 3, "kolom": 12}},
                    "blok": {"body": [{"node_type": "PernyataanEkspresi", "ekspresi": {"node_type": "Konstanta", "token": {"tipe": "ANGKA", "nilai": 1}}}]}
                }
            ],
            "blok_lain": {"body": [{"node_type": "PernyataanEkspresi", "ekspresi": {"node_type": "Konstanta", "token": {"tipe": "ANGKA", "nilai": 2}}}]}
        }

        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, JikaMaka)
        assert len(stmt.rantai_lain_jika) == 1
        assert stmt.blok_lain is not None
        assert isinstance(stmt.blok_lain, Bagian)


class TestFunctions:
    """Test function declarations and calls."""

    def test_function_declaration(self):
        """Test 'fungsi tambah(a, b) maka ... akhir'."""
        json_stmt = {
            "node_type": "FungsiDeklarasi",
            "nama": {"tipe": "NAMA", "nilai": "tambah", "baris": 1, "kolom": 8},
            "parameter": [
                {"tipe": "NAMA", "nilai": "a", "baris": 1, "kolom": 15},
                {"tipe": "NAMA", "nilai": "b", "baris": 1, "kolom": 18}
            ],
            "badan": {
                "body": [
                    {
                        "node_type": "PernyataanKembalikan",
                        "kata_kunci": {"tipe": "KEMBALI", "nilai": "kembali", "baris": 2, "kolom": 3},
                        "nilai": {
                            "node_type": "FoxBinary",
                            "kiri": {
                                "node_type": "Identitas",
                                "token": {"tipe": "NAMA", "nilai": "a", "baris": 2, "kolom": 11}
                            },
                            "operator": {"tipe": "PLUS", "nilai": "+", "baris": 2, "kolom": 13},
                            "kanan": {
                                "node_type": "Identitas",
                                "token": {"tipe": "NAMA", "nilai": "b", "baris": 2, "kolom": 15}
                            }
                        }
                    }
                ]
            }
        }

        stmt = _deserialize_stmt(json_stmt)
        assert isinstance(stmt, FungsiDeklarasi)
        assert stmt.nama.nilai == "tambah"
        assert len(stmt.parameter) == 2


class TestIntegration:
    """Integration tests dengan full programs."""

    def test_load_from_json_file(self):
        """Test loading AST dari JSON file."""
        json_data = {
            "ast": {
                "body": [
                    {
                        "node_type": "DeklarasiVariabel",
                        "jenis_deklarasi": {"tipe": "BIAR", "nilai": "biar", "baris": 1, "kolom": 1},
                        "nama": {"tipe": "NAMA", "nilai": "hasil", "baris": 1, "kolom": 6},
                        "nilai": {
                            "node_type": "FoxBinary",
                            "kiri": {
                                "node_type": "Konstanta",
                                "token": {"tipe": "ANGKA", "nilai": 5, "baris": 1, "kolom": 14}
                            },
                            "operator": {"tipe": "BINTANG", "nilai": "*", "baris": 1, "kolom": 16},
                            "kanan": {
                                "node_type": "Konstanta",
                                "token": {"tipe": "ANGKA", "nilai": 3, "baris": 1, "kolom": 18}
                            }
                        }
                    },
                    {
                        "node_type": "Tulis",
                        "argumen": [
                            {
                                "node_type": "Identitas",
                                "token": {"tipe": "NAMA", "nilai": "hasil", "baris": 2, "kolom": 7}
                            }
                        ]
                    }
                ]
            }
        }

        # Simpan ke temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            # Load AST
            ast = load_compiled_ast(temp_path)

            # Verify structure
            assert isinstance(ast, Bagian)
            assert len(ast.daftar_pernyataan) == 2
            assert isinstance(ast.daftar_pernyataan[0], DeklarasiVariabel)
            assert isinstance(ast.daftar_pernyataan[1], Tulis)
        finally:
            # Cleanup
            Path(temp_path).unlink()


class TestErrorHandling:
    """Test error cases dan edge conditions."""

    def test_unknown_token_type(self):
        """Test handling unknown token type."""
        json_token = {
            "tipe": "UNKNOWN_TOKEN_XYZ",
            "nilai": "?",
            "baris": 1,
            "kolom": 1
        }

        with pytest.raises(ValueError, match="Tipe token tidak diketahui"):
            _json_to_token(json_token)

    def test_unknown_node_type(self):
        """Test handling unknown node type."""
        json_expr = {
            "node_type": "UnknownNodeType",
            "some_field": "value"
        }

        with pytest.raises(NotImplementedError, match="belum diimplementasikan"):
            _deserialize_expr(json_expr)


# ============================================================================
# SMOKE TESTS - Quick validation per iteration
# ============================================================================

def smoke_test_iteration_1():
    """Quick test for Iteration 1 (Literals & Basic Ops)."""
    print("🔥 Running Smoke Test: Iteration 1...")

    json_expr = {
        "node_type": "FoxBinary",
        "kiri": {
            "node_type": "Konstanta",
            "token": {"tipe": "ANGKA", "nilai": 10, "baris": 1, "kolom": 1}
        },
        "operator": {"tipe": "PLUS", "nilai": "+", "baris": 1, "kolom": 3},
        "kanan": {
            "node_type": "Konstanta",
            "token": {"tipe": "ANGKA", "nilai": 5, "baris": 1, "kolom": 5}
        }
    }

    expr = _deserialize_expr(json_expr)
    assert isinstance(expr, FoxBinary)
    print("✅ Iteration 1 smoke test PASSED")


def smoke_test_iteration_2():
    """Quick test for Iteration 2 (Control Flow)."""
    print("🔥 Running Smoke Test: Iteration 2...")

    json_stmt = {
        "node_type": "JikaMaka",
        "kondisi": {
            "node_type": "Konstanta",
            "token": {"tipe": "BENAR", "nilai": True, "baris": 1, "kolom": 5}
        },
        "blok_maka": {"body": []},
        "rantai_lain_jika": [],
        "blok_lain": None
    }

    stmt = _deserialize_stmt(json_stmt)
    assert isinstance(stmt, JikaMaka)
    print("✅ Iteration 2 smoke test PASSED")


def smoke_test_iteration_3():
    """Quick test for Iteration 3 (Functions & Classes)."""
    print("🔥 Running Smoke Test: Iteration 3...")

    json_stmt = {
        "node_type": "FungsiDeklarasi",
        "nama": {"tipe": "NAMA", "nilai": "tesFungsi", "baris": 1, "kolom": 8},
        "parameter": [],
        "badan": { "body": [] }
    }

    stmt = _deserialize_stmt(json_stmt)
    assert isinstance(stmt, FungsiDeklarasi)
    assert stmt.nama.nilai == "tesFungsi"
    print("✅ Iteration 3 smoke test PASSED")


def smoke_test_iteration_4():
    """Quick test for Iteration 4 (Advanced Features)."""
    print("🔥 Running Smoke Test: Iteration 4...")

    json_stmt = {
        "node_type": "Jodohkan",
        "ekspresi": {
            "node_type": "Identitas",
            "token": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 1}
        },
        "kasus": [
            {
                "pola": {
                    "node_type": "PolaWildcard",
                    "token": {"tipe": "GARIS_PEMISAH", "nilai": "_", "baris": 2, "kolom": 3}
                },
                "badan": {"body": []}
            }
        ]
    }

    stmt = _deserialize_stmt(json_stmt)
    assert isinstance(stmt, Jodohkan)
    assert len(stmt.kasus) == 1
    assert isinstance(stmt.kasus[0].pola, PolaWildcard)
    print("✅ Iteration 4 smoke test PASSED")


if __name__ == "__main__":
    # Quick manual testing
    print("=" * 60)
    print("MANUAL SMOKE TESTS")
    print("=" * 60)

    try:
        smoke_test_iteration_1()
        smoke_test_iteration_2()
        smoke_test_iteration_3()
        smoke_test_iteration_4()
        print("\n✅ All smoke tests passed!")
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
