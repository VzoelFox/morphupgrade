from typing import Any, Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class ObjekError:
    """Struktur standar untuk error di Morph."""
    pesan: str
    baris: int
    kolom: int
    jenis: str = "ErrorRuntime"
    file: str = ""

class Result(Generic[T, E]):
    """
    Representasi hasil operasi yang bisa Sukses atau Gagal.
    Menggantikan pola dictionary ad-hoc {'sukses': bool, ...}
    """
    def __init__(self, is_success: bool, value: Any):
        self._is_success = is_success
        self._value = value

    @staticmethod
    def sukses(value: T) -> 'Result[T, Any]':
        return Sukses(value)

    @staticmethod
    def gagal(error: E) -> 'Result[Any, E]':
        return Gagal(error)

    def is_sukses(self) -> bool:
        return self._is_success

    def is_gagal(self) -> bool:
        return not self._is_success

    def unwrap(self) -> T:
        if self.is_sukses():
            return self._value
        raise Exception(f"Panic: Mencoba unwrap Gagal: {self._value}")

    def unwrap_error(self) -> E:
        if self.is_gagal():
            return self._value
        raise Exception(f"Panic: Mencoba unwrap_error Sukses: {self._value}")

    def __getitem__(self, key):
        """
        Kompatibilitas Backward: Memungkinkan akses seperti dictionary.
        res['sukses'] -> bool
        res['data'] -> value (jika sukses) atau None
        res['error'] -> value (jika gagal) atau None
        """
        if key == 'sukses':
            return self._is_success
        elif key == 'data':
            return self._value if self._is_success else None
        elif key == 'error':
            return self._value if not self._is_success else None
        else:
            raise KeyError(f"Key '{key}' tidak valid untuk Result. Gunakan 'sukses', 'data', atau 'error'.")

    def get(self, key, default=None):
        """
        Kompatibilitas Backward: Metode .get() seperti dictionary.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        """
        Kompatibilitas Backward: Operator 'in' (e.g., 'sukses' in res).
        """
        return key in ['sukses', 'data', 'error']

    def keys(self):
         return ['sukses', 'data', 'error']

class Sukses(Result[T, Any]):
    def __init__(self, value: T):
        super().__init__(True, value)
        self.data = value # Alias untuk kompatibilitas atau kemudahan akses

    def __repr__(self):
        return f"Sukses({self._value})"

class Gagal(Result[Any, E]):
    def __init__(self, error: E):
        super().__init__(False, error)
        self.error = error # Alias

    def __repr__(self):
        return f"Gagal({self._value})"
