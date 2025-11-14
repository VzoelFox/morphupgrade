# transisi/ffi.py
# Foreign Function Interface (FFI) Engine untuk MORPH

import importlib
from .kesalahan import KesalahanImportFFI, KesalahanPanggilanFFI, KesalahanAtributFFI
from .pembungkus import PythonObject

class PythonModule:
    """Wrapper untuk Python module yang di-import."""
    def __init__(self, module_name: str, actual_module):
        self.name = module_name
        self.module = actual_module

    def get_attribute(self, attr_name: str):
        try:
            return getattr(self.module, attr_name)
        except AttributeError as e:
            # Lempar kembali exception agar translator bisa menangkapnya
            raise e

    def __repr__(self):
        return f"<python module '{self.name}'>"


class FFIBridge:
    """Main engine untuk FFI operations."""

    def __init__(self):
        self.loaded_modules = {}

    def import_module(self, module_path: str, token) -> PythonModule:
        if module_path in self.loaded_modules:
            return self.loaded_modules[module_path]
        try:
            actual_module = importlib.import_module(module_path)
            py_module = PythonModule(module_path, actual_module)
            self.loaded_modules[module_path] = py_module
            return py_module
        except ImportError as e:
            raise KesalahanImportFFI(
                token,
                f"Gagal mengimpor modul Python '{module_path}'",
                python_exception=e
            )

import datetime

class FFIBridge:
    """Main engine untuk FFI operations."""

    def __init__(self):
        self.loaded_modules = {}

    def import_module(self, module_path: str, token) -> PythonModule:
        if module_path in self.loaded_modules:
            return self.loaded_modules[module_path]
        try:
            actual_module = importlib.import_module(module_path)
            py_module = PythonModule(module_path, actual_module)
            self.loaded_modules[module_path] = py_module
            return py_module
        except ImportError as e:
            raise KesalahanImportFFI(
                token,
                f"Gagal mengimpor modul Python '{module_path}'",
                python_exception=e
            )

    def morph_to_python(self, value):
        if isinstance(value, PythonObject):
            return value.obj
        if value is None: return None
        if isinstance(value, (str, int, float, bool, datetime.datetime)):
            return value
        if isinstance(value, list):
            return [self.morph_to_python(item) for item in value]
        if isinstance(value, dict):
            return {self.morph_to_python(k): self.morph_to_python(v) for k, v in value.items()}

        raise TypeError(f"Tipe data MORPH '{type(value).__name__}' tidak dapat dikonversi ke Python.")

    def python_to_morph(self, value):
        if value is None: return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self.python_to_morph(item) for item in value]
        if isinstance(value, dict):
            return {self.python_to_morph(k): self.python_to_morph(v) for k, v in value.items()}

        return PythonObject(value)

    def safe_call(self, func, args: list, token):
        """Memanggil fungsi Python dan menangani exception."""
        try:
            return func(*args)
        except Exception as e:
            raise KesalahanPanggilanFFI(
                token,
                f"Terjadi error saat memanggil fungsi Python '{getattr(func, '__name__', 'unknown')}'.",
                python_exception=e
            )
