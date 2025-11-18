# ivm/hir.py
"""
Definisi untuk High-level Intermediate Representation (HIR).
HIR adalah representasi program yang lebih sederhana dan lebih eksplisit
daripada AST, dirancang untuk memudahkan analisis dan kompilasi ke bytecode.
"""
from dataclasses import dataclass
from typing import List, Any

# --- Node Dasar ---
class HIRNode:
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

# --- Visitor Pattern untuk HIR ---
class HIRVisitor:
    def visit(self, node: HIRNode):
        return node.accept(self)

    def visit_generic(self, node: HIRNode):
        raise NotImplementedError(f"Metode visit_{node.__class__.__name__} belum diimplementasikan")
