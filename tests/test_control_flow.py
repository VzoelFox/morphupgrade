from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM

def test_if_else(capsys):
    # jika benar maka tulis(1) lain tulis(2) akhir

    cond = ast.Konstanta(Token(None, True, 0, 0))
    then_block = ast.Bagian([ast.Tulis([ast.Konstanta(Token(None, 1, 0, 0))])])
    else_block = ast.Bagian([ast.Tulis([ast.Konstanta(Token(None, 2, 0, 0))])])

    stmt = ast.JikaMaka(cond, then_block, [], else_block)
    prog = ast.Bagian([stmt])

    compiler = Compiler()
    instructions = compiler.compile(prog)

    vm = FoxVM()
    vm.run(instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "1"

def test_while_loop(capsys):
    # biar x = 3
    # selama x > 0 maka
    #   tulis(x)
    #   ubah x = x - 1
    # akhir

    # Setup Vars
    var_x = Token(TipeToken.NAMA, "x", 0, 0)
    decl = ast.DeklarasiVariabel(None, var_x, ast.Konstanta(Token(None, 3, 0, 0)))

    # Condition: x > 0
    cond = ast.FoxBinary(
        ast.Identitas(var_x),
        Token(TipeToken.LEBIH_DARI, ">", 0, 0),
        ast.Konstanta(Token(None, 0, 0, 0))
    )

    # Body: tulis(x); x = x - 1
    print_stmt = ast.Tulis([ast.Identitas(var_x)])

    sub_expr = ast.FoxBinary(
        ast.Identitas(var_x),
        Token(TipeToken.KURANG, "-", 0, 0),
        ast.Konstanta(Token(None, 1, 0, 0))
    )
    assign_stmt = ast.Assignment(ast.Identitas(var_x), sub_expr)

    body = ast.Bagian([print_stmt, assign_stmt])

    loop_stmt = ast.Selama(None, cond, body)
    prog = ast.Bagian([decl, loop_stmt])

    compiler = Compiler()
    instructions = compiler.compile(prog)

    vm = FoxVM()
    vm.run(instructions)

    captured = capsys.readouterr()
    assert captured.out.split() == ["3", "2", "1"]

def test_break(capsys):
    # selama benar maka
    #   tulis("start")
    #   berhenti
    #   tulis("end")
    # akhir

    cond = ast.Konstanta(Token(None, True, 0, 0))

    body = ast.Bagian([
        ast.Tulis([ast.Konstanta(Token(None, "start", 0, 0))]),
        ast.Berhenti(None),
        ast.Tulis([ast.Konstanta(Token(None, "end", 0, 0))])
    ])

    loop_stmt = ast.Selama(None, cond, body)
    prog = ast.Bagian([loop_stmt])

    compiler = Compiler()
    instructions = compiler.compile(prog)

    vm = FoxVM()
    vm.run(instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "start"
