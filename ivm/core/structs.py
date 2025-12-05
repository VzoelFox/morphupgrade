from dataclasses import dataclass, field
from typing import List, Any, Dict, Tuple, Optional

@dataclass
class Cell:
    """Container for closure variables."""
    value: Any = None

    def __repr__(self):
        return f"<Cell {self.value}>"

@dataclass
class CodeObject:
    name: str
    instructions: List[Tuple]
    arg_names: List[str] = field(default_factory=list)
    filename: str = "<unknown>"
    is_generator: bool = False
    free_vars: Tuple[str, ...] = field(default_factory=tuple) # Names of variables captured from outer scopes
    cell_vars: Tuple[str, ...] = field(default_factory=tuple) # Names of local variables captured by inner scopes

    def __repr__(self):
        return f"<CodeObject {self.name}>"

@dataclass
class MorphFunction:
    """Wrapper for CodeObject that closes over the module's globals."""
    code: CodeObject
    globals: Dict[str, Any]
    closure: Optional[Tuple[Cell, ...]] = None # Tuple of Cells for free variables

    def __repr__(self):
        return f"<Fungsi {self.code.name}>"

@dataclass
class Frame:
    code: CodeObject
    globals: Dict[str, Any] # Globals context for this frame
    pc: int = 0
    locals: Dict[str, Any] = field(default_factory=dict)
    stack: List[Any] = field(default_factory=list) # Operand stack for this frame
    is_init_call: bool = False # Flag if this frame is a constructor call
    exception_handlers: List[int] = field(default_factory=list) # Stack of PC targets for try-catch blocks
    snapshots: List[int] = field(default_factory=list) # Stack snapshots (SP locations)
    defining_class: Optional['MorphClass'] = None # Class that defined the method running in this frame
    cells: Dict[str, Cell] = field(default_factory=dict) # Mapping of cell_var/free_var names to Cell objects

@dataclass
class MorphClass:
    name: str
    methods: Dict[str, CodeObject]
    superclass: Optional['MorphClass'] = None
    globals: Dict[str, Any] = field(default_factory=dict) # Capture module scope

    def __repr__(self):
        return f"<Kelas {self.name}>"

@dataclass
class MorphInstance:
    klass: MorphClass
    properties: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<Instance {self.klass.name}>"

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

@dataclass
class BoundMethod:
    instance: MorphInstance
    method: CodeObject
    defining_class: Optional[MorphClass] = None

    def __repr__(self):
        # self.method could be MorphFunction or CodeObject
        name = getattr(self.method, 'name', None)
        if not name and hasattr(self.method, 'code'):
             name = self.method.code.name
        return f"<BoundMethod {name} of {self.instance}>"

@dataclass
class SuperBoundMethod(BoundMethod):
    """Subclass to signal that this is a super() call."""
    pass

@dataclass
class MorphVariant:
    name: str
    args: List[Any] = field(default_factory=list)

    def __repr__(self):
        if not self.args:
            return f"{self.name}"
        args_str = ", ".join(map(str, self.args))
        return f"{self.name}({args_str})"

@dataclass
class MorphGenerator:
    frame: Frame
    status: str = "suspended" # suspended, running, closed
    daftar_checkpoint: List[Tuple[Frame, Dict[str, Any]]] = field(default_factory=list)

    def __repr__(self):
        return f"<Generator {self.frame.code.name}>"
