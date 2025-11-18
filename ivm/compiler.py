# ivm/compiler.py
from .opcodes import OpCode
from .structs import CodeObject
from . import hir

class Compiler(hir.HIRVisitor):
    def __init__(self, parent: 'Compiler' = None):
        self.parent = parent
        self.code_obj = CodeObject(name="<anonim>") # Akan diubah nanti

        # Setiap compiler memiliki symbol table-nya sendiri untuk locals
        self.symbol_table = {}
        self.local_count = 0

    def compile(self, hir_node: hir.HIRNode, name: str = "<utama>"):
        """
        Mengkompilasi node HIR menjadi CodeObject yang berisi bytecode.
        """
        self.code_obj.name = name
        self.visit(hir_node)

        # Pastikan setiap fungsi diakhiri dengan return (implisit None jika perlu)
        if not self.code_obj.instructions or self.code_obj.instructions[-1] != OpCode.RETURN_VALUE:
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(None))
            self._emit_byte(OpCode.RETURN_VALUE)

        self.code_obj.n_locals = self.local_count
        return self.code_obj

    # --- Metode Internal ---

    def _emit_byte(self, byte):
        """Menambahkan satu byte ke instruksi."""
        self.code_obj.instructions.append(byte)

    def _emit_short(self, short_val):
        """Menambahkan dua byte (short) ke instruksi."""
        self._emit_byte(short_val & 0xFF)
        self._emit_byte((short_val >> 8) & 0xFF)

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

        # Jika initializer adalah fungsi, kita perlu membungkus CodeObject-nya
        if isinstance(node.initializer, hir.Function):
            self._emit_byte(OpCode.BUILD_FUNCTION)

        # Simpan hasilnya ke variabel lokal
        index = self.local_count
        self.symbol_table[node.name] = index
        self.local_count += 1

        self._emit_byte(OpCode.STORE_FAST)
        self._emit_byte(index)

    def visit_StoreGlobal(self, node: hir.StoreGlobal):
        self.visit(node.value)

        if isinstance(node.value, hir.Function):
            self._emit_byte(OpCode.BUILD_FUNCTION)

        name_index = self._add_constant(node.name)
        self._emit_byte(OpCode.STORE_GLOBAL)
        self._emit_byte(name_index)

    def visit_Assignment(self, node: hir.Assignment):
        # Kompilasi nilai baru
        self.visit(node.value)

        # Simpan ke variabel yang sudah ada
        self._emit_byte(OpCode.STORE_FAST)
        self._emit_byte(node.target.index)

        # Dorong kembali nilai yang di-assign ke stack agar bisa digunakan
        # oleh ExpressionStatement (POP_TOP) atau assignment berantai.
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(node.target.index)

    def visit_Local(self, node: hir.Local):
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(node.index)

    def visit_Global(self, node: hir.Global):
        name_index = self._add_constant(node.name)
        self._emit_byte(OpCode.LOAD_GLOBAL)
        self._emit_byte(name_index)

    def visit_Function(self, node: hir.Function):
        # 1. Buat compiler baru untuk scope fungsi ini
        func_compiler = Compiler(parent=self)

        # 2. Daftarkan parameter sebagai local variable di compiler baru
        for param_name in node.parameters:
            func_compiler.symbol_table[param_name] = func_compiler.local_count
            func_compiler.local_count += 1

        # 3. Kompilasi body fungsi
        func_code_obj = func_compiler.compile(node.body, name=node.name)
        func_code_obj.parameters = node.parameters

        # 4. Simpan CodeObject yang sudah dikompilasi sebagai konstanta di parent
        const_index = self._add_constant(func_code_obj)
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(const_index)

    def visit_Return(self, node: hir.Return):
        if node.value:
            self.visit(node.value)
        else:
            # Jika tidak ada nilai return, return None
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(None))

        self._emit_byte(OpCode.RETURN_VALUE)

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
            '<': OpCode.LESS_THAN,
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

    def visit_ListLiteral(self, node: hir.ListLiteral):
        # Kompilasi setiap elemen dan dorong ke stack
        for element in node.elements:
            self.visit(element)

        # Bangun list dari elemen-elemen di stack
        self._emit_byte(OpCode.BUILD_LIST)
        self._emit_byte(len(node.elements))

    def visit_IndexAccess(self, node: hir.IndexAccess):
        # Dorong target (objek yang akan diindeks)
        self.visit(node.target)

        # Dorong kunci/indeks
        self.visit(node.index)

        # Lakukan operasi load
        self._emit_byte(OpCode.LOAD_INDEX)

    def visit_StoreIndex(self, node: hir.StoreIndex):
        # Urutan penting: target, indeks, lalu nilai.
        self.visit(node.target)
        self.visit(node.index)
        self.visit(node.value)

        # Lakukan operasi store
        self._emit_byte(OpCode.STORE_INDEX)

    def visit_While(self, node: hir.While):
        # 1. Tandai titik awal loop
        loop_start_pos = len(self.code_obj.instructions)

        # 2. Kompilasi kondisi
        self.visit(node.condition)

        # 3. Emit JUMP_IF_FALSE dengan placeholder
        self._emit_byte(OpCode.JUMP_IF_FALSE)
        exit_jump_pos = len(self.code_obj.instructions)
        self._emit_short(0xFFFF)  # Placeholder

        # 4. Kompilasi badan loop
        self.visit(node.body)

        # 5. Emit JUMP kembali ke awal loop
        self._emit_byte(OpCode.JUMP)
        self._emit_short(loop_start_pos)

        # 6. Lakukan backpatching untuk JUMP_IF_FALSE
        exit_pos = len(self.code_obj.instructions)
        self.code_obj.instructions[exit_jump_pos] = exit_pos & 0xFF
        self.code_obj.instructions[exit_jump_pos + 1] = (exit_pos >> 8) & 0xFF
