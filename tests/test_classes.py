from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
from ivm.core.structs import CodeObject

def test_class_definition_and_instantiation(capsys):
    # kelas Hewan maka
    #   fungsi suara() maka
    #     tulis("Grr")
    #   akhir
    # akhir
    #
    # h = Hewan()
    # h.suara()

    # 1. Class Definition
    method_suara = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "suara", 0, 0),
        [],
        ast.Bagian([
            ast.Tulis([ast.Konstanta(Token(None, "Grr", 0, 0))])
        ])
    )

    class_decl = ast.Kelas(
        Token(TipeToken.NAMA, "Hewan", 0, 0),
        None,
        [method_suara]
    )

    # 2. Instantiation: h = Hewan()
    call_hewan = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "Hewan", 0, 0)),
        None,
        []
    )
    var_h = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "h", 0, 0), call_hewan)

    # 3. Method Call: h.suara()
    # Parser produces PanggilFungsi(AmbilProperti(h, "suara"), args)
    call_suara = ast.PanggilFungsi(
        ast.AmbilProperti(
            ast.Identitas(Token(TipeToken.NAMA, "h", 0, 0)),
            Token(TipeToken.NAMA, "suara", 0, 0)
        ),
        None,
        []
    )
    stmt_call_suara = ast.PernyataanEkspresi(call_suara)

    prog = ast.Bagian([class_decl, var_h, stmt_call_suara])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Grr"

def test_class_properties_and_this(capsys):
    # kelas Kotak maka
    #   fungsi inisiasi(p) maka
    #     ubah ini.panjang = p
    #   akhir
    #
    #   fungsi info() maka
    #     tulis(ini.panjang)
    #   akhir
    # akhir
    #
    # k = Kotak(10)
    # k.info()

    # Method: inisiasi(p)
    p_token = Token(TipeToken.NAMA, "p", 0, 0)

    assign_prop = ast.AturProperti(
        ast.Ini(Token(TipeToken.INI, "ini", 0, 0)),
        Token(TipeToken.NAMA, "panjang", 0, 0),
        ast.Identitas(p_token)
    )

    # Note: In my simplified parser logic for tests, I use AturProperti directly.
    # The parser actually produces Assignment with target AmbilProperti.
    # But my Compiler handles AturProperti.

    method_init = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "inisiasi", 0, 0),
        [p_token],
        ast.Bagian([ast.PernyataanEkspresi(assign_prop)])
    )

    # Method: info()
    read_prop = ast.AmbilProperti(
        ast.Ini(Token(TipeToken.INI, "ini", 0, 0)),
        Token(TipeToken.NAMA, "panjang", 0, 0)
    )
    method_info = ast.FungsiDeklarasi(
        Token(TipeToken.NAMA, "info", 0, 0),
        [],
        ast.Bagian([ast.Tulis([read_prop])])
    )

    class_kotak = ast.Kelas(
        Token(TipeToken.NAMA, "Kotak", 0, 0),
        None,
        [method_init, method_info]
    )

    # k = Kotak(10)
    call_new = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "Kotak", 0, 0)),
        None,
        [ast.Konstanta(Token(None, 10, 0, 0))]
    )
    var_k = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "k", 0, 0), call_new)

    # k.info()
    call_info = ast.PanggilFungsi(
        ast.AmbilProperti(
            ast.Identitas(Token(TipeToken.NAMA, "k", 0, 0)),
            Token(TipeToken.NAMA, "info", 0, 0)
        ),
        None,
        []
    )
    stmt_info = ast.PernyataanEkspresi(call_info)

    prog = ast.Bagian([class_kotak, var_k, stmt_info])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert captured.out.strip() == "10"
