from dataclasses import dataclass, field
from typing import List, Any, Dict, Tuple

@dataclass
class CodeObject:
    name: str
    instructions: List[Tuple]
    arg_names: List[str] = field(default_factory=list)

    def __repr__(self):
        return f"<CodeObject {self.name}>"

@dataclass
class Frame:
    code: CodeObject
    pc: int = 0
    locals: Dict[str, Any] = field(default_factory=dict)
    stack: List[Any] = field(default_factory=list) # Operand stack for this frame
