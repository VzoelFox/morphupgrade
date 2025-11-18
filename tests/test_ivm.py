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

def test_list_item_assignment(capsys):
    """Tes assignment nilai baru ke elemen list berdasarkan indeks."""
    kode_sumber = """
    biar data = [1, 2, 3];
    ubah data[1] = 99;
    tulis(data[1]);
    """
    run_test_case(capsys, kode_sumber, "99")

def test_while_loop(capsys):
    """Tes fungsionalitas perulangan 'selama'."""
    kode_sumber = """
    biar i = 0;
    selama i < 5 maka
        ubah i = i + 1;
    akhir
    tulis(i);
    """
    run_test_case(capsys, kode_sumber, "5")

def test_dict_creation_access_and_assignment(capsys):
    """Tes pembuatan kamus, assignment, dan akses elemen."""
    kode_sumber = """
    biar data = {"nama": "Jules", "nilai": 100};
    ubah data["nilai"] = 150;
    tulis(data["nama"]);
    tulis(data["nilai"]);
    """
    run_test_case(capsys, kode_sumber, "Jules\n150")

def test_module_import(capsys):
    """Tes mengimpor satu modul dan menggunakan fungsinya."""
    # Kita tidak bisa menggunakan string literal di sini karena path file penting.
    with open("tests/modul_utama.fox", 'r', encoding='utf-8') as f:
        kode_sumber = f.read()

    run_test_case(capsys, kode_sumber, "20")

def test_class_definition_instantiation_and_properties(capsys):
    """Tes definisi kelas, instansiasi, set properti, dan get properti."""
    kode_sumber = """
    kelas Pengguna maka
    akhir

    biar pengguna1 = Pengguna();
    ubah pengguna1.nama = "Jules";
    ubah pengguna1.skor = 100;

    tulis(pengguna1.nama);
    tulis(pengguna1.skor);
    """
    run_test_case(capsys, kode_sumber, "Jules\n100")

def test_class_methods_and_this(capsys):
    """Tes definisi metode, pemanggilan metode, dan penggunaan 'ini'."""
    kode_sumber = """
    kelas Konter maka
        fungsi inisiasi() maka
            ubah ini.nilai = 0;
        akhir

        fungsi tambah() maka
            ubah ini.nilai = ini.nilai + 1;
        akhir
    akhir

    biar k = Konter();
    k.inisiasi();
    k.tambah();
    k.tambah();
    tulis(k.nilai);
    """
    run_test_case(capsys, kode_sumber, "2")

def test_binary_operators(capsys):
    """Tes berbagai operator biner yang sebelumnya hilang."""
    kode_sumber = """
    tulis(10 - 3);      // SUBTRACT
    tulis(5 * 2 == 10); // MULTIPLY, EQUAL
    tulis(10 / 2);      // DIVIDE
    """
    run_test_case(capsys, kode_sumber, "7\nbenar\n5.0")

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
