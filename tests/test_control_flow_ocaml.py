import pytest
from transisi.morph_t import TipeToken
from transisi.absolute_sntx_morph import (
    JikaMaka, Selama, FungsiDeklarasi, PernyataanKembalikan, PanggilFungsi
)
from transisi.ocaml_loader import load_compiled_ast
import subprocess
import json

def compile_morph_to_json(source: str):
    """Helper to compile a Morph string to a JSON AST file."""
    with open("temp_test.morph", "w") as f:
        f.write(source)

    # Run the OCaml compiler
    subprocess.run(
        [
            "universal/_build/default/main.exe",
            "temp_test.morph",
            "temp_output.json"
        ],
        check=True
    )

    with open("temp_output.json", "r") as f:
        return json.load(f)

def test_jika_sederhana():
    source = "jika 5 > 3 maka\ntulis(10)\nakhir\n"
    compile_morph_to_json(source)
    ast_obj = load_compiled_ast("temp_output.json")

    assert len(ast_obj.daftar_pernyataan) == 1
    stmt = ast_obj.daftar_pernyataan[0]
    assert isinstance(stmt, JikaMaka)
    assert stmt.kondisi.op.tipe == TipeToken.LEBIH_DARI

def test_selama_loop():
    source = "selama benar maka\ntulis(1)\nakhir\n"
    compile_morph_to_json(source)
    ast_obj = load_compiled_ast("temp_output.json")

    assert len(ast_obj.daftar_pernyataan) == 1
    stmt = ast_obj.daftar_pernyataan[0]
    assert isinstance(stmt, Selama)
    assert stmt.token.tipe == TipeToken.SELAMA

def test_fungsi_deklarasi_dan_panggil():
    source = """
fungsi tambah(a, b) maka
  kembali a + b
akhir
tambah(1, 2)
"""
    compile_morph_to_json(source)
    ast_obj = load_compiled_ast("temp_output.json")

    assert len(ast_obj.daftar_pernyataan) == 2

    func_decl = ast_obj.daftar_pernyataan[0]
    assert isinstance(func_decl, FungsiDeklarasi)
    assert func_decl.nama.nilai == "tambah"
    assert len(func_decl.parameter) == 2

    return_stmt = func_decl.badan.daftar_pernyataan[0]
    assert isinstance(return_stmt, PernyataanKembalikan)

    func_call = ast_obj.daftar_pernyataan[1].ekspresi
    assert isinstance(func_call, PanggilFungsi)
    assert func_call.callee.token.nilai == "tambah"
    assert len(func_call.argumen) == 2
