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
from morph_engine.node_ast import NodeDeklarasiVariabel, NodePengenal, NodeAngka, NodeProgram
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

# ============================================================================
# 6. CONTROL FLOW
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestControlFlow:
    """Tes untuk parsing struktur kontrol (jika-maka-lain)."""

    def test_simple_if_statement(self, parser_factory):
        """Tes 'jika <kondisi> maka ... akhir'."""
        source = """
        jika x > 10 maka
            tulis("besar")
        akhir
        """
        parser = parser_factory(source)
        ast = parser.urai()

        assert not parser.daftar_kesalahan
        assert len(ast.daftar_pernyataan) == 1
        stmt = ast.daftar_pernyataan[0]

        from morph_engine.node_ast import NodeJikaMaka, NodeOperasiBiner
        assert isinstance(stmt, NodeJikaMaka)
        assert isinstance(stmt.kondisi, NodeOperasiBiner)
        assert len(stmt.blok_maka) == 1
        assert not stmt.rantai_lain_jika
        assert stmt.blok_lain is None

    def test_if_else_statement(self, parser_factory):
        """Tes 'jika <kondisi> maka ... lain ... akhir'."""
        source = """
        jika suhu <= 0 maka
            tulis("beku")
        lain
            tulis("cair")
        akhir
        """
        parser = parser_factory(source)
        ast = parser.urai()

        assert not parser.daftar_kesalahan
        stmt = ast.daftar_pernyataan[0]

        from morph_engine.node_ast import NodeJikaMaka
        assert isinstance(stmt, NodeJikaMaka)
        assert len(stmt.blok_maka) == 1
        assert not stmt.rantai_lain_jika
        assert stmt.blok_lain is not None
        assert len(stmt.blok_lain) == 1

    def test_if_elseif_else_statement(self, parser_factory):
        """Tes 'jika ... lain jika ... lain ... akhir'."""
        source = """
        jika nilai > 90 maka
            tulis("A")
        lain jika nilai > 80 maka
            tulis("B")
        lain
            tulis("C")
        akhir
        """
        parser = parser_factory(source)
        ast = parser.urai()

        assert not parser.daftar_kesalahan
        stmt = ast.daftar_pernyataan[0]

        from morph_engine.node_ast import NodeJikaMaka
        assert isinstance(stmt, NodeJikaMaka)
        assert len(stmt.blok_maka) == 1
        assert len(stmt.rantai_lain_jika) == 1
        assert stmt.blok_lain is not None
        assert len(stmt.blok_lain) == 1

        # Cek kondisi di 'lain jika'
        kondisi_lain_jika, _ = stmt.rantai_lain_jika[0]
        from morph_engine.node_ast import NodeOperasiBiner
        assert isinstance(kondisi_lain_jika, NodeOperasiBiner)

    def test_nested_if_statement(self, parser_factory):
        """Tes pernyataan 'jika' di dalam 'jika'."""
        source = """
        jika a > 0 maka
            jika b > 0 maka
                tulis("keduanya positif")
            akhir
        akhir
        """
        parser = parser_factory(source)
        ast = parser.urai()

        assert not parser.daftar_kesalahan
        outer_if = ast.daftar_pernyataan[0]

        from morph_engine.node_ast import NodeJikaMaka
        assert isinstance(outer_if, NodeJikaMaka)
        assert len(outer_if.blok_maka) == 1

        inner_if = outer_if.blok_maka[0]
        assert isinstance(inner_if, NodeJikaMaka)
        assert len(inner_if.blok_maka) == 1

# ============================================================================
# 7. Parser Integrity Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestParserIntegrity:
    """Tes untuk memastikan integritas parser dalam kasus-kasus khusus."""

    def test_parse_empty_source_returns_empty_program_node(self, parser_factory):
        """
        BLOCKER-3 VALIDATION:
        Memastikan parser menghasilkan NodeProgram yang valid (tapi kosong)
        saat tidak ada token selain ADS.
        """
        parser = parser_factory("") # Input kosong
        ast = parser.urai()

        assert isinstance(ast, NodeProgram), "Hasil harus selalu berupa NodeProgram"
        assert len(ast.daftar_pernyataan) == 0, "Daftar pernyataan harus kosong"
        assert not parser.daftar_kesalahan, "Tidak boleh ada kesalahan untuk input kosong"
