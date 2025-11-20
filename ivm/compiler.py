from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

class Compiler:
    # ... (Previous __init__ and other methods remain unchanged) ...
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

    # --- Pattern Matching (Updated) ---
    def visit_Jodohkan(self, node: ast.Jodohkan):
        self.visit(node.ekspresi) # Stack: [Subject]
        end_jumps = []

        for i, kasus in enumerate(node.kasus):
            is_wildcard = isinstance(kasus.pola, ast.PolaWildcard)
            is_binding = isinstance(kasus.pola, ast.PolaIkatanVariabel)

            if not (is_wildcard or is_binding):
                self.emit(Op.DUP) # Keep subject for check
                if isinstance(kasus.pola, ast.PolaLiteral):
                    self.visit(kasus.pola.nilai)
                    self.emit(Op.EQ)
                else:
                    self.emit(Op.POP)
                    self.emit(Op.PUSH_CONST, False) # Unsupported pattern fails

                jump_to_next = self.emit(Op.JMP_IF_FALSE, 0)
            elif is_binding:
                # Variable Binding: | x maka ...
                # We need to DUP because we might need the subject again if GUARD fails.
                self.emit(Op.DUP)
                # Bind to variable (local usually)
                name = kasus.pola.token.nilai
                if self.parent is not None:
                    self.locals.add(name)
                    self.emit(Op.STORE_LOCAL, name)
                else:
                    self.emit(Op.STORE_VAR, name)
                # No jump_to_next yet, because binding always succeeds.
                # But we check GUARD below.
                jump_to_next = None
            else:
                # Wildcard matches everything
                jump_to_next = None

            # --- Guard Clause (jaga) ---
            if kasus.jaga:
                self.visit(kasus.jaga) # Evaluate guard
                jump_to_next_guard = self.emit(Op.JMP_IF_FALSE, 0)
            else:
                jump_to_next_guard = None

            # Success Path (Execute Body)
            # If we arrived here, pattern matched AND guard (if any) passed.
            # If we did DUP (literal check or binding), the copy was consumed (by EQ or STORE).
            # But the ORIGINAL Subject is still on stack.
            # We need to POP it before executing body to keep stack clean?
            # NO, the subject must be popped ONLY ONCE at the very end or after body?
            # My previous logic was:
            #   DUP -> EQ -> JMP_FALSE
            #   POP -> Body -> JMP_END
            # So if match succeeds, we POP the subject.

            # If binding:
            #   DUP -> STORE
            #   (Subject still on stack)
            #   POP -> Body

            # If guard fails:
            #   DUP -> STORE
            #   Guard -> JMP_FALSE
            #   (Subject still on stack)
            #   POP -> Body

            # Issue: If guard fails, we jump to next case.
            # But if binding happened, we stored variable. That's side effect but acceptable?
            # Usually pattern match bindings are scoped to the case.
            # But here, if we jump to next, the stack must be clean (contain Subject).
            # If binding, we consumed the DUP. Stack has Subject. Correct.

            self.emit(Op.POP) # Pop Subject before body
            self.visit(kasus.badan)

            jump_to_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_to_end)

            # --- Patch Jumps for Failure ---
            next_case_idx = len(self.instructions)

            if jump_to_next_guard:
                self.patch_jump(jump_to_next_guard, next_case_idx)

            if jump_to_next:
                self.patch_jump(jump_to_next, next_case_idx)

        # End of all cases
        self.emit(Op.POP) # Pop Subject

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
