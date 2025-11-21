from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
import os

def test_builtins_core(capsys):
    # tulis(tipe("Morph"))
    # tulis(panjang([1, 2]))

    call_tipe = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "tipe", 0, 0)),
        None,
        [ast.Konstanta(Token(None, "Morph", 0, 0))]
    )

    call_len = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "panjang", 0, 0)),
        None,
        [ast.Daftar([
            ast.Konstanta(Token(None, 1, 0, 0)),
            ast.Konstanta(Token(None, 2, 0, 0))
        ])]
    )

    prog = ast.Bagian([
        ast.Tulis([call_tipe]),
        ast.Tulis([call_len])
    ])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    output = captured.out.split()
    assert "teks" in output
    assert "2" in output

def test_file_io(tmp_path):
    # tulis_file("test.txt", "Halo Dunia")
    # isi = baca_file("test.txt")
    # tulis(isi)

    file_path = tmp_path / "test_io.txt"
    path_str = str(file_path)

    call_write = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "tulis_file", 0, 0)),
        None,
        [
            ast.Konstanta(Token(None, path_str, 0, 0)),
            ast.Konstanta(Token(None, "Halo Dunia", 0, 0))
        ]
    )

    stmt_write = ast.PernyataanEkspresi(call_write)

    call_read = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "baca_file", 0, 0)),
        None,
        [ast.Konstanta(Token(None, path_str, 0, 0))]
    )

    # var isi = baca_file(...)
    decl_isi = ast.DeklarasiVariabel(
        None,
        Token(TipeToken.NAMA, "isi", 0, 0),
        call_read
    )

    stmt_print = ast.Tulis([ast.Identitas(Token(TipeToken.NAMA, "isi", 0, 0))])

    prog = ast.Bagian([stmt_write, decl_isi, stmt_print])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    # Verify file content directly
    assert file_path.read_text(encoding="utf-8") == "Halo Dunia"

def test_system_time(capsys):
    # t = waktu()
    # tulis(tipe(t))

    call_waktu = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "waktu", 0, 0)),
        None,
        []
    )

    decl_t = ast.DeklarasiVariabel(None, Token(TipeToken.NAMA, "t", 0, 0), call_waktu)

    call_tipe = ast.PanggilFungsi(
        ast.Identitas(Token(TipeToken.NAMA, "tipe", 0, 0)),
        None,
        [ast.Identitas(Token(TipeToken.NAMA, "t", 0, 0))]
    )

    stmt_print = ast.Tulis([call_tipe])

    prog = ast.Bagian([decl_t, stmt_print])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    vm = FoxVM()
    vm.run(code_obj)

    captured = capsys.readouterr()
    assert "angka" in captured.out
