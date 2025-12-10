from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
from ivm.core.structs import CodeObject

def test_function_call(capsys):
    # fungsi sapa(nama) maka
    #   tulis(nama)
    # akhir
    # sapa("Morph")

    # 1. Define Function `sapa`
    param_nama = Token(TipeToken.NAMA, "nama", 0, 0)
    body_sapa = ast.Bagian([
        ast.Tulis([ast.Identitas(param_nama)])
    ])
    func_decl = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "sapa", 0, 0),
        [param_nama],
        body_sapa
    )

    # 2. Call Function
    call_stmt = ast.PernyataanEkspresi(
        ast.PanggilFungsi(
            ast.Identitas(Token(TipeToken.NAMA, "sapa", 0, 0)),
            Token(TipeToken.KURUNG_TUTUP, ")", 0, 0),
            [ast.Konstanta(Token(None, "Morph", 0, 0))]
        )
    )

    prog = ast.Bagian([func_decl, call_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog) # Returns CodeObject

    # VM should now take a list of instructions (unpacked from module code object)
    # The StandardVM.load() method wraps instructions in a main frame.
    vm = FoxVM()
    vm.run(code_obj.instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Morph"

def test_return_value(capsys):
    # fungsi tambah(a, b) maka
    #   kembali a + b
    # akhir
    # tulis(tambah(5, 3))

    # 1. Function `tambah`
    p_a = Token(TipeToken.NAMA, "a", 0, 0)
    p_b = Token(TipeToken.NAMA, "b", 0, 0)

    sum_expr = ast.FoxBinary(
        ast.Identitas(p_a),
        Token(TipeToken.TAMBAH, "+", 0, 0),
        ast.Identitas(p_b)
    )

    func_body = ast.Bagian([
        ast.PernyataanKembalikan(None, sum_expr)
    ])

    func_decl = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "tambah", 0, 0),
        [p_a, p_b],
        func_body
    )

    # 2. Call and Print
    call_expr = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "tambah", 0, 0)),
        None,
        [
            ast.Konstanta(Token(None, 5, 0, 0)),
            ast.Konstanta(Token(None, 3, 0, 0))
        ]
    )

    print_stmt = ast.Tulis([call_expr])

    prog = ast.Bagian([func_decl, print_stmt])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj.instructions)

    captured = capsys.readouterr()
    assert captured.out.strip() == "8"

def test_local_scope(capsys):
    # biar x = 10
    # fungsi ubah() maka
    #   biar x = 99  <-- local x, should not affect global
    #   tulis(x)
    # akhir
    # ubah()
    # tulis(x)

    var_x = Token(TipeToken.NAMA, "x", 0, 0)

    # Global x = 10
    global_decl = ast.DeklarasiVariabel(None, var_x, ast.Konstanta(Token(None, 10, 0, 0)))

    # Function ubah
    local_decl = ast.DeklarasiVariabel(None, var_x, ast.Konstanta(Token(None, 99, 0, 0)))
    local_print = ast.Tulis([ast.Identitas(var_x)])

    func_decl = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "ubah", 0, 0),
        [],
        ast.Bagian([local_decl, local_print])
    )

    # Call ubah()
    call_stmt = ast.PernyataanEkspresi(
        ast.PanggilFungsi(
            ast.Identitas(Token(TipeToken.NAMA, "ubah", 0, 0)),
            None,
            []
        )
    )

    # Print global x
    global_print = ast.Tulis([ast.Identitas(var_x)])

    prog = ast.Bagian([global_decl, func_decl, call_stmt, global_print])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj.instructions)

    captured = capsys.readouterr()
    # Output should be 99 (from inside) then 10 (from outside)
    assert captured.out.split() == ["99", "10"]
