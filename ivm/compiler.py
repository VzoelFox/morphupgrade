from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken
from ivm.core.opcodes import Op

class Compiler:
    def __init__(self):
        self.instructions = []
        # A simple mapping for variable names to register indices could be added here
        # for optimization, but for now we stick to Stack + Variables.

    def compile(self, node: ast.MRPH) -> list:
        self.instructions = []
        self.visit(node)
        self.emit(Op.HALT)
        return self.instructions

    def emit(self, opcode, *args):
        self.instructions.append((opcode, *args))
        return len(self.instructions) - 1

    def patch_jump(self, index, target):
        opcode = self.instructions[index][0]
        # Preserve other args if any, though JMPs usually just have target
        # But my JMP definition is (Op.JMP, target).
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

    # --- Statements ---
    def visit_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        self.visit(node.ekspresi)
        # In a stack machine, an expression statement usually pops the result
        # unless it's void. For now, let's pop to keep stack clean.
        self.emit(Op.POP)

    def visit_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        if node.nilai:
            self.visit(node.nilai)
        else:
            self.emit(Op.PUSH_CONST, None)

        self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_Assignment(self, node: ast.Assignment):
        # Support simple variable assignment for now
        if isinstance(node.target, ast.Identitas):
            self.visit(node.nilai)
            self.emit(Op.STORE_VAR, node.target.nama)
        else:
            raise NotImplementedError("Assignment kompleks belum didukung")

    def visit_Tulis(self, node: ast.Tulis):
        for arg in node.argumen:
            self.visit(arg)
        self.emit(Op.PRINT, len(node.argumen))

    # --- Expressions ---
    def visit_Konstanta(self, node: ast.Konstanta):
        self.emit(Op.PUSH_CONST, node.nilai)

    def visit_Identitas(self, node: ast.Identitas):
        self.emit(Op.LOAD_VAR, node.nama)

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

    # --- Jodohkan (Pattern Matching) ---
    def visit_Jodohkan(self, node: ast.Jodohkan):
        # Implementation Strategy:
        # 1. Evaluate Subject
        # 2. For each Case:
        #    a. Duplicate Subject (Stack: [Subject, Subject])
        #    b. Evaluate Pattern (Stack: [Subject, Subject, Pattern])
        #    c. Compare (EQ) (Stack: [Subject, Result])
        #    d. JMP_IF_FALSE to NextCase
        #    e. Execute Body
        #    f. JMP to End
        #    g. NextCase Label
        # 3. End Label (Pop Subject)

        self.visit(node.ekspresi) # Stack: [Subject]

        end_jumps = []

        for i, kasus in enumerate(node.kasus):
            # Case Start

            # Special handling for Wildcard (_)
            is_wildcard = isinstance(kasus.pola, ast.PolaWildcard)

            if not is_wildcard:
                self.emit(Op.DUP) # Stack: [Subject, Subject]

                # Compile Pattern
                if isinstance(kasus.pola, ast.PolaLiteral):
                    self.visit(kasus.pola.nilai) # Stack: [Subj, Subj, PatVal]
                    self.emit(Op.EQ)             # Stack: [Subj, Match?]
                else:
                    # Fallback for unsupported patterns for now
                    # To avoid crashing, we treat unknown patterns as "No Match"
                    self.emit(Op.POP)            # Stack: [Subj]
                    self.emit(Op.PUSH_CONST, False) # Stack: [Subj, False]

                jump_to_next = self.emit(Op.JMP_IF_FALSE, 0) # Placeholder

            # Execute Body
            # If match (or wildcard), we are here.
            # Note: Subject is still on stack below.
            # Ideally we might want to pop it if we don't need it,
            # but let's leave it for the final cleanup.

            # Wait, if we execute body, we skip others.
            # Before executing body, we should probably pop the subject from stack?
            # In many VMs, match consumes the subject?
            # If we pop here, we must ensure we don't pop it again at End.
            # Let's keep it simple: Standard VM keeps stack clean.
            # If we enter body, we are "done" with matching.

            self.emit(Op.POP) # Pop Subject (Success path)
            self.visit(kasus.badan)

            jump_to_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_to_end)

            # Patch the Jump to Next Case (Failure path)
            if not is_wildcard:
                next_case_idx = len(self.instructions)
                self.patch_jump(jump_to_next, next_case_idx)

        # End of all cases (No match found)
        # If we fall through here, stack still has [Subject].
        # We should pop it.
        self.emit(Op.POP)

        # Target for successful matches to jump to
        end_target = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_target)

