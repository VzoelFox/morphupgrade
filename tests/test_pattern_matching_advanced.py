from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
from ivm.core.structs import CodeObject

def test_pattern_binding(capsys):
    # jodohkan 5 dengan
    # | x maka tulis(x)
    # akhir

    subj = ast.Konstanta(Token(None, 5, 0, 0))

    # Pattern: x
    pola = ast.PolaIkatanVariabel(Token(TipeToken.NAMA, "x", 0, 0))

    # Body: tulis(x)
    body = ast.Bagian([
        ast.Tulis([ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0))])
    ])

    kasus = ast.JodohkanKasus(pola, None, body)
    stmt = ast.Jodohkan(subj, [kasus])

    prog = ast.Bagian([stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "5"

def test_pattern_guard(capsys):
    # jodohkan 5 dengan
    # | x jaga x > 10 maka tulis("besar")
    # | x jaga x < 10 maka tulis("kecil")
    # akhir

    subj = ast.Konstanta(Token(None, 5, 0, 0))

    # Case 1: x > 10
    pola1 = ast.PolaIkatanVariabel(Token(TipeToken.NAMA, "x", 0, 0))
    guard1 = ast.FoxBinary(
        ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0)),
        Token(TipeToken.LEBIH_DARI, ">", 0, 0),
        ast.Konstanta(Token(None, 10, 0, 0))
    )
    body1 = ast.Bagian([ast.Tulis([ast.Konstanta(Token(None, "besar", 0, 0))])])
    kasus1 = ast.JodohkanKasus(pola1, guard1, body1)

    # Case 2: x < 10
    pola2 = ast.PolaIkatanVariabel(Token(TipeToken.NAMA, "x", 0, 0))
    guard2 = ast.FoxBinary(
        ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0)),
        Token(TipeToken.KURANG_DARI, "<", 0, 0),
        ast.Konstanta(Token(None, 10, 0, 0))
    )
    body2 = ast.Bagian([ast.Tulis([ast.Konstanta(Token(None, "kecil", 0, 0))])])
    kasus2 = ast.JodohkanKasus(pola2, guard2, body2)

    stmt = ast.Jodohkan(subj, [kasus1, kasus2])
    prog = ast.Bagian([stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "kecil"
