import pytest
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from transisi.morph_t import TipeToken
from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

def test_lexer_coba_tangkap():
    sumber = "coba \n tangkap e \n akhir"
    lexer = Leksikal(sumber)
    tokens, error = lexer.buat_token()
    assert not error
    token_types = [t.tipe for t in tokens]
    assert TipeToken.COBA in token_types
    assert TipeToken.TANGKAP in token_types
    assert TipeToken.AKHIR in token_types

def test_parser_coba_tangkap():
    sumber = """
    coba
        tulis("mencoba")
    tangkap e
        tulis("gagal")
    akhir
    """
    lexer = Leksikal(sumber)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()
    assert ast_node is not None
    assert len(ast_node.daftar_pernyataan) == 1

def test_compiler_coba_tangkap():
    sumber = """
    coba
        biar x = 1
    tangkap e
        biar y = 2
    akhir
    """
    lexer = Leksikal(sumber)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()

    compiler = Compiler()
    code_obj = compiler.compile(ast_node)

    instr_types = [i[0] for i in code_obj.instructions]
    assert Op.PUSH_TRY in instr_types
    assert Op.POP_TRY in instr_types

def test_vm_runtime_coba_tangkap_sukses():
    """Tes flow normal tanpa error."""
    sumber = """
    biar hasil = 0
    coba
        ubah hasil = 10
    tangkap e
        ubah hasil = 99
    akhir
    """
    lexer = Leksikal(sumber)
    tokens, _ = lexer.buat_token()
    parser = Pengurai(tokens)
    ast_node = parser.urai()
    compiler = Compiler()
    code = compiler.compile(ast_node)

    vm = StandardVM()
    vm.load(code)
    vm.run()

    assert vm.globals['hasil'] == 10

def test_vm_runtime_coba_tangkap_error():
    """Tes flow error tertangkap dengan manual bytecode injection."""
    program = [
        (Op.PUSH_TRY, 5), # 0: Jump to 5 on error
        (Op.PUSH_CONST, "Boom"), # 1
        (Op.THROW,), # 2
        (Op.POP_TRY,), # 3
        (Op.JMP, 8), # 4
        # Handler starts at index 5
        (Op.STORE_VAR, "err_msg"), # 5 (error obj popped to var)
        (Op.PUSH_CONST, 99), # 6
        (Op.STORE_VAR, "res"), # 7
        (Op.HALT,) # 8
    ]

    vm = StandardVM()
    vm.load(program)
    vm.run()

    assert vm.globals.get("res") == 99
    # Verifikasi object error (sekarang dict)
    err_obj = vm.globals.get("err_msg")
    assert isinstance(err_obj, dict)
    assert err_obj["pesan"] == "Boom"

def test_vm_stack_unwinding():
    """
    Tes fitur baru: Stack Unwinding.
    Fungsi A memanggil Fungsi B.
    Fungsi B melempar error.
    Fungsi A menangkap error.
    """
    # Code Object B (Function)
    # Instructions: PUSH "Error dari B", THROW, RET
    instr_b = [
        (Op.PUSH_CONST, "Error dari B"),
        (Op.THROW,),
        (Op.RET,)
    ]
    code_b = CodeObject(name="func_b", instructions=instr_b)

    # Main Program (A)
    # 0: PUSH_TRY -> ke 7 (Handler)
    # 1: PUSH_CONST CodeB
    # 2: CALL 0 args
    # 3: POP_TRY
    # 4: PUSH_CONST "Sukses" (seharusnya tidak dieksekusi)
    # 5: STORE_VAR "status"
    # 6: HALT
    # 7: Handler start -> STORE_VAR "caught"
    # 8: HALT

    program = [
        (Op.PUSH_TRY, 7),
        (Op.PUSH_CONST, code_b),
        (Op.CALL, 0),
        (Op.POP_TRY,),
        (Op.PUSH_CONST, "Sukses"),
        (Op.STORE_VAR, "status"),
        (Op.HALT,),
        (Op.STORE_VAR, "caught"), # 7
        (Op.HALT,) # 8
    ]

    vm = StandardVM()
    vm.load(program)
    vm.run()

    assert "status" not in vm.globals # Tidak boleh sukses
    caught = vm.globals.get("caught")
    assert isinstance(caught, dict)
    assert caught["pesan"] == "Error dari B"
