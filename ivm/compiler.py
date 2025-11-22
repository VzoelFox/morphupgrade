from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

class Compiler:
    def __init__(self, parent=None):
        self.instructions = []
        self.loop_contexts = []
        self.parent = parent
        self.locals = set()

    def compile(self, node: ast.MRPH) -> CodeObject:
        self.instructions = []
        self.visit(node)
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

    # --- Classes ---
    def visit_Kelas(self, node: ast.Kelas):
        for method_node in node.metode:
            self.emit(Op.PUSH_CONST, method_node.nama.nilai)
            self.visit_FungsiDeklarasi(method_node, is_method=True)

        self.emit(Op.PUSH_CONST, node.nama.nilai)
        self.emit(Op.BUILD_DICT, len(node.metode))
        self.emit(Op.BUILD_CLASS)
        self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_Ini(self, node: ast.Ini):
        self.emit(Op.LOAD_LOCAL, "ini")

    def visit_AmbilProperti(self, node: ast.AmbilProperti):
        self.visit(node.objek)
        self.emit(Op.LOAD_ATTR, node.nama.nilai)

    def visit_AturProperti(self, node: ast.AturProperti):
        self.visit(node.objek)
        self.visit(node.nilai)
        self.emit(Op.STORE_ATTR, node.nama.nilai)

    # --- Functions ---
    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi, is_method: bool = False):
        func_compiler = Compiler(parent=self)
        arg_names = [param.nilai for param in node.parameter]

        if is_method:
            arg_names.insert(0, "ini")

        for arg in arg_names:
            func_compiler.locals.add(arg)

        func_compiler.visit(node.badan)

        if not func_compiler.instructions or func_compiler.instructions[-1][0] != Op.RET:
            func_compiler.emit(Op.PUSH_CONST, None)
            func_compiler.emit(Op.RET)

        code_obj = CodeObject(
            name=node.nama.nilai,
            instructions=func_compiler.instructions,
            arg_names=arg_names
        )

        self.emit(Op.PUSH_CONST, code_obj)
        if not is_method:
            self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi):
        self.visit(node.callee)
        for arg in node.argumen:
            self.visit(arg)
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
        self.emit(Op.POP)

    def visit_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        if node.nilai:
            self.visit(node.nilai)
        else:
            self.emit(Op.PUSH_CONST, None)

        name = node.nama.nilai
        if self.parent is not None:
            self.locals.add(name)
            self.emit(Op.STORE_LOCAL, name)
        else:
            self.emit(Op.STORE_VAR, name)

    def visit_Assignment(self, node: ast.Assignment):
        if isinstance(node.target, ast.Identitas):
            self.visit(node.nilai)
            name = node.target.nama
            if name in self.locals:
                self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)
        elif isinstance(node.target, ast.Akses):
            self.visit(node.target.objek)
            self.visit(node.target.kunci)
            self.visit(node.nilai)
            self.emit(Op.STORE_INDEX)
        elif isinstance(node.target, ast.AmbilProperti):
            self.visit(node.target.objek)
            self.visit(node.nilai)
            self.emit(Op.STORE_ATTR, node.target.nama.nilai)
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

    def visit_CobaTangkap(self, node: ast.CobaTangkap):
        """
        Compiler untuk blok coba-tangkap:
        1. PUSH_TRY <handler_addr>
        2. [Block Coba]
        3. POP_TRY (jika sukses)
        4. JMP <end_addr>
        5. <handler_addr>: (Handler mulai di sini, stack punya Exception object)
        6. STORE_VAR/LOCAL <nama_error>
        7. [Block Tangkap]
        8. <end_addr>:
        """

        # Placeholder untuk jump target handler
        push_try_idx = self.emit(Op.PUSH_TRY, 0)

        # Compile blok 'coba'
        self.visit(node.blok_coba)

        # Jika sukses, pop handler dan lompat ke akhir
        self.emit(Op.POP_TRY)
        jump_to_end = self.emit(Op.JMP, 0)

        # Mulai handler (catch block)
        handler_start = len(self.instructions)
        self.patch_jump(push_try_idx, handler_start)

        # Simpan objek error ke variabel jika ada nama
        if node.nama_error:
            name = node.nama_error.nilai
            if self.parent is not None:
                self.locals.add(name)
                self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)
        else:
            # Jika tidak ada nama variabel, pop error object dari stack
            self.emit(Op.POP)

        # Compile blok 'tangkap'
        self.visit(node.blok_tangkap)

        # Patch jump sukses ke akhir
        end_pos = len(self.instructions)
        self.patch_jump(jump_to_end, end_pos)

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
        if not self.loop_contexts: raise SyntaxError("'berhenti' di luar loop")
        jmp = self.emit(Op.JMP, 0)
        self.loop_contexts[-1]['breaks'].append(jmp)

    def visit_Lanjutkan(self, node: ast.Lanjutkan):
        if not self.loop_contexts: raise SyntaxError("'lanjutkan' di luar loop")
        loop_start = self.loop_contexts[-1]['start']
        self.emit(Op.JMP, loop_start)

    def visit_Konstanta(self, node: ast.Konstanta):
        self.emit(Op.PUSH_CONST, node.nilai)

    def visit_Identitas(self, node: ast.Identitas):
        name = node.nama
        if name in self.locals: self.emit(Op.LOAD_LOCAL, name)
        else: self.emit(Op.LOAD_VAR, name)

    def visit_FoxBinary(self, node: ast.FoxBinary):
        self.visit(node.kiri); self.visit(node.kanan)
        op = node.op.tipe
        if op == TipeToken.TAMBAH: self.emit(Op.ADD)
        elif op == TipeToken.KURANG: self.emit(Op.SUB)
        elif op == TipeToken.KALI: self.emit(Op.MUL)
        elif op == TipeToken.BAGI: self.emit(Op.DIV)
        elif op == TipeToken.MODULO: self.emit(Op.MOD)
        elif op == TipeToken.SAMA_DENGAN: self.emit(Op.EQ)
        elif op == TipeToken.TIDAK_SAMA: self.emit(Op.NEQ)
        elif op == TipeToken.LEBIH_DARI: self.emit(Op.GT)
        elif op == TipeToken.KURANG_DARI: self.emit(Op.LT)
        else: raise NotImplementedError(f"Operator {node.op.nilai} belum didukung")

    def visit_Jodohkan(self, node: ast.Jodohkan):
        self.visit(node.ekspresi)
        end_jumps = []
        for i, kasus in enumerate(node.kasus):
            is_wildcard = isinstance(kasus.pola, ast.PolaWildcard)
            is_binding = isinstance(kasus.pola, ast.PolaIkatanVariabel)

            if not (is_wildcard or is_binding):
                self.emit(Op.DUP)
                if isinstance(kasus.pola, ast.PolaLiteral):
                    self.visit(kasus.pola.nilai); self.emit(Op.EQ)
                else:
                    self.emit(Op.POP); self.emit(Op.PUSH_CONST, False)
                jump_to_next = self.emit(Op.JMP_IF_FALSE, 0)
            elif is_binding:
                self.emit(Op.DUP)
                name = kasus.pola.token.nilai
                if self.parent is not None: self.locals.add(name); self.emit(Op.STORE_LOCAL, name)
                else: self.emit(Op.STORE_VAR, name)
                jump_to_next = None
            else:
                jump_to_next = None

            if kasus.jaga:
                self.visit(kasus.jaga)
                jump_to_next_guard = self.emit(Op.JMP_IF_FALSE, 0)
            else:
                jump_to_next_guard = None

            self.emit(Op.POP)
            self.visit(kasus.badan)
            jump_to_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_to_end)

            next_case_idx = len(self.instructions)
            if jump_to_next_guard: self.patch_jump(jump_to_next_guard, next_case_idx)
            if jump_to_next: self.patch_jump(jump_to_next, next_case_idx)

        self.emit(Op.POP)
        end_target = len(self.instructions)
        for jmp in end_jumps: self.patch_jump(jmp, end_target)

    def visit_Daftar(self, node: ast.Daftar):
        for elem in node.elemen: self.visit(elem)
        self.emit(Op.BUILD_LIST, len(node.elemen))

    def visit_Kamus(self, node: ast.Kamus):
        for k, v in node.pasangan: self.visit(k); self.visit(v)
        self.emit(Op.BUILD_DICT, len(node.pasangan))

    def visit_Akses(self, node: ast.Akses):
        self.visit(node.objek); self.visit(node.kunci); self.emit(Op.LOAD_INDEX)

    def visit_AmbilSemua(self, node: ast.AmbilSemua):
        """
        Compiler untuk 'ambil_semua "module" [sebagai alias]'
        """
        # Path modul (string)
        module_path = node.path_file.nilai

        # Opcode IMPORT akan load module object dan push ke stack
        self.emit(Op.IMPORT, module_path)

        # Jika ada alias, simpan di variabel dengan nama alias
        # Jika tidak, gunakan nama terakhir dari path (e.g. "a.b.c" -> "c")
        alias = node.alias.nilai if node.alias else module_path.split('.')[-1]

        if self.parent is not None:
            self.locals.add(alias)
            self.emit(Op.STORE_LOCAL, alias)
        else:
            self.emit(Op.STORE_VAR, alias)
