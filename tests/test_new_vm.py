from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
from ivm.core.opcodes import Op

def test_simple_arithmetic(capsys):
    # Test: 1 + 2 * 3
    # AST construction manually for simplicity
    node_1 = ast.Konstanta(Token(None, 1, 0, 0))
    node_2 = ast.Konstanta(Token(None, 2, 0, 0))
    node_3 = ast.Konstanta(Token(None, 3, 0, 0))

    # 2 * 3
    mult = ast.FoxBinary(node_2, Token(TipeToken.KALI, "*", 0, 0), node_3)
    # 1 + (2 * 3)
    add = ast.FoxBinary(node_1, Token(TipeToken.TAMBAH, "+", 0, 0), mult)

    # tulis(result)
    stmt = ast.Tulis([add])
    prog = ast.Bagian([stmt])

    compiler = Compiler()
    instructions = compiler.compile(prog)

    vm = FoxVM()
    vm.run(instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "7"

def test_basic_variable(capsys):
    # biar x = 10
    # tulis(x)

    var_x = Token(TipeToken.NAMA, "x", 0, 0)
    val_10 = ast.Konstanta(Token(None, 10, 0, 0))

    decl = ast.DeklarasiVariabel(None, var_x, val_10)

    access_x = ast.Identitas(var_x)
    print_x = ast.Tulis([access_x])

    prog = ast.Bagian([decl, print_x])

    compiler = Compiler()
    instructions = compiler.compile(prog)

    vm = FoxVM()
    vm.run(instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "10"
