from typing import List, Any, Dict, Tuple
from ivm.core.opcodes import Op

class StandardVM:
    def __init__(self):
        self.stack: List[Any] = []
        self.registers: List[Any] = [None] * 32  # 32 General Purpose Registers
        self.variables: Dict[str, Any] = {}      # Global scope for variables
        self.pc: int = 0                         # Program Counter
        self.instructions: List[Tuple] = []
        self.running: bool = False

    def load(self, instructions: List[Tuple]):
        self.instructions = instructions
        self.pc = 0
        self.stack.clear()
        self.registers = [None] * 32
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.pc < len(self.instructions):
            instruction = self.instructions[self.pc]
            self.pc += 1  # Advance PC *before* execution (Jumps will overwrite this)
            self.execute(instruction)

    def execute(self, instr: Tuple):
        opcode = instr[0]

        # === Stack Operations ===
        if opcode == Op.PUSH_CONST:
            self.stack.append(instr[1])

        elif opcode == Op.POP:
            if self.stack: self.stack.pop()

        elif opcode == Op.DUP:
            if self.stack: self.stack.append(self.stack[-1])

        # === Arithmetic (Stack) ===
        elif opcode == Op.ADD:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif opcode == Op.SUB:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif opcode == Op.MUL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif opcode == Op.DIV:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a / b)
        elif opcode == Op.MOD:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a % b)

        # === Logic (Stack) ===
        elif opcode == Op.EQ:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
        elif opcode == Op.NEQ:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a != b)
        elif opcode == Op.GT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a > b)
        elif opcode == Op.LT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a < b)
        elif opcode == Op.NOT:
            val = self.stack.pop()
            self.stack.append(not val)

        # === Register Operations ===
        elif opcode == Op.LOAD_REG:
            reg_idx, val = instr[1], instr[2]
            self._check_reg(reg_idx)
            self.registers[reg_idx] = val

        elif opcode == Op.MOVE_REG:
            dest, src = instr[1], instr[2]
            self._check_reg(dest)
            self._check_reg(src)
            self.registers[dest] = self.registers[src]

        elif opcode == Op.ADD_REG:
            dest, src1, src2 = instr[1], instr[2], instr[3]
            self._check_reg(dest)
            val1 = self.registers[src1]
            val2 = self.registers[src2]
            self.registers[dest] = val1 + val2

        # === Hybrid Bridges ===
        elif opcode == Op.PUSH_FROM_REG:
            reg_idx = instr[1]
            self._check_reg(reg_idx)
            self.stack.append(self.registers[reg_idx])

        elif opcode == Op.POP_TO_REG:
            reg_idx = instr[1]
            self._check_reg(reg_idx)
            val = self.stack.pop()
            self.registers[reg_idx] = val

        # === Variable Access ===
        elif opcode == Op.LOAD_VAR:
            name = instr[1]
            if name in self.variables:
                self.stack.append(self.variables[name])
            else:
                raise RuntimeError(f"Variabel '{name}' tidak ditemukan.")

        elif opcode == Op.STORE_VAR:
            name = instr[1]
            val = self.stack.pop()
            self.variables[name] = val

        # === Control Flow ===
        elif opcode == Op.JMP:
            target = instr[1]
            self.pc = target

        elif opcode == Op.JMP_IF_FALSE:
            target = instr[1]
            condition = self.stack.pop()
            if not condition:
                self.pc = target

        elif opcode == Op.JMP_IF_TRUE:
            target = instr[1]
            condition = self.stack.pop()
            if condition:
                self.pc = target

        # === IO ===
        elif opcode == Op.PRINT:
            count = instr[1]
            args = []
            for _ in range(count):
                args.append(self.stack.pop())
            print(*reversed(args))

        elif opcode == Op.HALT:
            self.running = False

    def _check_reg(self, idx):
        if idx < 0 or idx >= len(self.registers):
            raise IndexError(f"Register index {idx} out of bounds")
