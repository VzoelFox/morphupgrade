# tests/test_ivm.py
import pytest
from io import StringIO
import sys

from ivm.opcodes import OpCode
from ivm.compiler import Compiler
from ivm.vm import VirtualMachine

def test_hello_vm_integration(capsys):
    """
    Tes integrasi end-to-end untuk program sederhana: tulis(1 + 2)
    """
    # Representasi manual dari program
    program = [
        (OpCode.LOAD_GLOBAL, "tulis"),
        (OpCode.LOAD_CONST, 1),
        (OpCode.LOAD_CONST, 2),
        (OpCode.ADD,),
        (OpCode.CALL_FUNCTION, 1),
        (OpCode.POP_TOP,),
    ]

    # 1. Kompilasi program menjadi bytecode
    compiler = Compiler()
    code_obj = compiler.compile(program)

    # Verifikasi bytecode yang dihasilkan (opsional tapi bagus)
    assert code_obj.instructions == bytearray([
        OpCode.LOAD_GLOBAL, 0,  # 'tulis' di constants[0]
        OpCode.LOAD_CONST, 1,   # 1 di constants[1]
        OpCode.LOAD_CONST, 2,   # 2 di constants[2]
        OpCode.ADD,
        OpCode.CALL_FUNCTION, 1,
        OpCode.POP_TOP,
    ])
    assert code_obj.constants == ["tulis", 1, 2]

    # 2. Jalankan bytecode di VM
    vm = VirtualMachine()
    vm.run(code_obj)

    # 3. Verifikasi output
    captured = capsys.readouterr()
    assert captured.out.strip() == "3"
