# ivm/vm.py
import sys
from .opcodes import OpCode
from .structs import CodeObject, Frame

class VirtualMachine:
    def __init__(self):
        self.frame: Frame | None = None
        self.globals: dict = {}
        self.builtins: dict = {
            "tulis": self._builtin_tulis
        }

    def run(self, code_obj: CodeObject):
        """
        Mulai eksekusi dari sebuah code object.
        """
        self.frame = Frame(code_obj)

        while self.frame.ip < len(self.frame.code.instructions):
            opcode_val = self.read_byte()
            opcode = OpCode(opcode_val)

            # TODO: Implement dispatch logic
            self.dispatch(opcode)

        # Eksekusi selesai
        return self.frame.peek()

    def read_byte(self) -> int:
        """Membaca satu byte dari bytecode dan memajukan instruction pointer."""
        byte = self.frame.code.instructions[self.frame.ip]
        self.frame.ip += 1
        return byte

    def read_short(self) -> int:
        """Membaca dua byte (short) untuk argumen jump."""
        low_byte = self.read_byte()
        high_byte = self.read_byte()
        return (high_byte << 8) | low_byte

    def dispatch(self, opcode: OpCode):
        """Menjalankan satu instruksi."""
        if opcode == OpCode.LOAD_CONST:
            const_index = self.read_byte()
            self.frame.push(self.frame.code.constants[const_index])

        elif opcode == OpCode.ADD:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri + kanan)

        elif opcode == OpCode.GREATER_THAN:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri > kanan)

        elif opcode == OpCode.JUMP_IF_FALSE:
            target = self.read_short()
            condition = self.frame.pop()
            if not condition:
                self.frame.ip = target

        elif opcode == OpCode.JUMP:
            target = self.read_short()
            self.frame.ip = target

        elif opcode == OpCode.LOAD_GLOBAL:
            name_index = self.read_byte()
            name = self.frame.code.constants[name_index]
            if name in self.globals:
                self.frame.push(self.globals[name])
            elif name in self.builtins:
                self.frame.push(self.builtins[name])
            else:
                raise NameError(f"Nama global '{name}' tidak terdefinisi")

        elif opcode == OpCode.CALL_FUNCTION:
            arg_count = self.read_byte()

            # Ambil argumen dari stack (mereka berada di paling atas)
            args = []
            for _ in range(arg_count):
                args.append(self.frame.pop())
            args.reverse()

            # Callee berada di bawah argumen
            callee = self.frame.pop()

            # Untuk saat ini, hanya menangani fungsi bawaan
            if callable(callee):
                result = callee(args)
                self.frame.push(result)
            else:
                raise TypeError("Objek tidak dapat dipanggil")

        elif opcode == OpCode.STORE_FAST:
            local_index = self.read_byte()
            value = self.frame.pop()
            self.frame.locals[local_index] = value

        elif opcode == OpCode.LOAD_FAST:
            local_index = self.read_byte()
            value = self.frame.locals[local_index]
            self.frame.push(value)

        elif opcode == OpCode.POP_TOP:
            self.frame.pop()

        else:
            raise NotImplementedError(f"Opcode {opcode.name} belum diimplementasikan")

    # --- Built-in Functions ---
    def _builtin_tulis(self, args: list):
        """Implementasi fungsi bawaan 'tulis'."""
        output = [str(arg) for arg in args]
        print(" ".join(output), file=sys.stdout)
        return None
