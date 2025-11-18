# ivm/vm.py
import sys
from .opcodes import OpCode
from .structs import CodeObject, Frame, MorphFunction

class VirtualMachine:
    def __init__(self):
        self.frames: list[Frame] = []
        self.globals: dict = {}
        self.builtins: dict = {
            "tulis": self._builtin_tulis
        }

    @property
    def frame(self) -> Frame | None:
        return self.frames[-1] if self.frames else None

    def push_frame(self, frame: Frame):
        self.frames.append(frame)

    def pop_frame(self):
        if not self.frames:
            raise RuntimeError("Tidak bisa pop dari call stack kosong")
        return self.frames.pop()

    def run(self, code_obj: CodeObject):
        """
        Mulai eksekusi dari sebuah code object.
        """
        main_frame = Frame(code_obj)
        self.push_frame(main_frame)

        while self.frame:
            # Periksa apakah IP masih dalam batas
            if self.frame.ip >= len(self.frame.code.instructions):
                # Jika ini adalah frame utama, selesai. Jika tidak, return None implisit.
                result = self.frame.pop() if self.frame.stack else None
                self.pop_frame()
                if self.frame:
                    self.frame.push(result)
                continue

            opcode_val = self.read_byte()
            opcode = OpCode(opcode_val)

            self.dispatch(opcode)

        # Eksekusi selesai
        # Nilai hasil akhir mungkin ada di stack frame utama
        return main_frame.peek()

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

        elif opcode == OpCode.LESS_THAN:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri < kanan)

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

        elif opcode == OpCode.STORE_GLOBAL:
            name_index = self.read_byte()
            name = self.frame.code.constants[name_index]
            self.globals[name] = self.frame.pop()

        elif opcode == OpCode.CALL_FUNCTION:
            arg_count = self.read_byte()

            args = []
            for _ in range(arg_count):
                args.append(self.frame.pop())
            args.reverse()

            callee = self.frame.pop()

            if isinstance(callee, MorphFunction):
                if len(args) != len(callee.code_obj.parameters):
                    raise TypeError(
                        f"{callee.name} mengharapkan {len(callee.code_obj.parameters)} argumen, "
                        f"tetapi menerima {len(args)}"
                    )

                # Buat frame baru untuk pemanggilan fungsi
                new_frame = Frame(callee.code_obj, parent=self.frame)

                # Masukkan argumen ke dalam locals frame baru
                for i, arg_name in enumerate(callee.code_obj.parameters):
                    # Kita asumsikan compiler sudah mengatur indeks locals dengan benar
                    new_frame.locals[i] = args[i]

                self.push_frame(new_frame)

            elif callable(callee): # Untuk built-in
                result = callee(args)
                self.frame.push(result)
            else:
                raise TypeError(f"Objek '{type(callee).__name__}' tidak dapat dipanggil")

        elif opcode == OpCode.RETURN_VALUE:
            return_value = self.frame.pop()
            self.pop_frame()
            # Pastikan ada frame sebelumnya untuk mendorong nilai kembali
            if self.frame:
                self.frame.push(return_value)

        elif opcode == OpCode.BUILD_FUNCTION:
            code_obj = self.frame.pop()
            if not isinstance(code_obj, CodeObject):
                raise TypeError("BUILD_FUNCTION mengharapkan CodeObject di stack")

            func = MorphFunction(name=code_obj.name, code_obj=code_obj)
            self.frame.push(func)

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

        elif opcode == OpCode.BUILD_LIST:
            count = self.read_byte()
            elements = []
            for _ in range(count):
                elements.append(self.frame.pop())
            elements.reverse()
            self.frame.push(elements)

        elif opcode == OpCode.LOAD_INDEX:
            index = self.frame.pop()
            target = self.frame.pop()
            # TODO: Tambahkan penanganan error yang lebih baik (misalnya, IndexError)
            self.frame.push(target[index])

        elif opcode == OpCode.STORE_INDEX:
            value = self.frame.pop()
            index = self.frame.pop()
            target = self.frame.pop()
            # TODO: Tambahkan penanganan error yang lebih baik (misalnya, IndexError)
            target[index] = value

        elif opcode == OpCode.BUILD_DICT:
            count = self.read_byte()
            new_dict = {}
            for _ in range(count):
                value = self.frame.pop()
                key = self.frame.pop()
                new_dict[key] = value
            self.frame.push(new_dict)

        else:
            raise NotImplementedError(f"Opcode {opcode.name} belum diimplementasikan")

    # --- Built-in Functions ---
    def _builtin_tulis(self, args: list):
        """Implementasi fungsi bawaan 'tulis'."""
        output = [str(arg) for arg in args]
        print(" ".join(output), file=sys.stdout)
        return None
