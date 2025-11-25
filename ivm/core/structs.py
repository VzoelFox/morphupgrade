from dataclasses import dataclass, field
from typing import List, Any, Dict, Tuple, Optional

@dataclass
class CodeObject:
    name: str
    instructions: List[Tuple]
    arg_names: List[str] = field(default_factory=list)
    filename: str = "<unknown>"

    def __repr__(self):
        return f"<CodeObject {self.name}>"

@dataclass
class MorphFunction:
    """Wrapper for CodeObject that closes over the module's globals."""
    code: CodeObject
    globals: Dict[str, Any]

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

@dataclass
class MorphClass:
    name: str
    methods: Dict[str, CodeObject]
    globals: Dict[str, Any] = field(default_factory=dict) # Capture module scope

    def __repr__(self):
        return f"<Kelas {self.name}>"

@dataclass
class MorphInstance:
    klass: MorphClass
    properties: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<Instance {self.klass.name}>"

@dataclass
class BoundMethod:
    instance: MorphInstance
    method: CodeObject

    def __repr__(self):
        return f"<BoundMethod {self.method.name} of {self.instance}>"

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

    def __repr__(self):
        return f"<Generator {self.frame.code.name}>"
