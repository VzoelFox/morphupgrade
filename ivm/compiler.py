# ivm/compiler.py
from .opcodes import OpCode
from .structs import CodeObject
from . import hir

class Compiler(hir.HIRVisitor):
    def __init__(self):
        self.code_obj = CodeObject(name="<utama>")
        self.symbol_table = {}
        self.local_count = 0

    def compile(self, hir_program: hir.Program):
        """
        Mengkompilasi program dari HIR menjadi CodeObject yang berisi bytecode.
        """
        self.visit(hir_program)
        self.code_obj.n_locals = self.local_count
        return self.code_obj

    # --- Metode Internal ---

    def _emit_byte(self, byte):
        """Menambahkan satu byte ke instruksi."""
        self.code_obj.instructions.append(byte)

    def _add_constant(self, value) -> int:
        """Menambahkan konstanta ke pool dan mengembalikan indeksnya."""
        if value not in self.code_obj.constants:
            self.code_obj.constants.append(value)
        return self.code_obj.constants.index(value)

    # --- Implementasi Visitor HIR ---

    def visit_Program(self, node: hir.Program):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ExpressionStatement(self, node: hir.ExpressionStatement):
        self.visit(node.expression)
        # Setiap hasil ekspresi yang tidak digunakan harus di-pop dari stack
        self._emit_byte(OpCode.POP_TOP)

    def visit_Constant(self, node: hir.Constant):
        const_index = self._add_constant(node.value)
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(const_index)

    def visit_VarDeclaration(self, node: hir.VarDeclaration):
        # Kompilasi nilai initializer
        self.visit(node.initializer)

        # Simpan hasilnya ke variabel lokal
        index = self.local_count
        self.symbol_table[node.name] = index
        self.local_count += 1

        self._emit_byte(OpCode.STORE_FAST)
        self._emit_byte(index)

    def visit_Assignment(self, node: hir.Assignment):
        # Kompilasi nilai baru
        self.visit(node.value)

        # Simpan ke variabel yang sudah ada
        self._emit_byte(OpCode.STORE_FAST)
        self._emit_byte(node.target.index)

        # Untuk assignment sebagai expression, kita perlu mendorong nilainya kembali
        # Untuk saat ini, kita asumsikan assignment adalah statement
        # dan tidak meninggalkan apa pun di stack.
        # Jika `a = b = 5` didukung, kita akan mendorong nilainya di sini.

    def visit_Local(self, node: hir.Local):
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(node.index)

    def visit_Global(self, node: hir.Global):
        name_index = self._add_constant(node.name)
        self._emit_byte(OpCode.LOAD_GLOBAL)
        self._emit_byte(name_index)

    def visit_If(self, node: hir.If):
        # 1. Kompilasi kondisi
        self.visit(node.condition)

        # 2. Emit JUMP_IF_FALSE dengan placeholder
        self._emit_byte(OpCode.JUMP_IF_FALSE)
        placeholder_pos = len(self.code_obj.instructions)
        self._emit_byte(0xFF) # Placeholder low byte
        self._emit_byte(0xFF) # Placeholder high byte

        # 3. Kompilasi blok 'then'
        self.visit(node.then_block)

        # 4. Hitung alamat tujuan dan lakukan backpatching
        jump_target = len(self.code_obj.instructions)
        self.code_obj.instructions[placeholder_pos] = jump_target & 0xFF
        self.code_obj.instructions[placeholder_pos + 1] = (jump_target >> 8) & 0xFF

    def visit_BinaryOperation(self, node: hir.BinaryOperation):
        self.visit(node.left)
        self.visit(node.right)

        op_map = {
            '+': OpCode.ADD,
            '>': OpCode.GREATER_THAN,
        }
        opcode = op_map.get(node.op)
        if opcode:
            self._emit_byte(opcode)
        else:
            raise NotImplementedError(f"Operator biner '{node.op}' belum didukung.")

    def visit_Call(self, node: hir.Call):
        # Dorong target fungsi ke stack terlebih dahulu
        self.visit(node.target)

        # Kemudian, dorong semua argumen ke stack
        for arg in node.args:
            self.visit(arg)

        # Panggil fungsi
        self._emit_byte(OpCode.CALL_FUNCTION)
        self._emit_byte(len(node.args))
