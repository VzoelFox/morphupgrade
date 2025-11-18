# tests/test_ivm.py
import pytest
from io import StringIO
import sys

# Komponen dari arsitektur lama (parser)
from transisi.lx import Leksikal
from transisi.crusher import Pengurai

# Komponen dari arsitektur baru (compiler & vm)
from ivm import hir
from ivm.frontend import HIRConverter
from ivm.compiler import Compiler
from ivm.vm import VirtualMachine

def test_full_compilation_pipeline(capsys):
    """
    Tes integrasi end-to-end untuk alur kerja penuh:
    String Kode -> Lexer -> Parser -> AST -> HIR -> Compiler -> Bytecode -> VM -> Output
    """
    run_test_case(capsys, "tulis(1 + 2);", "3")

def test_variable_declaration_and_use(capsys):
    """
    Tes untuk deklarasi variabel, akses, dan penggunaannya dalam sebuah fungsi.
    """
    kode_sumber = """
    biar x = 10;
    tulis(x);
    """
    run_test_case(capsys, kode_sumber, "10")

def test_if_statement_true(capsys):
    """Tes pernyataan 'jika' di mana kondisi benar."""
    kode_sumber = """
    jika 1 > 0 maka
        tulis("benar");
    akhir
    """
    run_test_case(capsys, kode_sumber, "benar")

def test_if_statement_false(capsys):
    """Tes pernyataan 'jika' di mana kondisi salah."""
    kode_sumber = """
    jika 0 > 1 maka
        tulis("salah");
    akhir
    """
    run_test_case(capsys, kode_sumber, "")

def test_function_definition_and_call(capsys):
    """Tes mendefinisikan fungsi, memanggilnya, dan mendapatkan hasilnya."""
    kode_sumber = """
    fungsi tambah(a, b) maka
        kembali a + b;
    akhir
    tulis(tambah(3, 4));
    """
    run_test_case(capsys, kode_sumber, "7")

def test_list_creation_and_access(capsys):
    """Tes pembuatan list literal dan akses elemen berdasarkan indeks."""
    kode_sumber = """
    biar data = [10, 20, "tiga puluh"];
    tulis(data[1]);
    """
    run_test_case(capsys, kode_sumber, "20")

def run_test_case(capsys, kode_sumber, output_yang_diharapkan):
    """Fungsi helper untuk menjalankan satu kasus uji dari sumber ke output."""
    # 1. Parsing (AST Generation)
    lexer = Leksikal(kode_sumber, "<test>")
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_tree = parser.urai()
    assert ast_tree is not None, f"Parser gagal untuk kode: {kode_sumber}"

    # 2. Konversi AST ke HIR
    hir_converter = HIRConverter()
    hir_tree = hir_converter.convert(ast_tree)

    # 3. Kompilasi HIR ke Bytecode
    compiler = Compiler()
    code_obj = compiler.compile(hir_tree)

    # 4. Eksekusi Bytecode di VM
    vm = VirtualMachine()
    vm.run(code_obj)

    # 5. Verifikasi Output
    captured = capsys.readouterr()
    assert captured.out.strip() == output_yang_diharapkan
