# ivm/compiler.py
from .opcodes import OpCode
from .structs import CodeObject
from . import hir

class Compiler(hir.HIRVisitor):
    def __init__(self, parent: 'Compiler' = None):
        self.parent = parent
        self.code_obj = CodeObject(name="<anonim>")

        self.symbol_table = {}
        self.local_count = 0
        self.loop_contexts = []
        self.current_line = -1

    def compile(self, hir_node: hir.HIRNode, name: str = "<utama>"):
        self.code_obj.name = name
        self.visit(hir_node)
        if not self.code_obj.instructions or self.code_obj.instructions[-1] != OpCode.RETURN_VALUE:
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(None))
            self._emit_byte(OpCode.RETURN_VALUE)
        self.code_obj.n_locals = self.local_count
        return self.code_obj

    def visit(self, node: hir.HIRNode):
        self.current_line = node.line
        super().visit(node)

    def _emit_byte(self, byte):
        offset = len(self.code_obj.instructions)
        self.code_obj.line_map[offset] = self.current_line
        self.code_obj.instructions.append(byte)

    def _emit_short(self, short_val):
        self._emit_byte(short_val & 0xFF)
        self._emit_byte((short_val >> 8) & 0xFF)

    def _add_constant(self, value) -> int:
        if value not in self.code_obj.constants:
            self.code_obj.constants.append(value)
        return self.code_obj.constants.index(value)

    def visit_Program(self, node: hir.Program):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ExpressionStatement(self, node: hir.ExpressionStatement):
        self.visit(node.expression)
        self._emit_byte(OpCode.POP_TOP)

    def visit_Constant(self, node: hir.Constant):
        const_index = self._add_constant(node.value)
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(const_index)

    def visit_VarDeclaration(self, node: hir.VarDeclaration):
        self.visit(node.initializer)
        if isinstance(node.initializer, hir.Function):
            self._emit_byte(OpCode.BUILD_FUNCTION)
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
        self.visit(node.value)
        self._emit_byte(OpCode.STORE_FAST)
        self._emit_byte(node.target.index)
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(node.target.index)

    def visit_Local(self, node: hir.Local):
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(node.index)

    def visit_Global(self, node: hir.Global):
        name_index = self._add_constant(node.name)
        self._emit_byte(OpCode.LOAD_GLOBAL)
        self._emit_byte(name_index)

    def visit_Function(self, node: hir.Function, is_method: bool = False):
        func_compiler = Compiler(parent=self)
        if is_method:
            func_compiler.symbol_table['ini'] = func_compiler.local_count
            func_compiler.local_count += 1
        for param_name in node.parameters:
            func_compiler.symbol_table[param_name] = func_compiler.local_count
            func_compiler.local_count += 1
        func_code_obj = func_compiler.compile(node.body, name=node.name)
        func_code_obj.parameters = node.parameters
        const_index = self._add_constant(func_code_obj)
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(const_index)

    def visit_Return(self, node: hir.Return):
        if node.value:
            self.visit(node.value)
        else:
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(None))
        self._emit_byte(OpCode.RETURN_VALUE)

    def visit_If(self, node: hir.If):
        self.visit(node.condition)
        self._emit_byte(OpCode.JUMP_IF_FALSE)
        else_jump_pos = len(self.code_obj.instructions)
        self._emit_short(0xFFFF)
        self.visit(node.then_block)
        if node.else_block:
            self._emit_byte(OpCode.JUMP)
            end_jump_pos = len(self.code_obj.instructions)
            self._emit_short(0xFFFF)
            else_target = len(self.code_obj.instructions)
            self.code_obj.instructions[else_jump_pos] = else_target & 0xFF
            self.code_obj.instructions[else_jump_pos + 1] = (else_target >> 8) & 0xFF
            self.visit(node.else_block)
            end_target = len(self.code_obj.instructions)
            self.code_obj.instructions[end_jump_pos] = end_target & 0xFF
            self.code_obj.instructions[end_jump_pos + 1] = (end_target >> 8) & 0xFF
        else:
            end_target = len(self.code_obj.instructions)
            self.code_obj.instructions[else_jump_pos] = end_target & 0xFF
            self.code_obj.instructions[else_jump_pos + 1] = (end_target >> 8) & 0xFF

    def visit_BinaryOperation(self, node: hir.BinaryOperation):
        if node.op == 'dan':
            self.visit(node.left)
            self._emit_byte(OpCode.JUMP_IF_FALSE)
            end_jump_pos = len(self.code_obj.instructions)
            self._emit_short(0xFFFF) # Placeholder
            self.visit(node.right)
            end_target = len(self.code_obj.instructions)
            self.code_obj.instructions[end_jump_pos] = end_target & 0xFF
            self.code_obj.instructions[end_jump_pos + 1] = (end_target >> 8) & 0xFF
            return
        elif node.op == 'atau':
            self.visit(node.left)
            self._emit_byte(OpCode.JUMP_IF_TRUE)
            end_jump_pos = len(self.code_obj.instructions)
            self._emit_short(0xFFFF) # Placeholder
            self.visit(node.right)
            end_target = len(self.code_obj.instructions)
            self.code_obj.instructions[end_jump_pos] = end_target & 0xFF
            self.code_obj.instructions[end_jump_pos + 1] = (end_target >> 8) & 0xFF
            return

        self.visit(node.left)
        self.visit(node.right)
        op_map = {'+': OpCode.ADD, '-': OpCode.SUBTRACT, '*': OpCode.MULTIPLY, '/': OpCode.DIVIDE, '%': OpCode.MODULO, '^': OpCode.POWER, '==': OpCode.EQUAL, '!=': OpCode.NOT_EQUAL, '<': OpCode.LESS_THAN, '<=': OpCode.LESS_EQUAL, '>': OpCode.GREATER_THAN, '>=': OpCode.GREATER_EQUAL}
        opcode = op_map.get(node.op)
        if opcode:
            self._emit_byte(opcode)
        else:
            raise NotImplementedError(f"Operator uner '{node.op}' belum didukung.")

    def visit_Call(self, node: hir.Call):
        self.visit(node.target)
        for arg in node.args:
            self.visit(arg)
        self._emit_byte(OpCode.CALL_FUNCTION)
        self._emit_byte(len(node.args))

    def visit_ListLiteral(self, node: hir.ListLiteral):
        for element in node.elements:
            self.visit(element)
        self._emit_byte(OpCode.BUILD_LIST)
        self._emit_byte(len(node.elements))

    def visit_IndexAccess(self, node: hir.IndexAccess):
        self.visit(node.target)
        self.visit(node.index)
        self._emit_byte(OpCode.LOAD_INDEX)

    def visit_StoreIndex(self, node: hir.StoreIndex):
        self.visit(node.target)
        self.visit(node.index)
        self.visit(node.value)
        self._emit_byte(OpCode.STORE_INDEX)

    def visit_While(self, node: hir.While):
        loop_start_pos = len(self.code_obj.instructions)
        self.visit(node.condition)
        self._emit_byte(OpCode.JUMP_IF_FALSE)
        exit_jump_pos = len(self.code_obj.instructions)
        self._emit_short(0xFFFF)
        self.visit(node.body)
        self._emit_byte(OpCode.JUMP)
        self._emit_short(loop_start_pos)
        exit_pos = len(self.code_obj.instructions)
        self.code_obj.instructions[exit_jump_pos] = exit_pos & 0xFF
        self.code_obj.instructions[exit_jump_pos + 1] = (exit_pos >> 8) & 0xFF

        for break_pos in break_jumps:
            self.code_obj.instructions[break_pos] = exit_pos & 0xFF
            self.code_obj.instructions[break_pos + 1] = (exit_pos >> 8) & 0xFF

        self.loop_contexts.pop()

    def visit_Break(self, node: hir.Break):
        if not self.loop_contexts:
            raise SyntaxError("'berhenti' di luar loop tidak diizinkan.")

        self._emit_byte(OpCode.JUMP)
        placeholder_pos = len(self.code_obj.instructions)
        self._emit_short(0xFFFF)
        self.loop_contexts[-1]['breaks'].append(placeholder_pos)

    def visit_Continue(self, node: hir.Continue):
        if not self.loop_contexts:
            raise SyntaxError("'lanjutkan' di luar loop tidak diizinkan.")

        self._emit_byte(OpCode.JUMP)
        self._emit_short(self.loop_contexts[-1]['start'])

    def visit_Switch(self, node: hir.Switch):
        self.visit(node.expression)

        case_jumps = []
        end_jumps = []

        for case in node.cases:
            self._emit_byte(OpCode.DUP_TOP)
            self.visit(case.value)
            self._emit_byte(OpCode.EQUAL)
            self._emit_byte(OpCode.JUMP_IF_TRUE)
            jump_pos = len(self.code_obj.instructions)
            self._emit_short(0xFFFF)
            case_jumps.append(jump_pos)

        # Jika tidak ada kasus yang cocok, lompat ke default atau akhir
        if node.default:
            self.visit(node.default)
        self._emit_byte(OpCode.JUMP)
        end_jumps.append(len(self.code_obj.instructions))
        self._emit_short(0xFFFF)


        for i, case in enumerate(node.cases):
            jump_pos = case_jumps[i]
            target = len(self.code_obj.instructions)
            self.code_obj.instructions[jump_pos] = target & 0xFF
            self.code_obj.instructions[jump_pos + 1] = (target >> 8) & 0xFF
            self.visit(case.body)
            self._emit_byte(OpCode.JUMP)
            end_jumps.append(len(self.code_obj.instructions))
            self._emit_short(0xFFFF)

        end_target = len(self.code_obj.instructions)
        for jump_pos in end_jumps:
            self.code_obj.instructions[jump_pos] = end_target & 0xFF
            self.code_obj.instructions[jump_pos + 1] = (end_target >> 8) & 0xFF

        # Pop nilai ekspresi awal dari stack
        self._emit_byte(OpCode.POP_TOP)


    def visit_DictLiteral(self, node: hir.DictLiteral):
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
        self._emit_byte(OpCode.BUILD_DICT)
        self._emit_byte(len(node.pairs))

    def visit_Import(self, node: hir.Import):
        path_index = self._add_constant(node.path)
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(path_index)
        self._emit_byte(OpCode.IMPORT_MODULE)
        alias_index = self._add_constant(node.alias)
        self._emit_byte(OpCode.STORE_GLOBAL)
        self._emit_byte(alias_index)

    def visit_ClassDeclaration(self, node: hir.ClassDeclaration):
        name_index = self._add_constant(node.name)
        if node.superclass:
            self.visit(node.superclass)
        else:
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(None))
        self._emit_byte(OpCode.LOAD_CONST)
        self._emit_byte(name_index)
        for method in node.methods:
            self._emit_byte(OpCode.LOAD_CONST)
            self._emit_byte(self._add_constant(method.name))
            self.visit_Function(method, is_method=True)
            self._emit_byte(OpCode.BUILD_FUNCTION)
        self._emit_byte(OpCode.BUILD_DICT)
        self._emit_byte(len(node.methods))
        self._emit_byte(OpCode.BUILD_CLASS)
        self._emit_byte(OpCode.STORE_GLOBAL)
        self._emit_byte(name_index)

    def visit_This(self, node: hir.This):
        if 'ini' not in self.symbol_table:
            raise NameError("Kata kunci 'ini' hanya bisa digunakan di dalam metode kelas.")
        index = self.symbol_table['ini']
        self._emit_byte(OpCode.LOAD_FAST)
        self._emit_byte(index)

    def visit_GetProperty(self, node: hir.GetProperty):
        self.visit(node.target)
        attr_index = self._add_constant(node.attribute)
        self._emit_byte(OpCode.LOAD_ATTR)
        self._emit_byte(attr_index)

    def visit_SetProperty(self, node: hir.SetProperty):
        self.visit(node.value)
        self.visit(node.target)
        attr_index = self._add_constant(node.attribute)
        self._emit_byte(OpCode.STORE_ATTR)
        self._emit_byte(attr_index)

    def visit_Super(self, node: hir.Super):
        if 'ini' not in self.symbol_table:
            raise NameError("Kata kunci 'induk' hanya bisa digunakan di dalam metode kelas.")
        self.visit_This(hir.This())
        method_index = self._add_constant(node.method)
        self._emit_byte(OpCode.LOAD_SUPER_METHOD)
        self._emit_byte(method_index)
