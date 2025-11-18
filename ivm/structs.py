# ivm/structs.py
from dataclasses import dataclass, field
from typing import List, Any, Optional

@dataclass
class CodeObject:
    """
    Sebuah wadah untuk bytecode dan data terkait yang diperlukan untuk eksekusi.
    """
    name: str
    instructions: bytearray = field(default_factory=bytearray)
    constants: List[Any] = field(default_factory=list)

    # Metadata untuk debugging dan manajemen variabel
    n_locals: int = 0
    parameters: List[str] = field(default_factory=list)

@dataclass
class MorphFunction:
    """
    Objek runtime yang merepresentasikan fungsi Morph yang telah dikompilasi.
    """
    name: str
    code_obj: CodeObject

@dataclass
class MorphClass:
    """
    Objek runtime yang merepresentasikan sebuah kelas.
    """
    name: str
    methods: dict = field(default_factory=dict)
    superclass: Optional['MorphClass'] = None

@dataclass
class MorphInstance:
    """
    Objek runtime yang merepresentasikan sebuah instance dari kelas.
    """
    klass: MorphClass
    properties: dict = field(default_factory=dict)

@dataclass
class BoundMethod:
    """
    Objek callable yang mengikat instance ('ini') ke sebuah fungsi metode.
    """
    receiver: MorphInstance
    method: MorphFunction

@dataclass
class Frame:
    """
    Mewakili satu frame dalam call stack, sesuai dengan satu pemanggilan fungsi.
    """
    code: CodeObject
    parent: Optional['Frame'] = None
    current_module: Optional['MorphModule'] = None
    is_module_init: bool = False

    ip: int = 0  # Instruction Pointer

    # Penyimpanan untuk frame ini
    locals: List[Any] = field(init=False)
    stack: List[Any] = field(default_factory=list)

    def __post_init__(self):
        # Inisialisasi array locals dengan ukuran yang benar
        self.locals = [None] * self.code.n_locals

    def push(self, value: Any):
        """Mendorong nilai ke operand stack."""
        self.stack.append(value)

    def pop(self) -> Any:
        """Mengambil nilai dari operand stack."""
        if not self.stack:
            raise RuntimeError("Stack underflow in frame")
        return self.stack.pop()

    def peek(self) -> Any:
        """Melihat nilai teratas di stack tanpa mengambilnya."""
        return self.stack[-1] if self.stack else None

    @property
    def function_name(self) -> str:
        return self.code.name
