import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi.absolute_sntx_morph import (
    Jodohkan, JodohkanKasus, PolaLiteral, PolaWildcard, PolaIkatanVariabel,
    PolaVarian, PolaDaftar, Konstanta
)

def parse_jodohkan_statement(code):
    """Helper untuk mem-parse hanya statement 'jodohkan' dan mengembalikan node-nya."""
    lexer = Leksikal(code)
    tokens, errors = lexer.buat_token()
    assert not errors, "Lexer errors found"

    parser = Pengurai(tokens)
    program = parser.urai()
    assert not parser.daftar_kesalahan, f"Parser errors found: {parser.daftar_kesalahan}"

    assert len(program.daftar_pernyataan) == 1, "Expected one statement"
    stmt = program.daftar_pernyataan[0]
    assert isinstance(stmt, Jodohkan), f"Expected Jodohkan statement, but got {type(stmt)}"
    return stmt

class TestJodohkanPatternParsing:
    def test_parse_pola_literal(self):
        code = """
        jodohkan x dengan
            | 10 maka
                tulis(1)
            | "halo" maka
                tulis(1)
            | benar maka
                tulis(1)
            | salah maka
                tulis(1)
            | nil maka
                tulis(1)
        akhir
        """
        jodohkan_node = parse_jodohkan_statement(code)
        assert len(jodohkan_node.kasus) == 5
        case1 = jodohkan_node.kasus[0]
        assert isinstance(case1.pola, PolaLiteral)
        assert isinstance(case1.pola.nilai, Konstanta)
        assert case1.pola.nilai.nilai == 10
        case2 = jodohkan_node.kasus[1]
        assert isinstance(case2.pola, PolaLiteral)
        assert case2.pola.nilai.nilai == "halo"

    def test_parse_pola_wildcard_dan_ikatan_variabel(self):
        code = """
        jodohkan y dengan
            | _ maka
                tulis(1)
            | variabelLain maka
                tulis(1)
        akhir
        """
        jodohkan_node = parse_jodohkan_statement(code)
        assert len(jodohkan_node.kasus) == 2
        case1 = jodohkan_node.kasus[0]
        assert isinstance(case1.pola, PolaWildcard)
        case2 = jodohkan_node.kasus[1]
        assert isinstance(case2.pola, PolaIkatanVariabel)
        assert case2.pola.token.nilai == "variabelLain"

    def test_parse_pola_varian(self):
        code = """
        jodohkan hasil dengan
            | Sukses(data) maka
                tulis(1)
            | Gagal maka
                tulis(1)
            | Peringatan(kode, _) maka
                tulis(1)
        akhir
        """
        jodohkan_node = parse_jodohkan_statement(code)
        assert len(jodohkan_node.kasus) == 3
        case1 = jodohkan_node.kasus[0]
        assert isinstance(case1.pola, PolaVarian)
        assert case1.pola.nama.nilai == "Sukses"
        assert len(case1.pola.daftar_ikatan) == 1
        assert case1.pola.daftar_ikatan[0].nilai == "data"
        case2 = jodohkan_node.kasus[1]
        assert isinstance(case2.pola, PolaVarian)
        assert case2.pola.nama.nilai == "Gagal"
        assert len(case2.pola.daftar_ikatan) == 0
        case3 = jodohkan_node.kasus[2]
        assert isinstance(case3.pola, PolaVarian)
        assert case3.pola.nama.nilai == "Peringatan"
        assert len(case3.pola.daftar_ikatan) == 2
        assert case3.pola.daftar_ikatan[0].nilai == "kode"
        assert case3.pola.daftar_ikatan[1].nilai == "_"

    def test_parse_pola_daftar(self):
        code = """
        jodohkan daftar dengan
            | [] maka
                tulis(1)
            | [x] maka
                tulis(1)
            | [x, _, z] maka
                tulis(1)
        akhir
        """
        jodohkan_node = parse_jodohkan_statement(code)
        assert len(jodohkan_node.kasus) == 3
        case1 = jodohkan_node.kasus[0]
        assert isinstance(case1.pola, PolaDaftar)
        assert len(case1.pola.daftar_pola) == 0
        case2 = jodohkan_node.kasus[1]
        assert isinstance(case2.pola, PolaDaftar)
        assert len(case2.pola.daftar_pola) == 1
        assert isinstance(case2.pola.daftar_pola[0], PolaIkatanVariabel)
        case3 = jodohkan_node.kasus[2]
        assert isinstance(case3.pola, PolaDaftar)
        assert len(case3.pola.daftar_pola) == 3
        assert isinstance(case3.pola.daftar_pola[0], PolaIkatanVariabel)
        assert isinstance(case3.pola.daftar_pola[1], PolaWildcard)
        assert isinstance(case3.pola.daftar_pola[2], PolaIkatanVariabel)
