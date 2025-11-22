# ... (Previous imports)
from typing import List, Any, Dict, Tuple, Union
from ivm.core.opcodes import Op
from ivm.core.structs import Frame, CodeObject, MorphClass, MorphInstance, BoundMethod
from ivm.stdlib.core import CORE_BUILTINS
from ivm.stdlib.file_io import FILE_IO_BUILTINS
from ivm.stdlib.sistem import SYSTEM_BUILTINS
from ivm.stdlib.fox import FOX_BUILTINS

class StandardVM:
    # ... (__init__ and properties same)
    def __init__(self, max_instructions: int = 1_000_000):
        self.call_stack: List[Frame] = []
        self.registers: List[Any] = [None] * 32
        self.globals: Dict[str, Any] = {}
        self.running: bool = False
        self.max_instructions = max_instructions
        self.instruction_count = 0
        # Hapus global exception_handlers, pindahkan ke Frame
        self._init_builtins()

    def _init_builtins(self):
        self.globals.update(CORE_BUILTINS)
        self.globals.update(FILE_IO_BUILTINS)
        self.globals.update(SYSTEM_BUILTINS)
        self.globals.update(FOX_BUILTINS)

    @property
    def current_frame(self) -> Frame:
        return self.call_stack[-1]

    @property
    def stack(self) -> List[Any]:
        return self.current_frame.stack

    def load(self, code: Union[List[Tuple], CodeObject]):
        if isinstance(code, list):
            main_code = CodeObject(name="<main>", instructions=code)
        elif isinstance(code, CodeObject):
            main_code = code
        else:
            raise TypeError("StandardVM.load expects list or CodeObject")

        main_frame = Frame(code=main_code)
        self.call_stack = [main_frame]
        self.registers = [None] * 32
        self.running = False
        self.instruction_count = 0

    def run(self):
        global _CURRENT_VM
        _CURRENT_VM = self
        self.running = True
        try:
            while self.running and self.call_stack:
                if self.instruction_count >= self.max_instructions:
                    raise RuntimeError(f"Instruction limit exceeded ({self.max_instructions}). Possible infinite loop.")

                frame = self.current_frame
                if frame.pc >= len(frame.code.instructions):
                    self._return_from_frame(None)
                    continue

                instruction = frame.code.instructions[frame.pc]
                frame.pc += 1

                try:
                    self.execute(instruction)
                except Exception as e:
                    # Handle system crashes (RuntimeError, etc.)
                    # Bungkus sebagai error Morph dan lemparkan via mekanisme internal
                    error_obj = {
                            "pesan": str(e),
                            "baris": 0,
                            "kolom": 0,
                            "jenis": "ErrorSistem"
                        }
                    self._handle_exception(error_obj)

                self.instruction_count += 1
        except Exception:
            self.running = False
            raise
        finally:
            _CURRENT_VM = None

    def _return_from_frame(self, val):
        finished_frame = self.call_stack.pop()
        if self.call_stack:
            # If this was a constructor call, we ignore the return value 'val'
            # and instead return the instance 'ini'.
            if finished_frame.is_init_call:
                instance = finished_frame.locals.get('ini')
                self.current_frame.stack.append(instance)
            else:
                self.current_frame.stack.append(val)
        else:
            self.running = False

    def execute(self, instr: Tuple):
        opcode = instr[0]

        # ... (Stack, Arith, Logic, Reg, Hybrid, Var, Data, Flow - Same as before)
        if opcode == Op.PUSH_CONST: self.stack.append(instr[1])
        elif opcode == Op.POP: self.stack.pop() if self.stack else None
        elif opcode == Op.DUP: self.stack.append(self.stack[-1]) if self.stack else None
        elif opcode == Op.ADD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a + b)
        elif opcode == Op.SUB: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a - b)
        elif opcode == Op.MUL: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a * b)
        elif opcode == Op.DIV: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a / b)
        elif opcode == Op.MOD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a % b)
        elif opcode == Op.EQ: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a == b)
        elif opcode == Op.NEQ: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a != b)
        elif opcode == Op.GT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a > b)
        elif opcode == Op.LT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a < b)
        elif opcode == Op.GTE: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a >= b)
        elif opcode == Op.LTE: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a <= b)
        elif opcode == Op.NOT: val = self.stack.pop(); self.stack.append(not val)
        elif opcode == Op.LOAD_REG: self.registers[instr[1]] = instr[2]
        elif opcode == Op.MOVE_REG: self.registers[instr[1]] = self.registers[instr[2]]
        elif opcode == Op.ADD_REG: self.registers[instr[1]] = self.registers[instr[2]] + self.registers[instr[3]]
        elif opcode == Op.PUSH_FROM_REG: self.stack.append(self.registers[instr[1]])
        elif opcode == Op.POP_TO_REG: self.registers[instr[1]] = self.stack.pop()
        elif opcode == Op.LOAD_VAR:
            name = instr[1]
            if name in self.globals: self.stack.append(self.globals[name])
            else: raise RuntimeError(f"Global '{name}' not found.")
        elif opcode == Op.STORE_VAR: self.globals[instr[1]] = self.stack.pop()
        elif opcode == Op.LOAD_LOCAL:
            name = instr[1]
            if name in self.current_frame.locals: self.stack.append(self.current_frame.locals[name])
            elif name in self.globals: self.stack.append(self.globals[name])
            else: raise RuntimeError(f"Variable '{name}' not found.")
        elif opcode == Op.STORE_LOCAL: self.current_frame.locals[instr[1]] = self.stack.pop()
        elif opcode == Op.BUILD_LIST:
            c = instr[1]; el = [self.stack.pop() for _ in range(c)]; el.reverse(); self.stack.append(el)
        elif opcode == Op.BUILD_DICT:
            c = instr[1]; d = {};
            for _ in range(c): v = self.stack.pop(); k = self.stack.pop(); d[k] = v
            self.stack.append(d)
        elif opcode == Op.LOAD_INDEX: i = self.stack.pop(); t = self.stack.pop(); self.stack.append(t[i])
        elif opcode == Op.STORE_INDEX: v = self.stack.pop(); i = self.stack.pop(); t = self.stack.pop(); t[i] = v
        elif opcode == Op.UNPACK_SEQUENCE:
            count = instr[1]
            # Perubahan: Peek seq, jangan pop!
            seq = self.stack[-1]
            if len(seq) < count: raise ValueError(f"Tidak cukup nilai untuk unpack (diharapkan {count}, dapat {len(seq)})")
            for i in range(count - 1, -1, -1):
                self.stack.append(seq[i])
        elif opcode == Op.CHECK_LEN:
            count = instr[1]
            seq = self.stack[-1] # Peek, jangan pop karena nanti mau dipakai
            self.stack.append(len(seq) == count)
        elif opcode == Op.CHECK_LEN_MIN:
            count = instr[1]
            seq = self.stack[-1]
            self.stack.append(len(seq) >= count)
        elif opcode == Op.SNAPSHOT:
            self.current_frame.snapshots.append(len(self.stack))
        elif opcode == Op.RESTORE:
            if not self.current_frame.snapshots:
                raise RuntimeError("Stack Underflow: Tidak ada snapshot untuk direstore")
            target_len = self.current_frame.snapshots.pop()
            # Potong stack sampai target_len.
            # List slice in place: del self.stack[target_len:]
            del self.stack[target_len:]
        elif opcode == Op.DISCARD_SNAPSHOT:
            if self.current_frame.snapshots:
                self.current_frame.snapshots.pop()
        elif opcode == Op.JMP: self.current_frame.pc = instr[1]
        elif opcode == Op.JMP_IF_FALSE:
            if not self.stack.pop(): self.current_frame.pc = instr[1]
        elif opcode == Op.JMP_IF_TRUE:
            if self.stack.pop(): self.current_frame.pc = instr[1]

        # === Classes & Objects ===
        elif opcode == Op.BUILD_CLASS:
            methods = self.stack.pop()
            name = self.stack.pop()
            klass = MorphClass(name=name, methods=methods)
            self.stack.append(klass)

        elif opcode == Op.LOAD_ATTR:
            name = instr[1]
            obj = self.stack.pop()
            if isinstance(obj, MorphInstance):
                if name in obj.properties: self.stack.append(obj.properties[name])
                elif name in obj.klass.methods:
                    method = obj.klass.methods[name]
                    self.stack.append(BoundMethod(instance=obj, method=method))
                else: raise AttributeError(f"Instance '{obj}' has no attribute '{name}'")
            elif isinstance(obj, MorphClass):
                 if name in obj.methods: self.stack.append(obj.methods[name])
                 else: raise AttributeError(f"Class '{obj.name}' has no attribute '{name}'")
            elif isinstance(obj, dict):
                # Support akses key dictionary sebagai atribut (terutama untuk ObjekError/Result)
                if name in obj: self.stack.append(obj[name])
                else: raise AttributeError(f"Dictionary has no key '{name}'")
            else:
                if hasattr(obj, name): self.stack.append(getattr(obj, name))
                else: raise AttributeError(f"Object '{obj}' has no attribute '{name}'")

        elif opcode == Op.STORE_ATTR:
            name = instr[1]
            val = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, MorphInstance): obj.properties[name] = val
            else: setattr(obj, name, val)

        elif opcode == Op.IS_INSTANCE:
            # Sederhana: Cek apakah objek adalah tipe bawaan tertentu
            # Di masa depan, ini harus support cek instance MorphClass
            type_name = instr[1]
            obj = self.stack.pop()
            result = False
            if type_name == "Daftar" and isinstance(obj, list): result = True
            elif type_name == "Kamus" and isinstance(obj, dict): result = True
            elif type_name == "Teks" and isinstance(obj, str): result = True
            elif type_name == "Angka" and isinstance(obj, (int, float)): result = True
            # TODO: Support Varian dan Class
            self.stack.append(result)

        # === Functions (Updated for Class Init) ===
        elif opcode == Op.CALL:
            arg_count = instr[1]
            args = []
            for _ in range(arg_count): args.append(self.stack.pop())
            args.reverse()

            func_obj = self.stack.pop()

            if isinstance(func_obj, BoundMethod):
                args.insert(0, func_obj.instance) # 'ini'
                self.call_function_internal(func_obj.method, args)

            elif isinstance(func_obj, MorphClass):
                instance = MorphInstance(klass=func_obj)
                if 'inisiasi' in func_obj.methods:
                    init_method = func_obj.methods['inisiasi']
                    args.insert(0, instance)
                    self.call_function_internal(init_method, args, is_init=True)
                else:
                    self.stack.append(instance)

            elif callable(func_obj) and not isinstance(func_obj, CodeObject):
                try:
                    # Handle builtins yang mengharapkan multiple args, bukan list args
                    # Kita unpack list args menjadi positional args
                    self.stack.append(func_obj(*args))
                except TypeError as e: raise TypeError(f"Error calling builtin: {e}")

            elif isinstance(func_obj, CodeObject):
                self.call_function_internal(func_obj, args)

            else:
                raise TypeError(f"Cannot call object of type {type(func_obj)}")

        elif opcode == Op.RET:
            val = None
            if self.stack: val = self.stack.pop()
            self._return_from_frame(val)

        # === Exception Handling ===
        elif opcode == Op.PUSH_TRY:
            handler_pc = instr[1]
            self.current_frame.exception_handlers.append(handler_pc)

        elif opcode == Op.POP_TRY:
            if self.current_frame.exception_handlers:
                self.current_frame.exception_handlers.pop()

        elif opcode == Op.THROW:
            err_val = self.stack.pop()
            self._handle_exception(err_val)

        # === Modules ===
        elif opcode == Op.IMPORT:
            module_path = instr[1]
            # TODO: Implementasi proper module loader.
            # Saat ini kita mock dengan dictionary global untuk stdlib yang known.
            # Di masa depan, ini harus memanggil sistem module loader yang sebenarnya.

            # Mock stdlib loading logic
            if module_path == "transisi.stdlib.wajib.teks":
                from transisi.stdlib.wajib import _teks_internal
                self.stack.append(_teks_internal)
            elif module_path == "transisi.stdlib.wajib.koleksi":
                from transisi.stdlib.wajib import _koleksi_internal
                self.stack.append(_koleksi_internal)
            elif module_path == "transisi.stdlib.wajib._teks_internal":
                from transisi.stdlib.wajib import _teks_internal
                self.stack.append(_teks_internal)
            elif module_path == "transisi.stdlib.wajib._koleksi_internal":
                from transisi.stdlib.wajib import _koleksi_internal
                self.stack.append(_koleksi_internal)
            # Mock tambahan untuk testing module loader di masa depan
            elif module_path.startswith("tests.samples"):
                 # Placeholder untuk test module loading
                 self.stack.append({"pesan": "Modul Test Loaded"})
            else:
                raise ImportError(f"Modul '{module_path}' tidak ditemukan (Mock Import).")

        # === IO ===
        elif opcode == Op.PRINT:
            count = instr[1]; args = [self.stack.pop() for _ in range(count)]; print(*reversed(args))

        elif opcode == Op.HALT:
            self.running = False

    def call_function_internal(self, func_obj: CodeObject, args: List[Any], is_init: bool = False):
        new_frame = Frame(code=func_obj, is_init_call=is_init)

        if len(args) != len(func_obj.arg_names):
            raise TypeError(f"Function '{func_obj.name}' expects {len(func_obj.arg_names)} arguments, got {len(args)}")

        for name, val in zip(func_obj.arg_names, args):
            new_frame.locals[name] = val

        self.call_stack.append(new_frame)

    def _check_reg(self, idx):
        if idx < 0 or idx >= len(self.registers): raise IndexError("Reg idx out of bounds")

    def _handle_exception(self, error_obj):
        """
        Mencari handler di stack frame saat ini, atau unwinding stack sampai ketemu.
        Jika error_obj bukan dict (dan bukan instance ObjekError), bungkus jadi dict standar.
        Menambahkan stack trace (jejak) ke objek error.
        """
        # Standarisasi Error Object
        if not isinstance(error_obj, dict) and not hasattr(error_obj, 'pesan'):
             error_obj = {
                "pesan": str(error_obj),
                "baris": 0,
                "kolom": 0,
                "jenis": "ErrorManual"
            }

        # Tambahkan Stack Trace
        trace = []
        for f in self.call_stack:
            trace.append(f"{f.code.name} at PC {f.pc}")

        if isinstance(error_obj, dict):
            error_obj['jejak'] = trace
        elif hasattr(error_obj, 'jejak'): # ObjekError class
            error_obj.jejak = trace

        while self.call_stack:
            frame = self.current_frame
            if frame.exception_handlers:
                # Handler found in current frame
                handler_pc = frame.exception_handlers.pop()
                frame.stack.append(error_obj)
                frame.pc = handler_pc
                return
            else:
                # No handler in current frame, pop frame (unwind)
                if len(self.call_stack) > 1:
                    self.call_stack.pop()
                else:
                    # Stack habis, panic
                    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")

        # Should not be reached if stack check works
        raise RuntimeError(f"Unhandled Panic: {error_obj}")

    def call_function_sync(self, func_obj: CodeObject, args: List[Any]) -> Any:
        self.call_function_internal(func_obj, args)
        start_depth = len(self.call_stack)
        while len(self.call_stack) >= start_depth and self.running:
             if self.instruction_count >= self.max_instructions:
                raise RuntimeError(f"Instruction limit exceeded")
             frame = self.current_frame
             if frame.pc >= len(frame.code.instructions):
                self._return_from_frame(None)
                continue
             instr = frame.code.instructions[frame.pc]
             frame.pc += 1
             self.execute(instr)
             self.instruction_count += 1
        return self.stack.pop()
