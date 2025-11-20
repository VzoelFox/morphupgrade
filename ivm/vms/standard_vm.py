from typing import List, Any, Dict, Tuple, Union
from ivm.core.opcodes import Op
from ivm.core.structs import Frame, CodeObject

class StandardVM:
    def __init__(self):
        self.call_stack: List[Frame] = []
        self.registers: List[Any] = [None] * 32  # 32 General Purpose Registers
        self.globals: Dict[str, Any] = {}        # Global variables
        self.running: bool = False

    @property
    def current_frame(self) -> Frame:
        return self.call_stack[-1]

    @property
    def stack(self) -> List[Any]:
        return self.current_frame.stack

    def load(self, code: Union[List[Tuple], CodeObject]):
        if isinstance(code, list):
            # Legacy support: Wrap list in CodeObject
            main_code = CodeObject(name="<main>", instructions=code)
        elif isinstance(code, CodeObject):
            main_code = code
        else:
            raise TypeError("StandardVM.load expects list or CodeObject")

        main_frame = Frame(code=main_code)
        self.call_stack = [main_frame]
        self.registers = [None] * 32
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.call_stack:
            frame = self.current_frame

            if frame.pc >= len(frame.code.instructions):
                # Implicit return None if end of code reached
                self._return_from_frame(None)
                continue

            instruction = frame.code.instructions[frame.pc]
            frame.pc += 1
            self.execute(instruction)

    def _return_from_frame(self, val):
        finished_frame = self.call_stack.pop()
        if self.call_stack:
            # Push return value to caller's stack
            self.current_frame.stack.append(val)
        else:
            # Program finished
            self.running = False

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
            if name in self.globals:
                self.stack.append(self.globals[name])
            else:
                raise RuntimeError(f"Global variable '{name}' not found.")

        elif opcode == Op.STORE_VAR:
            name = instr[1]
            val = self.stack.pop()
            self.globals[name] = val

        elif opcode == Op.LOAD_LOCAL:
            name = instr[1]
            if name in self.current_frame.locals:
                self.stack.append(self.current_frame.locals[name])
            elif name in self.globals:
                # Fallback to global (closure support lite)
                self.stack.append(self.globals[name])
            else:
                raise RuntimeError(f"Variable '{name}' not found (checked local and global).")

        elif opcode == Op.STORE_LOCAL:
            name = instr[1]
            val = self.stack.pop()
            self.current_frame.locals[name] = val

        # === Data Structures ===
        elif opcode == Op.BUILD_LIST:
            count = instr[1]
            elements = []
            for _ in range(count):
                elements.append(self.stack.pop())
            elements.reverse() # Stack is LIFO, so reverse to preserve order
            self.stack.append(elements)

        elif opcode == Op.BUILD_DICT:
            count = instr[1]
            new_dict = {}
            # Pairs are pushed as Key, Value. So stack top is Value, then Key.
            # We iterate `count` times.
            for _ in range(count):
                val = self.stack.pop()
                key = self.stack.pop()
                new_dict[key] = val
            self.stack.append(new_dict)

        elif opcode == Op.LOAD_INDEX:
            index = self.stack.pop()
            target = self.stack.pop()
            try:
                self.stack.append(target[index])
            except (IndexError, KeyError):
                raise IndexError(f"Index/Key '{index}' not found or out of range.")
            except TypeError:
                raise TypeError(f"Object of type {type(target)} is not subscriptable.")

        elif opcode == Op.STORE_INDEX:
            val = self.stack.pop()
            index = self.stack.pop()
            target = self.stack.pop()
            try:
                target[index] = val
            except (IndexError, KeyError):
                # For dicts, this shouldn't fail usually. For lists, it might.
                 raise IndexError(f"Index '{index}' out of range for assignment.")
            except TypeError:
                 raise TypeError(f"Object of type {type(target)} does not support item assignment.")

        # === Control Flow ===
        elif opcode == Op.JMP:
            target = instr[1]
            self.current_frame.pc = target

        elif opcode == Op.JMP_IF_FALSE:
            target = instr[1]
            condition = self.stack.pop()
            if not condition:
                self.current_frame.pc = target

        elif opcode == Op.JMP_IF_TRUE:
            target = instr[1]
            condition = self.stack.pop()
            if condition:
                self.current_frame.pc = target

        # === Functions ===
        elif opcode == Op.CALL:
            arg_count = instr[1]
            args = []
            for _ in range(arg_count):
                args.append(self.stack.pop())
            # Args are popped in reverse order (last arg is top)
            args.reverse()

            func_obj = self.stack.pop()

            if not isinstance(func_obj, CodeObject):
                raise TypeError(f"Cannot call object of type {type(func_obj)}")

            new_frame = Frame(code=func_obj)

            # Map arguments to local variables
            if len(args) != len(func_obj.arg_names):
                raise TypeError(f"Function '{func_obj.name}' expects {len(func_obj.arg_names)} arguments, got {len(args)}")

            for name, val in zip(func_obj.arg_names, args):
                new_frame.locals[name] = val

            self.call_stack.append(new_frame)

        elif opcode == Op.RET:
            val = None
            if self.stack:
                val = self.stack.pop()
            self._return_from_frame(val)

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
