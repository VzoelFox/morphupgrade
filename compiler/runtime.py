# compiler/runtime.py
from llvmlite import ir

class RuntimeManager:
    def __init__(self, module):
        self.module = module
        self.format_strings = {}
        self._declare_printf()

    def _declare_printf(self):
        """
        Mendeklarasikan fungsi C 'printf' di dalam modul LLVM.
        Signature: int printf(char* format, ...)
        """
        printf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.printf = ir.Function(self.module, printf_type, "printf")

    def get_printf_format(self, arg_type):
        """
        Membuat atau mendapatkan format string global untuk tipe data tertentu.
        Contoh: untuk integer, formatnya adalah "%d\n".
        """
        if arg_type == ir.IntType(32):
            format_str = "%d\n\0"
            format_name = "format_int"
        elif arg_type == ir.DoubleType():
            format_str = "%f\n\0"
            format_name = "format_float"
        else:
            # Default atau error, untuk sekarang kita fokus pada integer
            # Tambahkan tipe lain seiring pengembangan
            raise NotImplementedError(f"Tipe data {arg_type} belum didukung untuk pencetakan.")

        if format_name in self.format_strings:
            return self.format_strings[format_name]

        # Buat format string sebagai konstanta global di modul LLVM
        c_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode("utf8")))
        global_var = ir.GlobalVariable(self.module, c_str.type, name=format_name)
        global_var.linkage = 'internal'
        global_var.global_constant = True
        global_var.initializer = c_str

        # Dapatkan pointer ke elemen pertama dari array string
        ptr = global_var.gep([ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
        self.format_strings[format_name] = ptr
        return ptr
