# ivm/hir.py
"""
Definisi untuk High-level Intermediate Representation (HIR).
HIR adalah representasi program yang lebih sederhana dan lebih eksplisit
daripada AST, dirancang untuk memudahkan analisis dan kompilasi ke bytecode.
"""
from dataclasses import dataclass
from typing import List, Any, Optional

# --- Node Dasar ---
class HIRNode:
    line: int = -1

    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__}'
        visitor_method = getattr(visitor, method_name, visitor.visit_generic)
        return visitor_method(self)

class Statement(HIRNode): pass
class Expression(HIRNode): pass

# --- Node Program Utama ---
@dataclass
class Program(HIRNode):
    body: List[Statement]

# --- Pernyataan (Statements) ---
@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class VarDeclaration(Statement):
    name: str
    initializer: Expression

@dataclass
class If(Statement):
    condition: Expression
    then_block: 'Program'
    else_block: Optional['Program'] = None

@dataclass
class StoreGlobal(Statement):
    name: str
    value: Expression

@dataclass
class Return(Statement):
    value: Optional[Expression]

@dataclass
class StoreIndex(Statement):
    target: Expression
    index: Expression
    value: Expression

@dataclass
class While(Statement):
    condition: Expression
    body: 'Program'

@dataclass
class Import(Statement):
    path: str
    alias: str

@dataclass
class Export(Statement):
    value: Expression

@dataclass
class ClassDeclaration(Statement):
    name: str
    superclass: Optional[Expression]
    methods: List['Function']

@dataclass
class SetProperty(Statement):
    target: Expression
    attribute: str
    value: Expression

# --- Ekspresi (Expressions) ---
@dataclass
class Constant(Expression):
    value: Any

@dataclass
class Global(Expression):
    name: str

@dataclass
class Local(Expression):
    name: str
    index: int

@dataclass
class Assignment(Expression): # Dijadikan Expression agar bisa `a = b = 5`
    target: 'Local' # Untuk saat ini hanya mendukung assignment ke variabel lokal
    value: Expression

@dataclass
class BinaryOperation(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class Call(Expression):
    target: Expression
    args: List[Expression]

@dataclass
class Function(Expression):
    name: str
    parameters: List[str]
    body: 'Program'

@dataclass
class ListLiteral(Expression):
    elements: List[Expression]

@dataclass
class IndexAccess(Expression):
    target: Expression
    index: Expression

@dataclass
class DictLiteral(Expression):
    pairs: List[tuple[Expression, Expression]]

@dataclass
class GetProperty(Expression):
    target: Expression
    attribute: str

@dataclass
class This(Expression):
    pass

@dataclass
class Super(Expression):
    method: str

# --- Visitor Pattern untuk HIR ---
class HIRVisitor:
    def visit(self, node: HIRNode):
        return node.accept(self)

    def visit_generic(self, node: HIRNode):
        raise NotImplementedError(f"Metode visit_{node.__class__.__name__} belum diimplementasikan")
