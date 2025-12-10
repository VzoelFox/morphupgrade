from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
from ivm.core.structs import CodeObject

def test_list_creation(capsys):
    # x = [1, 2, 3]
    # tulis(x)

    list_lit = ast.Daftar([
        ast.Konstanta(Token(None, 1, 0, 0)),
        ast.Konstanta(Token(None, 2, 0, 0)),
        ast.Konstanta(Token(None, 3, 0, 0))
    ])

    decl = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "x", 0, 0), list_lit)
    print_stmt = ast.Tulis([ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0))])

    prog = ast.Bagian([decl, print_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "[1, 2, 3]"

def test_dict_creation(capsys):
    # x = {"a": 1}
    # tulis(x)

    dict_lit = ast.Kamus([
        (ast.Konstanta(Token(None, "a", 0, 0)), ast.Konstanta(Token(None, 1, 0, 0)))
    ])

    decl = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "x", 0, 0), dict_lit)
    print_stmt = ast.Tulis([ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0))])

    prog = ast.Bagian([decl, print_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "{'a': 1}"

def test_list_index_access(capsys):
    # x = [10, 20]
    # tulis(x[1])

    list_lit = ast.Daftar([
        ast.Konstanta(Token(None, 10, 0, 0)),
        ast.Konstanta(Token(None, 20, 0, 0))
    ])

    decl = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "x", 0, 0), list_lit)

    access = ast.Akses(
        ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0)),
        ast.Konstanta(Token(None, 1, 0, 0))
    )
    print_stmt = ast.Tulis([access])

    prog = ast.Bagian([decl, print_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "20"

def test_list_modification(capsys):
    # x = [1, 2]
    # ubah x[0] = 99
    # tulis(x)

    list_lit = ast.Daftar([
        ast.Konstanta(Token(None, 1, 0, 0)),
        ast.Konstanta(Token(None, 2, 0, 0))
    ])
    decl = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "x", 0, 0), list_lit)

    target = ast.Akses(
        ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0)),
        ast.Konstanta(Token(None, 0, 0, 0))
    )

    assign = ast.Assignment(target, ast.Konstanta(Token(None, 99, 0, 0)))
    print_stmt = ast.Tulis([ast.Identitas(Token(TipeToken.NAMA, "x", 0, 0))])

    prog = ast.Bagian([decl, assign, print_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "[99, 2]"
