from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

class Compiler:
    def __init__(self, parent=None):
        self.instructions = []
        self.loop_contexts = [] # Stack to track loop contexts for break/continue
        self.parent = parent
        # Symbol table for tracking local vs global variables
        # Map: name -> scope_type ('global' or 'local')
        # This is a simple implementation. A full compiler would track indices.
        self.locals = set()

    def compile(self, node: ast.MRPH) -> CodeObject:
        # Reset for new compilation
        self.instructions = []
        self.visit(node)

        # Implicit return for safety
        self.emit(Op.PUSH_CONST, None)
        self.emit(Op.RET)

        return CodeObject(name="<module>", instructions=self.instructions)

    def emit(self, opcode, *args):
        self.instructions.append((opcode, *args))
        return len(self.instructions) - 1

    def patch_jump(self, index, target):
        opcode = self.instructions[index][0]
        self.instructions[index] = (opcode, target)

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Compiler belum mendukung node: {node.__class__.__name__}")

    # --- Program Structure ---
    def visit_Bagian(self, node: ast.Bagian):
        for stmt in node.daftar_pernyataan:
            self.visit(stmt)

    # --- Functions ---
    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        # Create a child compiler for the function body
        func_compiler = Compiler(parent=self)

        # Register parameters as locals
        arg_names = [param.nilai for param in node.parameter]
        for arg in arg_names:
            func_compiler.locals.add(arg)

        # Compile body
        # Note: visit(body) will populate func_compiler.instructions
        func_compiler.visit(node.badan)

        # Ensure explicit return at end of function
        if not func_compiler.instructions or func_compiler.instructions[-1][0] != Op.RET:
            func_compiler.emit(Op.PUSH_CONST, None)
            func_compiler.emit(Op.RET)

        code_obj = CodeObject(
            name=node.nama.nilai,
            instructions=func_compiler.instructions,
            arg_names=arg_names
        )

        # In the current scope, push the code object and store it
        self.emit(Op.PUSH_CONST, code_obj)
        self.emit(Op.STORE_VAR, node.nama.nilai) # Function is stored as a variable

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi):
        # 1. Push function object
        self.visit(node.callee)

        # 2. Push arguments
        for arg in node.argumen:
            self.visit(arg)

        # 3. Emit CALL
        self.emit(Op.CALL, len(node.argumen))

    def visit_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        if node.nilai:
            self.visit(node.nilai)
        else:
            self.emit(Op.PUSH_CONST, None)
        self.emit(Op.RET)

    # --- Statements ---
    def visit_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        self.visit(node.ekspresi)
        # If expression leaves a value, pop it (unless it's void)
        # Ideally we'd know if an expression is void, but for now we assume values.
        self.emit(Op.POP)

    def visit_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        if node.nilai:
            self.visit(node.nilai)
        else:
            self.emit(Op.PUSH_CONST, None)

        name = node.nama.nilai

        # Simple scope resolution:
        # If we are inside a function (parent is not None), declare as local
        if self.parent is not None:
            self.locals.add(name)
            self.emit(Op.STORE_LOCAL, name)
        else:
            self.emit(Op.STORE_VAR, name)

    def visit_Assignment(self, node: ast.Assignment):
        self.visit(node.nilai) # Evaluate value first

        if isinstance(node.target, ast.Identitas):
            name = node.target.nama
            if name in self.locals:
                self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)
        elif isinstance(node.target, ast.Akses):
            self.visit(node.target.objek) # Target object (List/Dict)
            self.visit(node.target.kunci) # Index/Key
            # Stack: [Value, Target, Index] -> STORE_INDEX pops Value, Index, Target
            # Wait, my Opcode STORE_INDEX logic is: val = pop(), index = pop(), target = pop()
            # Stack should be: [Target, Index, Value] before calling STORE_INDEX.
            # But I visited Value first. Stack: [Value]. Then Target. Stack: [Value, Target]. Then Index. Stack: [Value, Target, Index].
            # So:
            #   val = pop() -> Index
            #   index = pop() -> Target
            #   target = pop() -> Value
            # THIS IS WRONG.
            # Correct order for STORE_INDEX (Value, Index, Target on stack? Or Target, Index, Value?)
            # StandardVM: val=pop, idx=pop, target=pop. So stack top must be Value, then Index, then Target.
            # Stack build order: Push Target, Push Index, Push Value.

            # Let's restart logic for Assignment to Access:
            # 1. Push Target
            # 2. Push Index
            # 3. Push Value (Already visited above!)

            # Current state: Value is on stack.
            # I need Target and Index BELOW Value.
            # This requires stack manipulation (ROT_3) or different visit order.
            # Easier: Visit Target and Index BEFORE Value.

            # Retrying Assignment logic...
            pass # Handled in the corrected block below

        else:
            raise NotImplementedError("Assignment kompleks belum didukung")

    def visit_Tulis(self, node: ast.Tulis):
        for arg in node.argumen:
            self.visit(arg)
        self.emit(Op.PRINT, len(node.argumen))

    def visit_JikaMaka(self, node: ast.JikaMaka):
        end_jumps = []
        self.visit(node.kondisi)
        jump_to_next = self.emit(Op.JMP_IF_FALSE, 0)

        self.visit(node.blok_maka)
        jump_to_end = self.emit(Op.JMP, 0)
        end_jumps.append(jump_to_end)

        next_target = len(self.instructions)
        self.patch_jump(jump_to_next, next_target)

        if node.rantai_lain_jika:
            for kond_lain, blok_lain in node.rantai_lain_jika:
                self.visit(kond_lain)
                jump_to_next_elif = self.emit(Op.JMP_IF_FALSE, 0)

                self.visit(blok_lain)
                jump_to_end_elif = self.emit(Op.JMP, 0)
                end_jumps.append(jump_to_end_elif)

                next_elif_target = len(self.instructions)
                self.patch_jump(jump_to_next_elif, next_elif_target)

        if node.blok_lain:
            self.visit(node.blok_lain)

        end_pos = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_pos)

    def visit_Selama(self, node: ast.Selama):
        loop_start = len(self.instructions)
        current_loop_ctx = {'breaks': [], 'start': loop_start}
        self.loop_contexts.append(current_loop_ctx)

        self.visit(node.kondisi)
        jump_to_end = self.emit(Op.JMP_IF_FALSE, 0)

        self.visit(node.badan)
        self.emit(Op.JMP, loop_start)

        loop_end = len(self.instructions)
        self.patch_jump(jump_to_end, loop_end)

        for break_idx in current_loop_ctx['breaks']:
            self.patch_jump(break_idx, loop_end)

        self.loop_contexts.pop()

    def visit_Berhenti(self, node: ast.Berhenti):
        if not self.loop_contexts:
            raise SyntaxError("'berhenti' di luar loop")
        jmp = self.emit(Op.JMP, 0)
        self.loop_contexts[-1]['breaks'].append(jmp)

    def visit_Lanjutkan(self, node: ast.Lanjutkan):
        if not self.loop_contexts:
            raise SyntaxError("'lanjutkan' di luar loop")
        loop_start = self.loop_contexts[-1]['start']
        self.emit(Op.JMP, loop_start)

    # --- Expressions ---
    def visit_Konstanta(self, node: ast.Konstanta):
        self.emit(Op.PUSH_CONST, node.nilai)

    def visit_Identitas(self, node: ast.Identitas):
        name = node.nama
        if name in self.locals:
            self.emit(Op.LOAD_LOCAL, name)
        else:
            self.emit(Op.LOAD_VAR, name)

    def visit_FoxBinary(self, node: ast.FoxBinary):
        self.visit(node.kiri)
        self.visit(node.kanan)

        op_type = node.op.tipe
        if op_type == TipeToken.TAMBAH:
            self.emit(Op.ADD)
        elif op_type == TipeToken.KURANG:
            self.emit(Op.SUB)
        elif op_type == TipeToken.KALI:
            self.emit(Op.MUL)
        elif op_type == TipeToken.BAGI:
            self.emit(Op.DIV)
        elif op_type == TipeToken.MODULO:
            self.emit(Op.MOD)
        elif op_type == TipeToken.SAMA_DENGAN:
            self.emit(Op.EQ)
        elif op_type == TipeToken.TIDAK_SAMA:
            self.emit(Op.NEQ)
        elif op_type == TipeToken.LEBIH_DARI:
            self.emit(Op.GT)
        elif op_type == TipeToken.KURANG_DARI:
            self.emit(Op.LT)
        else:
            raise NotImplementedError(f"Operator {node.op.nilai} belum didukung")

    def visit_Jodohkan(self, node: ast.Jodohkan):
        self.visit(node.ekspresi)
        end_jumps = []

        for i, kasus in enumerate(node.kasus):
            is_wildcard = isinstance(kasus.pola, ast.PolaWildcard)

            if not is_wildcard:
                self.emit(Op.DUP)
                if isinstance(kasus.pola, ast.PolaLiteral):
                    self.visit(kasus.pola.nilai)
                    self.emit(Op.EQ)
                else:
                    self.emit(Op.POP)
                    self.emit(Op.PUSH_CONST, False)

                jump_to_next = self.emit(Op.JMP_IF_FALSE, 0)

            self.emit(Op.POP)
            self.visit(kasus.badan)

            jump_to_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_to_end)

            if not is_wildcard:
                next_case_idx = len(self.instructions)
                self.patch_jump(jump_to_next, next_case_idx)

        self.emit(Op.POP)

        end_target = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_target)

    # --- Data Structures ---
    def visit_Daftar(self, node: ast.Daftar):
        for elem in node.elemen:
            self.visit(elem)
        self.emit(Op.BUILD_LIST, len(node.elemen))

    def visit_Kamus(self, node: ast.Kamus):
        for key, val in node.pasangan:
            self.visit(key)
            self.visit(val)
        self.emit(Op.BUILD_DICT, len(node.pasangan))

    def visit_Akses(self, node: ast.Akses):
        self.visit(node.objek)
        self.visit(node.kunci)
        self.emit(Op.LOAD_INDEX)

    # Fixing Assignment for Access
    def visit_Assignment(self, node: ast.Assignment):
        if isinstance(node.target, ast.Identitas):
            # Standard variable assignment
            self.visit(node.nilai)
            name = node.target.nama
            if name in self.locals:
                self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)

        elif isinstance(node.target, ast.Akses):
            # Index assignment: target[index] = value
            # VM expects Stack: [Target, Index, Value] (Top) -> STORE_INDEX
            self.visit(node.target.objek) # Target
            self.visit(node.target.kunci) # Index
            self.visit(node.nilai)        # Value
            self.emit(Op.STORE_INDEX)

        else:
            raise NotImplementedError("Assignment kompleks belum didukung")
