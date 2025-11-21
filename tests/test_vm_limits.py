from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken, Token
from ivm.compiler import Compiler
from ivm.core.fox_vm import FoxVM
import pytest

def test_infinite_loop_protection(capsys):
    # selama benar maka
    #   tulis("loop")
    # akhir

    # This would run forever without limit.
    # Set small limit for testing.

    cond = ast.Konstanta(Token(None, True, 0, 0))
    body = ast.Bagian([
        ast.Tulis([ast.Konstanta(Token(None, "loop", 0, 0))])
    ])
    loop = ast.Selama(None, cond, body)
    prog = ast.Bagian([loop])

    compiler = Compiler()
    code_obj = compiler.compile(prog)

    # Use low limit
    vm = FoxVM()
    vm.standard_vm.max_instructions = 100

    with pytest.raises(RuntimeError, match="Instruction limit exceeded"):
        vm.run(code_obj)

    # Verify it ran at least some instructions
    captured = capsys.readouterr()
    assert "loop" in captured.out
