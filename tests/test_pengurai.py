# tests/test_pengurai.py
"""
Unit tests untuk Pengurai (Parser).
"""
import pytest
from morph_engine.crusher import Pengurai, PenguraiKesalahan
from morph_engine.absolute_sntx_morph import DeklarasiVariabel, Identitas, Konstanta, Bagian
from morph_engine.morph_t import TipeToken, Token


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
        assert isinstance(stmt, DeklarasiVariabel)

        # Cek jenis deklarasi
        assert stmt.jenis_deklarasi.tipe == TipeToken.BIAR

        # Cek nama variabel
        assert isinstance(stmt.nama_variabel, Identitas)
        assert stmt.nama_variabel.token.nilai == "x"

        # Cek nilai assignment
        assert isinstance(stmt.nilai, Konstanta)
        assert stmt.nilai.token.nilai == 5

    def test_constant_variable_declaration(self, parser_factory):
        """Tes deklarasi variabel konstan: tetap PI = 3.14"""
        source = "tetap PI = 3.14"
        parser = parser_factory(source)
        ast = parser.urai()

        stmt = ast.daftar_pernyataan[0]
        assert isinstance(stmt, DeklarasiVariabel)

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

        from morph_engine.absolute_sntx_morph import Jika_Maka, FoxBinary
        assert isinstance(stmt, Jika_Maka)
        assert isinstance(stmt.kondisi, FoxBinary)
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

        from morph_engine.absolute_sntx_morph import Jika_Maka
        assert isinstance(stmt, Jika_Maka)
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

        from morph_engine.absolute_sntx_morph import Jika_Maka
        assert isinstance(stmt, Jika_Maka)
        assert len(stmt.blok_maka) == 1
        assert len(stmt.rantai_lain_jika) == 1
        assert stmt.blok_lain is not None
        assert len(stmt.blok_lain) == 1

        # Cek kondisi di 'lain jika'
        kondisi_lain_jika, _ = stmt.rantai_lain_jika[0]
        from morph_engine.absolute_sntx_morph import FoxBinary
        assert isinstance(kondisi_lain_jika, FoxBinary)

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

        from morph_engine.absolute_sntx_morph import Jika_Maka
        assert isinstance(outer_if, Jika_Maka)
        assert len(outer_if.blok_maka) == 1

        inner_if = outer_if.blok_maka[0]
        assert isinstance(inner_if, Jika_Maka)
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
        Memastikan parser menghasilkan Bagian yang valid (tapi kosong)
        saat tidak ada token selain ADS.
        """
        parser = parser_factory("") # Input kosong
        ast = parser.urai()

        assert isinstance(ast, Bagian), "Hasil harus selalu berupa Bagian"
        assert len(ast.daftar_pernyataan) == 0, "Daftar pernyataan harus kosong"
        assert not parser.daftar_kesalahan, "Tidak boleh ada kesalahan untuk input kosong"
