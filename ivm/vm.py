# ivm/vm.py
import sys
from typing import NewType

from .opcodes import OpCode
from .structs import (
    CodeObject, Frame, MorphFunction, MorphClass, MorphInstance, BoundMethod
)
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from .frontend import HIRConverter
from .compiler import Compiler

MorphModule = NewType("MorphModule", dict)

class VirtualMachine:
    def __init__(self):
        self.frames: list[Frame] = []
        self.globals: dict = {}
        self.builtins: dict = {
            "tulis": self._builtin_tulis
        }
        self.module_cache: dict = {}

    @property
    def frame(self) -> Frame | None:
        return self.frames[-1] if self.frames else None

    def push_frame(self, frame: Frame):
        self.frames.append(frame)

    def pop_frame(self):
        if not self.frames:
            raise RuntimeError("Tidak bisa pop dari call stack kosong")
        return self.frames.pop()

    def run(self, code_obj: CodeObject, current_module: MorphModule | None = None):
        """
        Mulai eksekusi dari sebuah code object.
        """
        main_frame = Frame(code_obj, current_module=current_module)
        self.push_frame(main_frame)

        while self.frame:
            # Periksa apakah IP masih dalam batas
            if self.frame.ip >= len(self.frame.code.instructions):
                # Akhir implisit dari sebuah frame (misalnya, akhir dari file skrip)
                frame_yang_selesai = self.pop_frame()
                if self.frame:
                    if frame_yang_selesai.is_module_init:
                        self.frame.push(frame_yang_selesai.current_module)
                    else:
                        # Return implisit 'nil' dari sebuah fungsi atau skrip
                        self.frame.push(None)
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

        elif opcode == OpCode.SUBTRACT:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri - kanan)

        elif opcode == OpCode.MULTIPLY:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri * kanan)

        elif opcode == OpCode.DIVIDE:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri / kanan)

        elif opcode == OpCode.MODULO:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri % kanan)

        elif opcode == OpCode.POWER:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri ** kanan)

        elif opcode == OpCode.EQUAL:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri == kanan)

        elif opcode == OpCode.NOT_EQUAL:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri != kanan)

        elif opcode == OpCode.GREATER_THAN:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri > kanan)

        elif opcode == OpCode.LESS_THAN:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri < kanan)

        elif opcode == OpCode.LESS_EQUAL:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri <= kanan)

        elif opcode == OpCode.GREATER_EQUAL:
            kanan = self.frame.pop()
            kiri = self.frame.pop()
            self.frame.push(kiri >= kanan)

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
            value = self.frame.pop()
            self.globals[name] = value
            # Jika kita berada dalam konteks eksekusi modul, ekspor juga globalnya
            if self.frame.current_module is not None:
                self.frame.current_module[name] = value

        elif opcode == OpCode.IMPORT_MODULE:
            path = self.frame.pop()

            if path in self.module_cache:
                self.frame.push(self.module_cache[path])
            else:
                # Kompilasi modul
                code_obj = self._compile_module(path)

                # Buat objek modul kosong dan cache
                module_obj = MorphModule({})
                self.module_cache[path] = module_obj

                # Dorong frame baru untuk inisialisasi modul
                new_frame = Frame(
                    code_obj,
                    parent=self.frame,
                    current_module=module_obj,
                    is_module_init=True
                )
                self.push_frame(new_frame)
                # Loop eksekusi utama akan menjalankan frame ini.
                # Ketika selesai, ia akan mendorong module_obj ke stack pemanggil.

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

                new_frame = Frame(callee.code_obj, parent=self.frame)

                for i, arg_name in enumerate(callee.code_obj.parameters):
                    new_frame.locals[i] = args[i]

                self.push_frame(new_frame)

            elif isinstance(callee, BoundMethod):
                if len(args) != len(callee.method.code_obj.parameters):
                     raise TypeError(
                        f"{callee.method.name} mengharapkan {len(callee.method.code_obj.parameters)} argumen, "
                        f"tetapi menerima {len(args)}"
                    )

                new_frame = Frame(callee.method.code_obj, parent=self.frame)
                # Masukkan 'ini' sebagai argumen implisit pertama
                new_frame.locals[0] = callee.receiver
                # Masukkan argumen lainnya
                for i, arg in enumerate(args):
                    new_frame.locals[i + 1] = arg

                self.push_frame(new_frame)

            elif isinstance(callee, MorphClass):
                # Ini adalah instansiasi kelas
                instance = MorphInstance(klass=callee)
                self.frame.push(instance)
                # Di masa depan, panggil konstruktor `inisiasi` di sini

            elif callable(callee): # Untuk built-in
                result = callee(args)
                self.frame.push(result)
            else:
                raise TypeError(f"Objek '{type(callee).__name__}' tidak dapat dipanggil")

        elif opcode == OpCode.RETURN_VALUE:
            return_value = self.frame.pop()
            frame_yang_selesai = self.pop_frame()

            if self.frame:
                if frame_yang_selesai.is_module_init:
                    # Modul mengembalikan objek modulnya, bukan nilai kembali.
                    self.frame.push(frame_yang_selesai.current_module)
                else:
                    # Perilaku return fungsi normal
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

        elif opcode == OpCode.BUILD_CLASS:
            methods = self.frame.pop()
            class_name = self.frame.pop()
            superclass = self.frame.pop()

            if superclass:
                # Warisi metode dari superclass
                all_methods = superclass.methods.copy()
                all_methods.update(methods)
            else:
                all_methods = methods

            klass = MorphClass(name=class_name, methods=all_methods, superclass=superclass)
            self.frame.push(klass)

        elif opcode == OpCode.LOAD_ATTR:
            attr_index = self.read_byte()
            attr_name = self.frame.code.constants[attr_index]
            target = self.frame.pop()
            if isinstance(target, MorphInstance):
                # Cari di properti instance terlebih dahulu
                if attr_name in target.properties:
                    self.frame.push(target.properties.get(attr_name))
                    return

                # Jika tidak ada, cari metode di rantai warisan
                current_class = target.klass
                while current_class:
                    if attr_name in current_class.methods:
                        method = current_class.methods[attr_name]
                        bound_method = BoundMethod(receiver=target, method=method)
                        self.frame.push(bound_method)
                        break
                    current_class = current_class.superclass
                else: # Jika loop selesai tanpa break
                    self.frame.push(None) # Atribut tidak ditemukan

            elif isinstance(target, dict): # Untuk modul
                self.frame.push(target.get(attr_name))
            else:
                raise TypeError(f"Objek tipe '{type(target).__name__}' tidak memiliki atribut.")

        elif opcode == OpCode.STORE_ATTR:
            attr_index = self.read_byte()
            attr_name = self.frame.code.constants[attr_index]
            target = self.frame.pop()
            value = self.frame.pop()
            if isinstance(target, MorphInstance):
                target.properties[attr_name] = value
            elif isinstance(target, dict): # Untuk modul
                target[attr_name] = value
            else:
                raise TypeError(f"Tidak dapat mengatur atribut pada objek tipe '{type(target).__name__}'.")

        elif opcode == OpCode.LOAD_SUPER_METHOD:
            method_index = self.read_byte()
            method_name = self.frame.code.constants[method_index]
            receiver = self.frame.pop()

            superclass = receiver.klass.superclass
            if not superclass:
                raise TypeError("induk dipanggil pada kelas yang tidak memiliki superkelas.")

            # Cari metode di rantai superkelas
            current_class = superclass
            while current_class:
                if method_name in current_class.methods:
                    method = current_class.methods[method_name]
                    bound_method = BoundMethod(receiver=receiver, method=method)
                    self.frame.push(bound_method)
                    break
                current_class = current_class.superclass
            else: # Jika loop selesai tanpa break
                raise AttributeError(f"Metode '{method_name}' tidak ditemukan di rantai superkelas.")

        else:
            raise NotImplementedError(f"Opcode {opcode.name} belum diimplementasikan")

    # --- Built-in Functions ---
    def _builtin_tulis(self, args: list):
        """Implementasi fungsi bawaan 'tulis'."""
        output = []
        for arg in args:
            if isinstance(arg, bool):
                output.append("benar" if arg else "salah")
            elif arg is None:
                output.append("nil")
            else:
                output.append(str(arg))
        print(" ".join(output), file=sys.stdout)
        return None

    def _compile_module(self, path: str) -> CodeObject:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                kode_sumber = f.read()
        except FileNotFoundError:
            raise ImportError(f"Modul tidak ditemukan: {path}")

        # Jalankan pipeline kompilasi untuk modul
        lexer = Leksikal(kode_sumber, path)
        tokens, _ = lexer.buat_token()
        parser = Pengurai(tokens)
        ast_tree = parser.urai()
        if not ast_tree:
            raise ImportError(f"Gagal mengurai modul: {path}")

        hir_converter = HIRConverter()
        hir_tree = hir_converter.convert(ast_tree)

        compiler = Compiler()
        return compiler.compile(hir_tree, name=f"<modul {path}>")
