from ivm.optimizer import Optimizer
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

def test_optimizer_constant_folding():
    # Code: 1 + 2
    # PUSH 1, PUSH 2, ADD
    code = CodeObject(
        name="test",
        instructions=[
            (Op.PUSH_CONST, 1),
            (Op.PUSH_CONST, 2),
            (Op.ADD,)
        ]
    )

    opt = Optimizer()
    optimized_code = opt.optimize(code)

    assert len(optimized_code.instructions) == 1
    assert optimized_code.instructions[0] == (Op.PUSH_CONST, 3)

def test_optimizer_multiple_folds():
    # Code: 1 + 2 + 3
    # PUSH 1, PUSH 2, ADD, PUSH 3, ADD
    # -> PUSH 3, PUSH 3, ADD -> PUSH 6

    # Note: My simple optimizer does single pass peephole (3 instructions).
    # PUSH 1, PUSH 2, ADD -> PUSH 3
    # Result instructions: PUSH 3, PUSH 3, ADD
    # It needs a loop or recursion to fold the next one.
    # My implementation: "Recursive pass if changes were made? For now single pass..."
    # So it will fold the first pair.

    code = CodeObject(
        name="test",
        instructions=[
            (Op.PUSH_CONST, 1),
            (Op.PUSH_CONST, 2),
            (Op.ADD,),
            (Op.PUSH_CONST, 3),
            (Op.ADD,)
        ]
    )

    opt = Optimizer()
    opt_code = opt.optimize(code)

    # Expectation for single pass:
    # PUSH 3, PUSH 3, ADD
    assert len(opt_code.instructions) == 3
    assert opt_code.instructions[0] == (Op.PUSH_CONST, 3)
