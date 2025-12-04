# ... (Previous imports)
from typing import List, Any, Dict, Tuple, Union, Optional
from ivm.core.opcodes import Op
from ivm.core.structs import Frame, CodeObject, MorphClass, MorphInstance, BoundMethod, SuperBoundMethod, MorphFunction, MorphVariant, MorphGenerator
from transisi.common.result import Result
from ivm.stdlib.core import CORE_BUILTINS
from ivm.stdlib.file_io import FILE_IO_BUILTINS
from ivm.stdlib.sistem import SYSTEM_BUILTINS
from ivm.stdlib.fox import FOX_BUILTINS
from ivm.stdlib.loader import jalan_biner
from ivm.vm_context import set_current_vm

class StandardVM:
    # ... (__init__ and properties same)
    def __init__(self, max_instructions: int = 50_000_000, script_args: List[str] = None):
        self.call_stack: List[Frame] = []
        self.registers: List[Any] = [None] * 32
        self.globals: Dict[str, Any] = {}
        self.running: bool = False
        self.max_instructions = max_instructions
        self.instruction_count = 0
        # Hapus global exception_handlers, pindahkan ke Frame
        self.loaded_modules: Dict[str, Dict[str, Any]] = {}
        self._init_builtins()
        self.globals["argumen_sistem"] = script_args if script_args is not None else []

    def _init_builtins(self):
        self.globals.update(CORE_BUILTINS)
        self.globals.update(FILE_IO_BUILTINS)
        self.globals.update(SYSTEM_BUILTINS)
        self.globals.update(FOX_BUILTINS)
        self.globals["_jalan_biner_internal"] = jalan_biner

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

        # Main frame uses the initial global scope
        main_frame = Frame(code=main_code, globals=self.globals)
        self.call_stack = [main_frame]
        self.registers = [None] * 32
        self.running = False
        self.instruction_count = 0

    def run(self):
        set_current_vm(self)
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
            set_current_vm(None)

    def _return_from_frame(self, val):
        finished_frame = self.call_stack.pop()
        if self.call_stack:
            # Restore globals from the frame we are returning to
            self.globals = self.current_frame.globals

            # If this was a constructor call, we ignore the return value 'val'
            # and instead return the instance 'ini'.
            if finished_frame.is_init_call:
                instance = finished_frame.locals.get('ini')
                self.current_frame.stack.append(instance)
            else:
                self.current_frame.stack.append(val)
        else:
            self.running = False

    def _lookup_method(self, klass: MorphClass, name: str) -> Tuple[Optional[CodeObject], Optional[MorphClass]]:
        curr = klass
        while curr:
            if name in curr.methods:
                return curr.methods[name], curr
            curr = curr.superclass
        return None, None

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
        elif opcode == Op.AND: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a and b)
        elif opcode == Op.OR: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a or b)
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
        elif opcode == Op.SLICE:
            # Stack: [obj, start, end] -> Pop 3 -> Push Result
            end = self.stack.pop()
            start = self.stack.pop()
            obj = self.stack.pop()

            # Handle nil/None for slicing to end
            s_idx = start if start is not None else 0
            e_idx = end if end is not None else len(obj)

            if isinstance(obj, (str, list, tuple, bytes, bytearray)):
                self.stack.append(obj[s_idx:e_idx])
            else:
                raise TypeError(f"Objek tipe '{type(obj).__name__}' tidak mendukung slicing/iris.")

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
            superclass = self.stack.pop()
            name = self.stack.pop()
            # Capture current globals for class methods context
            klass = MorphClass(name=name, methods=methods, superclass=superclass, globals=self.globals)
            self.stack.append(klass)

        elif opcode == Op.LOAD_ATTR:
            name = instr[1]
            obj = self.stack.pop()
            if isinstance(obj, MorphInstance):
                if name == "__class__": self.stack.append(obj.klass)
                elif name in obj.properties: self.stack.append(obj.properties[name])
                else:
                    method, def_cls = self._lookup_method(obj.klass, name)
                    if method:
                        self.stack.append(BoundMethod(instance=obj, method=method, defining_class=def_cls))
                    else: raise AttributeError(f"Instance '{obj}' has no attribute '{name}'")
            elif isinstance(obj, MorphClass):
                 # Perbaikan: Izinkan akses ke properti meta-class seperti 'name'
                 if name == "name":
                     self.stack.append(obj.name)
                 else:
                     method, def_cls = self._lookup_method(obj, name)
                     if method: self.stack.append(method)
                     else: raise AttributeError(f"Class '{obj.name}' has no attribute '{name}'")
            elif isinstance(obj, dict):
                # Support akses key dictionary sebagai atribut (terutama untuk ObjekError/Result)
                if name == "punya":
                    # Return helper function for .punya(key)
                    def dict_punya(key):
                        return key in obj
                    self.stack.append(dict_punya)
                elif name in obj: self.stack.append(obj[name])
                else: raise AttributeError(f"Dictionary has no key '{name}'")
            elif isinstance(obj, Result):
                if name == "sukses": self.stack.append(obj.is_sukses())
                elif name == "data": self.stack.append(obj.unwrap() if obj.is_sukses() else None)
                elif name == "error": self.stack.append(obj.unwrap_error() if obj.is_gagal() else None)
                else: raise AttributeError(f"Result object has no attribute '{name}'")
            elif isinstance(obj, MorphVariant):
                 # Support access to variant content by index via attribute (e.g., .0, .1) or named if we track it?
                 # Current MorphVariant only has args list.
                 # If we want named fields, we need to store them. But `tipe` decl only has ordered params.
                 # Access via index like tuple? Or allow unpacking.
                 # User typically matches, doesn't access directly.
                 raise AttributeError(f"Varian '{obj.name}' tidak mendukung akses atribut langsung. Gunakan jodohkan.")
            else:
                if hasattr(obj, name): self.stack.append(getattr(obj, name))
                else: raise AttributeError(f"Object '{obj}' has no attribute '{name}'")

        elif opcode == Op.STORE_ATTR:
            name = instr[1]
            val = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, MorphInstance): obj.properties[name] = val
            else: setattr(obj, name, val)

        elif opcode == Op.LOAD_SUPER_METHOD:
            method_name = instr[1]
            instance = self.stack.pop()

            start_class = self.current_frame.defining_class
            if start_class is None:
                start_class = instance.klass

            superclass = start_class.superclass
            if not superclass:
                raise RuntimeError(f"Cannot call 'induk': class '{start_class.name}' has no superclass.")

            method, def_cls = self._lookup_method(superclass, method_name)
            if not method:
                raise AttributeError(f"Superclass '{superclass.name}' has no method '{method_name}'.")

            self.stack.append(SuperBoundMethod(instance=instance, method=method, defining_class=def_cls))

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

        elif opcode == Op.IS_VARIANT:
            variant_name = instr[1]
            obj = self.stack.pop()
            result = False
            if isinstance(obj, MorphVariant):
                result = (obj.name == variant_name)
            elif isinstance(obj, Result):
                # Compat for Result object
                if variant_name == "Sukses": result = obj.is_sukses()
                elif variant_name == "Gagal": result = obj.is_gagal()
            self.stack.append(result)

        elif opcode == Op.UNPACK_VARIANT:
            obj = self.stack.pop()
            if isinstance(obj, MorphVariant):
                # Push all args to stack
                for arg in reversed(obj.args):
                    self.stack.append(arg)
            elif isinstance(obj, Result):
                # Compat for Result
                if obj.is_sukses(): self.stack.append(obj.unwrap())
                else: self.stack.append(obj.unwrap_error())
            else:
                raise TypeError(f"Objek bukan varian: {type(obj)} {obj}")

        elif opcode == Op.BUILD_VARIANT:
            variant_name = instr[1]
            count = instr[2]
            args = [self.stack.pop() for _ in range(count)]
            args.reverse()
            variant = MorphVariant(name=variant_name, args=args)
            self.stack.append(variant)

        elif opcode == Op.BUILD_FUNCTION:
            # Self-Hosting Bridge: Create CodeObject from Dict
            # Stack: [func_def_dict]
            # func_def keys: "nama", "instruksi", "args" (optional)
            func_def = self.stack.pop()
            if not isinstance(func_def, dict):
                 raise TypeError("BUILD_FUNCTION expects a dictionary definition.")

            name = func_def.get("nama", "<lambda>")
            instr_raw = func_def.get("instruksi", [])
            arg_names = func_def.get("args", [])
            tipe_func = func_def.get("tipe", "script")

            # Validate instructions format? Usually list of lists/tuples
            # Convert list-of-lists (from Morph) to list-of-tuples (for VM) if needed
            instructions = []
            for ins in instr_raw:
                # Morph array: [op, arg]
                # VM expects: (op, arg, ...)
                if isinstance(ins, list):
                    instructions.append(tuple(ins))
                else:
                    instructions.append(ins)

            code_obj = CodeObject(
                name=name,
                instructions=instructions,
                arg_names=arg_names,
                is_generator=(tipe_func == "generator")
            )
            # Create MorphFunction to capture current globals (closure)
            func_obj = MorphFunction(code=code_obj, globals=self.globals)
            self.stack.append(func_obj)

        # === Functions (Updated for Class Init) ===
        elif opcode == Op.CALL:
            arg_count = instr[1]
            args = []
            for _ in range(arg_count): args.append(self.stack.pop())
            args.reverse()

            func_obj = self.stack.pop()

            if isinstance(func_obj, SuperBoundMethod):
                # Untuk panggilan `induk`, `ini` (instance) harus disisipkan secara manual
                # sama seperti BoundMethod biasa.
                args.insert(0, func_obj.instance) # 'ini'
                self.call_function_internal(
                    func_obj.method,
                    args,
                    context_globals=func_obj.defining_class.globals if func_obj.defining_class else func_obj.instance.klass.superclass.globals,
                    defining_class=func_obj.defining_class
                )
            elif isinstance(func_obj, BoundMethod):
                args.insert(0, func_obj.instance) # 'ini'
                # Use class globals for method execution
                self.call_function_internal(
                    func_obj.method, args,
                    context_globals=func_obj.defining_class.globals if func_obj.defining_class else func_obj.instance.klass.globals,
                    defining_class=func_obj.defining_class
                )

            elif isinstance(func_obj, MorphClass):
                instance = MorphInstance(klass=func_obj)
                init_method, def_cls = self._lookup_method(func_obj, 'inisiasi')
                if init_method:
                    args.insert(0, instance)
                    # Use class globals for constructor execution
                    self.call_function_internal(
                        init_method, args, is_init=True,
                        context_globals=def_cls.globals,
                        defining_class=def_cls
                    )
                else:
                    self.stack.append(instance)

            elif isinstance(func_obj, (CodeObject, MorphFunction)):
                code_to_run = func_obj.code if isinstance(func_obj, MorphFunction) else func_obj
                if code_to_run.is_generator:
                    # Create a new frame but don't execute it. Wrap it in a generator object.
                    new_frame = Frame(code=code_to_run, globals=self.globals)
                    for name, val in zip(code_to_run.arg_names, args):
                        new_frame.locals[name] = val
                    gen_obj = MorphGenerator(frame=new_frame, status="suspended")
                    self.stack.append(gen_obj)
                else:
                    self.call_function_internal(func_obj, args)

            elif callable(func_obj):
                try:
                    self.stack.append(func_obj(*args))
                except TypeError as e:
                    raise TypeError(f"Error calling builtin '{func_obj}': {e}")

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
            # Jika ini modul internal Python, load langsung
            if module_path in ["transisi.stdlib.wajib._teks_internal", "transisi.stdlib.wajib._koleksi_internal"]:
                # Import dinamis modul python
                import importlib
                import sys

                if module_path in sys.modules:
                    mod = importlib.reload(sys.modules[module_path])
                else:
                    mod = importlib.import_module(module_path)

                self.stack.append(mod)
                # Don't return here, continue to next opcode

            else:
                # Jika bukan internal, gunakan load_module (untuk file .fox)
                try:
                    module_obj = self.load_module(module_path)
                    self.stack.append(module_obj)
                except Exception as e:
                    # Rethrow sebagai error VM jika perlu, atau biarkan handler tangkap
                    raise ImportError(f"Gagal memuat modul '{module_path}': {e}")

        elif opcode == Op.IMPORT_NATIVE:
            # FFI: Meminjam library Python asli
            module_name = instr[1]
            import importlib
            try:
                mod = importlib.import_module(module_name)
                self.stack.append(mod)
            except ImportError as e:
                raise ImportError(f"Gagal meminjam modul Python '{module_name}': {e}")

        elif opcode == Op.LEN:
            obj = self.stack.pop()
            try:
                self.stack.append(len(obj))
            except TypeError:
                self.stack.append(0)

        elif opcode == Op.TYPE:
            obj = self.stack.pop()
            from ivm.stdlib.core import builtins_tipe
            self.stack.append(builtins_tipe(obj))

        # === IO ===
        elif opcode == Op.PRINT:
            count = instr[1]; args = [self.stack.pop() for _ in range(count)]; print(*reversed(args))

        elif opcode == Op.PRINT_RAW:
            val = self.stack.pop()
            print(val, end="", flush=True)

        elif opcode == Op.HALT:
            self.running = False

        elif opcode == Op.YIELD:
            # Pop value to yield
            val = self.stack.pop()

            # Current frame is the generator frame
            gen_frame = self.call_stack.pop()

            # Wrap in MorphGenerator
            gen_obj = MorphGenerator(frame=gen_frame, status="suspended")

            # We need to return (val, gen_obj) to the caller.
            # The caller frame is now at self.call_stack[-1].
            # We push a Variant "Momen(nilai, kelanjutan)"

            moment = MorphVariant("Momen", [val, gen_obj])

            if self.call_stack:
                self.current_frame.stack.append(moment)
                # Restore globals of caller
                self.globals = self.current_frame.globals
            else:
                # Yielded from main?
                print(f"Yielded: {val}")
                self.running = False

        elif opcode == Op.RESUME:
            # Pop Generator
            gen_obj = self.stack.pop()
            if not isinstance(gen_obj, MorphGenerator):
                raise TypeError("RESUME butuh Generator")

            if gen_obj.status != "suspended":
                raise RuntimeError("Generator tidak bisa di-resume (mungkin sudah selesai)")

            # Push Generator Frame back to stack
            self.call_stack.append(gen_obj.frame)
            self.globals = gen_obj.frame.globals

            # Push 'nil' (or resumption value) to Generator's stack
            # (Result of 'bekukan' expression inside generator)
            gen_obj.frame.stack.append(None)

    def call_function_internal(self, func_obj: Union[CodeObject, MorphFunction], args: List[Any], is_init: bool = False, context_globals: Dict[str, Any] = None, defining_class: MorphClass = None):
        if isinstance(func_obj, MorphFunction):
            code = func_obj.code
            new_globals = func_obj.globals
        else:
            code = func_obj
            # If explicit context provided (e.g. from Class), use it. Otherwise inherit.
            new_globals = context_globals if context_globals is not None else self.globals

        new_frame = Frame(code=code, globals=new_globals, is_init_call=is_init, defining_class=defining_class)

        # Periksa jumlah argumen, izinkan argumen yang lebih sedikit (diisi dengan None/nil)
        expected_argc = len(code.arg_names)
        actual_argc = len(args)
        if actual_argc > expected_argc:
            raise TypeError(
                f"Panggilan fungsi '{code.name}' salah: "
                f"mengharapkan paling banyak {expected_argc} argumen, tetapi mendapat {actual_argc}."
            )

        # Isi argumen yang diberikan
        for i in range(actual_argc):
            new_frame.locals[code.arg_names[i]] = args[i]

        # Isi sisa argumen yang tidak diberikan dengan None (nil)
        if actual_argc < expected_argc:
            for i in range(actual_argc, expected_argc):
                new_frame.locals[code.arg_names[i]] = None

        self.call_stack.append(new_frame)
        self.globals = new_globals

    def _check_reg(self, idx):
        if idx < 0 or idx >= len(self.registers): raise IndexError("Reg idx out of bounds")

    def load_module(self, module_path: str) -> Dict[str, Any]:
        """
        Memuat modul .fox atau .mvm dari path, kompilasi/parse, dan eksekusi.
        Mengembalikan dictionary hasil ekspor (globals modul tersebut).
        """
        # 1. Resolve Path
        # Jika path diakhiri .fox atau .mvm, gunakan langsung.
        import os
        if module_path.endswith('.fox') or module_path.endswith('.mvm'):
            # Cek apakah path relatif atau absolut
            if os.path.exists(module_path):
                file_path_str = module_path
            else:
                 # Jika tidak ditemukan, coba cari relatif terhadap file yang sedang dieksekusi
                 # (Jika ada context frame)
                 if self.call_stack:
                     caller_file = self.current_frame.code.filename
                     if caller_file and caller_file != "<main>" and caller_file != "<module>":
                         base_dir = os.path.dirname(caller_file)
                         possible_path = os.path.join(base_dir, module_path)
                         if os.path.exists(possible_path):
                             file_path_str = possible_path
                         else:
                             # Fallback ke pencarian standar
                             file_path_str = module_path
                     else:
                         file_path_str = module_path
                 else:
                     file_path_str = module_path

            # HACK: Support path "cotc(stdlib)/..."
            # Bootstrap Fix: Force mapping to greenfield/cotc/stdlib regardless of caller context
            if "cotc(stdlib)" in file_path_str:
                # Jika kita di root repo dan folder greenfield ada
                greenfield_path = file_path_str.replace("cotc(stdlib)", "greenfield/cotc/stdlib")
                if os.path.exists(greenfield_path):
                    file_path_str = greenfield_path

                # Fallback: Jika path relatif
                elif not os.path.exists(file_path_str):
                     if self.call_stack:
                         caller_file = self.current_frame.code.filename
                         if caller_file:
                             base_dir = os.path.dirname(caller_file)
                             joined = os.path.join(base_dir, module_path)
                             if os.path.exists(joined):
                                 file_path_str = joined

        else:
             # Asumsi module_path seperti "tests.samples.hello"
             # Ubah jadi path file: "tests/samples/hello.fox"
             file_path_str = module_path.replace('.', '/') + '.fox'

        if not os.path.exists(file_path_str):
            raise FileNotFoundError(f"File modul tidak ditemukan: {file_path_str}")

        if file_path_str in self.loaded_modules:
            return self.loaded_modules[file_path_str]

        # 2. Read & Compile/Load
        code_obj = None

        if file_path_str.endswith('.mvm'):
            with open(file_path_str, 'rb') as f:
                binary_data = f.read()
            # Cek Magic Bytes "VZOEL FOXS"
            if binary_data[:10] != b"VZOEL FOXS":
                raise ValueError(f"File .mvm tidak valid (Magic Header mismatch): {file_path_str}")

            # Skip Header (16 bytes)
            # Magic(10) + Ver(1) + Flags(1) + TS(4) = 16
            payload = binary_data[16:]

            # Deserialisasi Payload
            # Kita butuh parser biner sederhana di sini
            from ivm.core.deserializer import deserialize_code_object
            code_obj = deserialize_code_object(payload, filename=file_path_str)

        else:
            # .fox source file
            with open(file_path_str, 'r', encoding='utf-8') as f:
                source = f.read()

            # 3. Compile (Lazy Imports untuk hindari circular dependency)
            from transisi.lx import Leksikal
            from transisi.crusher import Pengurai
            from ivm.compiler import Compiler

            lexer = Leksikal(source, nama_file=file_path_str)
            tokens, err = lexer.buat_token()
            if err: raise SyntaxError(f"Lexer Error di {module_path}: {err}")

            parser = Pengurai(tokens)
            ast = parser.urai()
            if not ast:
                err_msg = "\n".join([f"{e[1]}" for e in parser.daftar_kesalahan])
                raise SyntaxError(f"Parser Error di {module_path}: {err_msg}")

            compiler = Compiler()
            code_obj = compiler.compile(ast, filename=file_path_str)

        # 4. Execute Isolated
        # Simpan globals saat ini
        saved_globals = self.globals
        # Simpan exception handlers dari frame pemanggil
        saved_handlers = list(self.current_frame.exception_handlers) if self.call_stack else []

        # Buat env baru untuk modul, tapi sertakan builtins
        module_globals = {}
        module_globals.update(CORE_BUILTINS)
        module_globals.update(FILE_IO_BUILTINS)
        module_globals.update(SYSTEM_BUILTINS)
        module_globals.update(FOX_BUILTINS)

        # Inject argumen_sistem dari VM context
        if "argumen_sistem" in self.globals:
            module_globals["argumen_sistem"] = self.globals["argumen_sistem"]
        elif "argumen_sistem" in saved_globals:
             module_globals["argumen_sistem"] = saved_globals["argumen_sistem"]

        self.globals = module_globals

        # Simpan running state sebelumnya
        previous_running = self.running
        self.running = True # Force running agar loop eksekusi berjalan

        try:
            # Jalankan code object modul sebagai script level atas
            # Kita gunakan call_function_sync tapi tanpa argumen
            # CodeObject modul biasanya diakhiri dengan RET nil.
            # Kita tidak butuh return value-nya (biasanya nil), tapi kita butuh state globals-nya.

            # Manual Frame Push and Run untuk kontrol penuh
            frame = Frame(code=code_obj, globals=module_globals)
            self.call_stack.append(frame)

            # Jalankan sampai frame ini selesai
            # Masalah: run() adalah loop utama. Jika kita panggil run() lagi, itu rekursif.
            # VM single threaded. Kita harus re-enter loop?
            # Jika load_module dipanggil dari dalam execute (nested), kita harus hati-hati.
            # execute -> load_module -> ...
            # Kita bisa gunakan call_function_internal, lalu biarkan loop execute utama melanjutkan.
            # TAPI, opcode IMPORT mengharapkan hasil SEGERA di stack.
            # Jadi kita harus eksekusi synchronous sampai selesai DI SINI.

            # Sub-loop eksekusi
            start_depth = len(self.call_stack)
            while len(self.call_stack) >= start_depth and self.running:
                if self.instruction_count >= self.max_instructions:
                    raise RuntimeError("Instruction limit exceeded")

                curr = self.current_frame
                if curr.pc >= len(curr.code.instructions):
                    self._return_from_frame(None)
                    continue

                instr = curr.code.instructions[curr.pc]
                curr.pc += 1

                try:
                    self.execute(instr)
                except Exception as e:
                    # Tangani error modul
                    err = {
                        "pesan": str(e), "jenis": "ErrorModul",
                        "file": file_path_str
                    }
                    self._handle_exception(err)

                self.instruction_count += 1

        finally:
            # 5. Restore & Return
            self.globals = saved_globals
            self.running = previous_running # Restore running state
            # Pulihkan exception handlers dari frame pemanggil
            if self.call_stack:
                self.current_frame.exception_handlers = saved_handlers

        # Wrap exported functions with closure
        for k, v in module_globals.items():
             if isinstance(v, CodeObject):
                 module_globals[k] = MorphFunction(v, module_globals)

        self.loaded_modules[file_path_str] = module_globals
        return module_globals

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
