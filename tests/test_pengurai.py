# tests/test_pengurai.py
"""
Unit tests untuk Pengurai (Parser).

Test Categories:
1. Variable Declarations (biar, tetap)
2. Assignments
3. Expressions (arithmetic, logical, comparison)
4. Function Declarations
5. Function Calls
6. Control Flow (jika-maka-akhir)
7. Error Recovery
8. Identifier Validation
"""
import pytest
from morph_engine.pengurai import Pengurai, PenguraiKesalahan
from morph_engine.node_ast import NodeDeklarasiVariabel, NodePengenal, NodeAngka
from morph_engine.token_morph import TipeToken, Token


# ============================================================================
# 1. VARIABLE DECLARATIONS
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestVariableDeclarations:
    """Tes untuk parsing deklarasi variabel (biar dan tetap)."""

    def test_simple_variable_declaration(self, parser_factory):
        """Tes deklarasi variabel sederhana: biar x = 5"""
        source = "biar x = 5"
        parser = parser_factory(source)
        ast = parser.urai()

        # AST harus berisi satu statement
        assert len(ast.daftar_pernyataan) == 1
        stmt = ast.daftar_pernyataan[0]

        # Cek tipe node
        assert isinstance(stmt, NodeDeklarasiVariabel)

        # Cek jenis deklarasi
        assert stmt.jenis_deklarasi.tipe == TipeToken.BIAR

        # Cek nama variabel
        assert isinstance(stmt.nama_variabel, NodePengenal)
        assert stmt.nama_variabel.token.nilai == "x"

        # Cek nilai assignment
        assert isinstance(stmt.nilai, NodeAngka)
        assert stmt.nilai.token.nilai == 5

    def test_constant_variable_declaration(self, parser_factory):
        """Tes deklarasi variabel konstan: tetap PI = 3.14"""
        source = "tetap PI = 3.14"
        parser = parser_factory(source)
        ast = parser.urai()

        stmt = ast.daftar_pernyataan[0]
        assert isinstance(stmt, NodeDeklarasiVariabel)

        assert stmt.jenis_deklarasi.tipe == TipeToken.TETAP
        assert stmt.nama_variabel.token.nilai == "PI"
        assert stmt.nilai.token.nilai == 3.14
