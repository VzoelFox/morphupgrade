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
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken


# Helper untuk menjalankan pipeline lexer -> parser
def parse_source(source: str) -> ast.Bagian | None:
    lexer = Leksikal(source)
    tokens, lex_errors = lexer.buat_token()
    if lex_errors:
        pytest.fail(f"Lexer errors found: {lex_errors}")

    parser = Pengurai(tokens)
    program = parser.urai()
    if parser.daftar_kesalahan:
        pytest.fail(f"Parser errors found: {parser.daftar_kesalahan}")

    return program

# ============================================================================
# 1. VARIABLE DECLARATIONS
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestVariableDeclarations:
    """Tes untuk parsing deklarasi variabel (biar dan tetap)."""

    def test_simple_variable_declaration(self):
        """Tes deklarasi variabel sederhana: biar x = 5"""
        source = "biar x = 5"
        program = parse_source(source)

        assert program is not None
        assert len(program.daftar_pernyataan) == 1
        stmt = program.daftar_pernyataan[0]

        assert isinstance(stmt, ast.DeklarasiVariabel)
        assert stmt.jenis_deklarasi.tipe == TipeToken.BIAR
        assert stmt.nama.nilai == "x"
        assert isinstance(stmt.nilai, ast.Konstanta)
        assert stmt.nilai.nilai == 5

    def test_constant_variable_declaration(self):
        """Tes deklarasi variabel konstan: tetap PI = 3.14"""
        source = "tetap PI = 3.14"
        program = parse_source(source)

        assert program is not None
        stmt = program.daftar_pernyataan[0]
        assert isinstance(stmt, ast.DeklarasiVariabel)
        assert stmt.jenis_deklarasi.tipe == TipeToken.TETAP
        assert stmt.nama.nilai == "PI"
        assert stmt.nilai.nilai == 3.14

# ============================================================================
# 6. CONTROL FLOW
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestControlFlow:
    """Tes untuk parsing struktur kontrol (jika-maka-lain)."""

    def test_simple_if_statement(self):
        """Tes 'jika <kondisi> maka ... akhir'."""
        source = """
        jika x > 10 maka
            tulis("besar")
        akhir
        """
        program = parse_source(source)

        assert program is not None
        assert len(program.daftar_pernyataan) == 1
        stmt = program.daftar_pernyataan[0]

        assert isinstance(stmt, ast.JikaMaka)
        assert isinstance(stmt.kondisi, ast.FoxBinary)
        assert len(stmt.blok_maka.daftar_pernyataan) == 1
        assert not stmt.rantai_lain_jika
        assert stmt.blok_lain is None

    def test_if_else_statement(self):
        """Tes 'jika <kondisi> maka ... lain ... akhir'."""
        source = """
        jika x < 10 maka
            tulis("kecil")
        lain
            tulis("besar")
        akhir
        """
        program = parse_source(source)
        assert program is not None
        stmt = program.daftar_pernyataan[0]

        assert isinstance(stmt, ast.JikaMaka)
        assert len(stmt.blok_maka.daftar_pernyataan) == 1
        assert not stmt.rantai_lain_jika
        assert stmt.blok_lain is not None
        assert len(stmt.blok_lain.daftar_pernyataan) == 1

    def test_if_elif_else_statement(self):
        """Tes 'jika ... lain jika ... lain ... akhir'."""
        source = """
        jika x < 0 maka
            tulis("negatif")
        lain jika x == 0 maka
            tulis("nol")
        lain
            tulis("positif")
        akhir
        """
        program = parse_source(source)
        assert program is not None
        stmt = program.daftar_pernyataan[0]

        assert isinstance(stmt, ast.JikaMaka)
        assert len(stmt.blok_maka.daftar_pernyataan) == 1
        assert len(stmt.rantai_lain_jika) == 1
        assert stmt.blok_lain is not None
        assert len(stmt.blok_lain.daftar_pernyataan) == 1

# ============================================================================
# 7. Parser Integrity Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parser
class TestParserIntegrity:
    """Tes untuk memastikan integritas parser dalam kasus-kasus khusus."""

    def test_parse_empty_source_returns_empty_program_node(self):
        """
        Memastikan parser menghasilkan NodeProgram yang valid (tapi kosong)
        saat tidak ada token selain ADS.
        """
        program = parse_source("") # Input kosong

        assert isinstance(program, ast.Bagian), "Hasil harus selalu berupa ast.Bagian"
        assert len(program.daftar_pernyataan) == 0, "Daftar pernyataan harus kosong"
