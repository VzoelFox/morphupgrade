from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject
from typing import List, Tuple

class Optimizer:
    def optimize(self, code_obj: CodeObject) -> CodeObject:
        """
        Optimizes the given CodeObject by performing constant folding
        and dead code elimination. Returns a new CodeObject.
        """
        instructions = code_obj.instructions[:]

        # Pass 1: Constant Folding
        instructions = self.fold_constants(instructions)

        # Pass 2: Dead Code Elimination
        # instructions = self.eliminate_dead_code(instructions) # Skip for now, tricky with jumps

        return CodeObject(
            name=f"{code_obj.name}_opt",
            instructions=instructions,
            arg_names=code_obj.arg_names
        )

    def fold_constants(self, instructions: List[Tuple]) -> List[Tuple]:
        """
        Simple peephole optimization for constant arithmetic.
        Pattern: PUSH_CONST a, PUSH_CONST b, BINARY_OP -> PUSH_CONST (a op b)
        """
        if len(instructions) < 3:
            return instructions

        new_instr = []
        i = 0
        while i < len(instructions):
            # Check for 3-op sequence
            if i + 2 < len(instructions):
                op1 = instructions[i]
                op2 = instructions[i+1]
                op3 = instructions[i+2]

                if (op1[0] == Op.PUSH_CONST and
                    op2[0] == Op.PUSH_CONST and
                    self.is_binary_math_op(op3[0])):

                    val1 = op1[1]
                    val2 = op2[1]

                    try:
                        res = self.evaluate_op(op3[0], val1, val2)
                        # Replace 3 ops with 1 result
                        new_instr.append((Op.PUSH_CONST, res))
                        i += 3
                        continue
                    except Exception:
                        # If eval fails (e.g. div by zero), keep original
                        pass

            new_instr.append(instructions[i])
            i += 1

        # Recursive pass if changes were made?
        # For now single pass is enough for prototype.
        return new_instr

    def is_binary_math_op(self, opcode: Op) -> bool:
        return opcode in [Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.EQ, Op.NEQ, Op.GT, Op.LT]

    def evaluate_op(self, opcode: Op, a, b):
        # Note: Stack order for subtraction/division:
        # PUSH a, PUSH b, SUB -> a - b ?
        # StandardVM Logic: b = pop(), a = pop(), push(a-b).
        # So PUSH a (bottom), PUSH b (top). a is first operand.
        if opcode == Op.ADD: return a + b
        if opcode == Op.SUB: return a - b
        if opcode == Op.MUL: return a * b
        if opcode == Op.DIV: return a / b
        if opcode == Op.MOD: return a % b
        if opcode == Op.EQ: return a == b
        if opcode == Op.NEQ: return a != b
        if opcode == Op.GT: return a > b
        if opcode == Op.LT: return a < b
        raise ValueError(f"Unknown op {opcode}")
