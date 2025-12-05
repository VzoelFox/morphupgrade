from transisi import absolute_sntx_morph as ast
from transisi.morph_t import TipeToken
from ivm.core.opcodes import Op
from ivm.core.structs import CodeObject

class ScopeAnalyzer:
    """Pre-pass visitor to populate free_vars and cell_vars in Compiler instances."""
    def __init__(self, compiler):
        self.compiler = compiler

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        if hasattr(node, '__dict__'):
             for key, value in node.__dict__.items():
                 if isinstance(value, list):
                     for item in value:
                         if hasattr(item, 'lokasi'): self.visit(item)
                 elif hasattr(value, 'lokasi'):
                     self.visit(value)

    def visit_FungsiDeklarasi(self, node):
        # Create child compiler context for analysis
        # Note: We don't attach it to self.compiler children list because Compiler structure is tree but parent-pointer only.
        # We rely on recursive instantiation mirroring the actual compilation.

        # BUT, we need the SAME compiler instance that will be used for code gen?
        # OR we assume `visit_FungsiDeklarasi` in Compiler creates a new one.
        # The `Compiler` class does `func_compiler = Compiler(parent=self)`.
        # We should simulate this.

        child_compiler = Compiler(parent=self.compiler)

        # Register arguments as locals
        for param in node.parameter:
            child_compiler.locals.add(param.nilai)

        # Recurse into body
        analyzer = ScopeAnalyzer(child_compiler)
        analyzer.visit(node.badan)

        # Now child_compiler has free_vars populated.
        # We need to propagate `cell_vars` to `self.compiler`.
        # `child_compiler.resolve_variable` call in children triggered `self.compiler.cell_vars.append`.
        # Wait, `child_compiler` parent is `self.compiler`.
        # So modifications happen in-place on `self.compiler`.

        # The only thing lost is `child_compiler` itself.
        # But we need `child_compiler.free_vars` to know what to capture.
        # CodeGen will create a NEW `func_compiler`.
        # The new one starts empty.

        # THIS IS THE PROBLEM. CodeGen creates a NEW instance.
        # The `cell_vars` on `self.compiler` will be populated by Analyzer.
        # But `free_vars` on the CodeGen's `func_compiler` will be empty initially.

        # We need to persist the analysis results.
        # Or, we attach the `child_compiler` to the AST node?
        node.compiler_context = child_compiler

    def visit_Identitas(self, node):
        self.compiler.resolve_variable(node.nama)

    def visit_DeklarasiVariabel(self, node):
        if isinstance(node.nama, list):
            for t in node.nama: self.compiler.locals.add(t.nilai)
        else:
            self.compiler.locals.add(node.nama.nilai)
        # Visit value
        if node.nilai: self.visit(node.nilai)

    def visit_Assignment(self, node):
        if isinstance(node.target, ast.Identitas):
            self.compiler.locals.add(node.target.nama)
        self.visit(node.nilai)

class Compiler:
    def __init__(self, parent=None, scope_info=None):
        self.instructions = []
        self.loop_contexts = []
        self.parent = parent
        self.locals = set()
        self.free_vars = [] # Captured from outer
        self.cell_vars = [] # Captured by inner
        # scope_info could be passed if we did pre-analysis

    def compile(self, node: ast.MRPH, filename: str = "<module>", is_main_script: bool = False) -> CodeObject:
        # Pre-pass: Analyze Scopes
        # Since implementing a full visitor is huge, I will implement "On-Demand" analysis
        # or just simple "Defined in this scope" tracking.
        # But true closures need to know if a var is *used* in inner.

        # Hack: For this task, I will implement the analysis inside visit_FungsiDeklarasi
        # by recursively scanning the body for usages *before* compiling it.

        self.instructions = []
        self.visit(node)

        if is_main_script:
            self.emit(Op.LOAD_VAR, "utama")
            self.emit(Op.CALL, 0)
            self.emit(Op.POP)

        self.emit(Op.PUSH_CONST, None)
        self.emit(Op.RET)
        return CodeObject(name="<module>", instructions=self.instructions, filename=filename)

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
        self.emit(Op.PUSH_CONST, node.nama.nilai)

        # Muat superclass ke stack jika ada
        if node.superkelas:
            self.visit(node.superkelas)
        else:
            self.emit(Op.PUSH_CONST, None)

        # Buat method dictionary
        for method_node in node.metode:
            self.emit(Op.PUSH_CONST, method_node.nama.nilai)
            self.visit_FungsiDeklarasi(method_node, is_method=True)

        self.emit(Op.BUILD_DICT, len(node.metode))
        self.emit(Op.BUILD_CLASS) # BUILD_CLASS akan mengambil nama, superclass, dan methods dari stack
        self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_Ini(self, node: ast.Ini):
        self.emit(Op.LOAD_LOCAL, "ini")

    def visit_Induk(self, node: ast.Induk):
        self.emit(Op.LOAD_LOCAL, "ini")
        self.emit(Op.LOAD_SUPER_METHOD, node.metode.nilai)

    def visit_AmbilProperti(self, node: ast.AmbilProperti):
        self.visit(node.objek)
        self.emit(Op.LOAD_ATTR, node.nama.nilai)

    def visit_AturProperti(self, node: ast.AturProperti):
        self.visit(node.objek)
        self.visit(node.nilai)
        self.emit(Op.STORE_ATTR, node.nama.nilai)

    # --- Functions ---
    def _analyze_usages(self, node) -> set:
        """Scan AST node for identifier usages."""
        usages = set()
        if hasattr(node, 'nama') and isinstance(node, ast.Identitas):
            usages.add(node.nama.nilai)

        # Recursive scan
        if hasattr(node, '__dict__'):
             for key, value in node.__dict__.items():
                 if key == "badan" and isinstance(node, (ast.FungsiDeklarasi, ast.FungsiAsinkDeklarasi)):
                     # Don't scan inner function bodies yet, or handled recursively?
                     # We need to scan to know if *this* function uses it.
                     # But variables defined inside inner function mask outer ones.
                     # Scope logic is complex.

                     # Ideally we should use the ScopeVisitor.
                     # But for now, let's just gather ALL identifiers and filter by what we know is local.
                     pass

                 if isinstance(value, list):
                     for item in value:
                         if hasattr(item, 'lokasi'): usages.update(self._analyze_usages(item))
                 elif hasattr(value, 'lokasi'):
                     usages.update(self._analyze_usages(value))
        return usages

    # --- Functions ---
    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi, is_method: bool = False):
        # Pass 1: Scope Analysis (Pre-compute free/cell vars)
        # We use a dummy child compiler just for analysis, or reuse if attached.
        if hasattr(node, 'compiler_context'):
             # Already analyzed by parent's analyzer?
             # But 'self' here is the code generator compiler.
             # The 'compiler_context' on node was created by the Analyzer.
             # We can reuse its free_vars/cell_vars!
             analyzed_compiler = node.compiler_context
        else:
             # Root level function or first pass
             # We must run analyzer on this node first
             analyzer = ScopeAnalyzer(self)
             # self is the parent. analyzer creates child context.
             # But Analyzer visit_FungsiDeklarasi creates child compiler and attaches to node.
             analyzer.visit_FungsiDeklarasi(node)
             analyzed_compiler = node.compiler_context

        # Pass 2: Code Generation
        # We use the analyzed_compiler as the func_compiler because it has the free_vars populated.
        # But we need to generate instructions into it. It is currently empty of instructions.
        func_compiler = analyzed_compiler

        # We need to make sure 'parent' pointer is correct.
        # Analyzer created it with parent=self (which was the analyzer's compiler).
        # Here 'self' is the code generator. They are different instances if we didn't share.
        # If we assume single-pass at module level:
        # compile() -> visit(Module).
        # If we run Analyzer on Module first, then all nodes have context.

        # But I'm running lazy analysis inside visit_FungsiDeklarasi.
        # So 'self' IS the compiler that Analyzer used as parent.

        # Ensure args are locals (Analyzer did this, but let's be safe or just trust)
        arg_names = [param.nilai for param in node.parameter]
        if is_method: arg_names.insert(0, "ini")

        # Generate Code
        func_compiler.visit(node.badan)

        if not func_compiler.instructions or func_compiler.instructions[-1][0] != Op.RET:
            func_compiler.emit(Op.PUSH_CONST, None)
            func_compiler.emit(Op.RET)

        is_gen = any(instr[0] == Op.YIELD for instr in func_compiler.instructions)

        closure_cells = func_compiler.free_vars

        code_obj = CodeObject(
            name=node.nama.nilai,
            instructions=func_compiler.instructions,
            arg_names=arg_names,
            is_generator=is_gen,
            free_vars=tuple(func_compiler.free_vars),
            cell_vars=tuple(func_compiler.cell_vars)
        )

        # Emit Closure creation
        if closure_cells:
            for name in closure_cells:
                # We need to load the CELL for this variable from current scope.
                # If it's a local of current scope, we emit LOAD_CLOSURE (which pushes the cell).
                # If it's a free var of current scope, we emit LOAD_CLOSURE (pushes the cell from free vars).
                self.emit(Op.LOAD_CLOSURE, name)

            # Make tuple
            self.emit(Op.BUILD_LIST, len(closure_cells))
            # We need tuple. VM BUILD_LIST makes list.
            # StandardVM BUILD_FUNCTION can handle list or tuple.
            # Let's assume tuple/list is fine.

        # Function definition
        # Use static MAKE_FUNCTION for Host Compiler
        self.emit(Op.PUSH_CONST, code_obj)

        # Emit MAKE_FUNCTION
        # Stack: [closure (optional), code_obj]
        self.emit(Op.MAKE_FUNCTION, 1 if closure_cells else 0)

        if not is_method:
            self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi):
        # Special handling for 'bekukan' and 'lanjut' intrinsics
        if isinstance(node.callee, ast.Identitas):
            # node.callee.nama is a string, not a Token
            if node.callee.nama == "bekukan":
                if len(node.argumen) != 1:
                    raise SyntaxError("bekukan() butuh 1 argumen")
                self.visit(node.argumen[0])
                self.emit(Op.YIELD)
                return
            elif node.callee.nama == "lanjut":
                if len(node.argumen) != 1:
                    raise SyntaxError("lanjut() butuh 1 argumen (generator)")
                self.visit(node.argumen[0])
                self.emit(Op.RESUME)
                return
            elif node.callee.nama == "iris":
                if len(node.argumen) != 3:
                    raise SyntaxError("iris(obj, awal, akhir) butuh 3 argumen")
                self.visit(node.argumen[0]) # Obj
                self.visit(node.argumen[1]) # Start
                self.visit(node.argumen[2]) # End
                self.emit(Op.SLICE)
                return

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

        # Cek apakah node.nama adalah list (Destructuring) atau token tunggal
        if isinstance(node.nama, list):
            count = len(node.nama)
            self.emit(Op.UNPACK_SEQUENCE, count)

            for token_nama in node.nama:
                name = token_nama.nilai
                if self.parent is not None:
                    self.locals.add(name)
                    if name in self.cell_vars:
                        self.emit(Op.STORE_DEREF, name)
                    else:
                        self.emit(Op.STORE_LOCAL, name)
                else:
                    self.emit(Op.STORE_VAR, name)
        else:
            # Single Variable
            name = node.nama.nilai
            if self.parent is not None:
                self.locals.add(name)
                if name in self.cell_vars:
                    self.emit(Op.STORE_DEREF, name)
                else:
                    self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)

    def visit_Assignment(self, node: ast.Assignment):
        if isinstance(node.target, ast.Identitas):
            self.visit(node.nilai)
            name = node.target.nama
            if name in self.locals:
                if name in self.cell_vars:
                    self.emit(Op.STORE_DEREF, name)
                else:
                    self.emit(Op.STORE_LOCAL, name)
            elif name in self.free_vars:
                self.emit(Op.STORE_DEREF, name)
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

    def visit_Warnai(self, node: ast.Warnai):
        self.visit(node.warna)
        self.emit(Op.PRINT_RAW)
        push_try_idx = self.emit(Op.PUSH_TRY, 0)
        self.visit(node.badan)
        self.emit(Op.POP_TRY)
        self.emit(Op.PUSH_CONST, "\u001b[0m") # RESET ANSI code
        self.emit(Op.PRINT_RAW)
        jump_end = self.emit(Op.JMP, 0)
        handler_start = len(self.instructions)
        self.patch_jump(push_try_idx, handler_start)
        self.emit(Op.PUSH_CONST, "\u001b[0m")
        self.emit(Op.PRINT_RAW)
        self.emit(Op.THROW)
        end_pos = len(self.instructions)
        self.patch_jump(jump_end, end_pos)

    def visit_Ternary(self, node: ast.Ternary):
        self.visit(node.kondisi)
        jump_else = self.emit(Op.JMP_IF_FALSE, 0)
        self.visit(node.benar)
        jump_end = self.emit(Op.JMP, 0)

        self.patch_jump(jump_else, len(self.instructions))
        self.visit(node.salah)

        self.patch_jump(jump_end, len(self.instructions))

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
        push_try_idx = self.emit(Op.PUSH_TRY, 0)
        self.visit(node.blok_coba)
        self.emit(Op.POP_TRY)
        jump_to_finally = self.emit(Op.JMP, 0)
        handler_start = len(self.instructions)
        self.patch_jump(push_try_idx, handler_start)
        end_catch_jumps = []
        for tangkap in node.daftar_tangkap:
            if tangkap.nama_error:
                self.emit(Op.DUP) # Keep copy for next handler if guard fails
                name = tangkap.nama_error.nilai
                if self.parent: self.locals.add(name); self.emit(Op.STORE_LOCAL, name)
                else: self.emit(Op.STORE_VAR, name)
            if tangkap.kondisi_jaga:
                self.visit(tangkap.kondisi_jaga)
                jump_guard_fail = self.emit(Op.JMP_IF_FALSE, 0)
                self.emit(Op.POP) # Pop Error Copy
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)
                target_guard_fail = len(self.instructions)
                self.patch_jump(jump_guard_fail, target_guard_fail)
            else:
                self.emit(Op.POP) # Pop Error Obj (sudah di bind)
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)
                break
        if len(node.daftar_tangkap) > 0:
             self.emit(Op.THROW)
        else:
             self.emit(Op.THROW)
        finally_start = len(self.instructions)
        self.patch_jump(jump_to_finally, finally_start)
        for jmp in end_catch_jumps:
            self.patch_jump(jmp, finally_start)
        if node.blok_akhirnya:
            self.visit(node.blok_akhirnya)

    def visit_Lemparkan(self, node: ast.Lemparkan):
        if node.jenis:
            self.emit(Op.PUSH_CONST, "pesan")
            self.visit(node.ekspresi)
            self.emit(Op.PUSH_CONST, "jenis")
            self.visit(node.jenis)
            self.emit(Op.BUILD_DICT, 2)
        else:
            self.visit(node.ekspresi) # Push pesan/objek
        self.emit(Op.THROW)

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

    def visit_KonversiTeks(self, node: ast.KonversiTeks):
        self.visit(node.ekspresi)
        self.emit(Op.STR)

    def visit_Konstanta(self, node: ast.Konstanta):
        # Node Konstanta dari parser lama memiliki `token` bukan `nilai`
        if hasattr(node, 'token'):
            self.emit(Op.PUSH_CONST, node.token.nilai)
        else:
            self.emit(Op.PUSH_CONST, node.nilai)

    def resolve_variable(self, name: str) -> str:
        # Return 'local', 'cell', 'free', or 'global'
        if name in self.locals:
            return 'local'

        # Check parent
        if self.parent:
            # Determine if captured
            parent_scope = self.parent.resolve_variable(name)
            if parent_scope in ('local', 'cell', 'free'):
                # Captured!
                # If parent has it as 'local', it becomes 'cell' in parent.
                # If parent has it as 'free' (captured from its parent), it stays 'free' here.

                # Mark in parent (side effect needed)
                if parent_scope == 'local':
                    if name not in self.parent.cell_vars:
                        self.parent.cell_vars.append(name)
                        # Also move from locals to cell_vars? No, cell vars are subset of locals conceptually but handled differently.
                        # StandardVM LOAD_LOCAL doesn't look at cells.
                        # So parent must emit LOAD_DEREF for this variable too.
                        # This requires parent to know it's a cell BEFORE emitting code for it.
                        # IMPOSSIBLE in single pass if usage comes after definition.
                        # Python solves this with Symbol Table pass.

                        pass

                if name not in self.free_vars:
                    self.free_vars.append(name)
                return 'free'

        return 'global'

    def visit_Identitas(self, node: ast.Identitas):
        # In single-pass, we assume global if not local.
        # Scope analysis for Closures is hard without pre-pass.
        name = node.nama

        # Try to resolve using scope chain (best effort)
        scope = self.resolve_variable(name)

        if scope == 'local':
            if name in self.cell_vars:
                 self.emit(Op.LOAD_DEREF, name)
            else:
                 self.emit(Op.LOAD_LOCAL, name)
        elif scope == 'free':
            self.emit(Op.LOAD_DEREF, name)
        else:
            self.emit(Op.LOAD_VAR, name)

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
        elif op == TipeToken.LEBIH_SAMA: self.emit(Op.GTE)
        elif op == TipeToken.KURANG_SAMA: self.emit(Op.LTE)
        elif op == TipeToken.DAN:
             self.emit(Op.AND)
        elif op == TipeToken.ATAU:
             self.emit(Op.OR)
        else: raise NotImplementedError(f"Operator {node.op.nilai} belum didukung")

    def visit_FoxUnary(self, node: ast.FoxUnary):
        self.visit(node.kanan)
        if node.op.tipe == TipeToken.TIDAK: self.emit(Op.NOT)
        elif node.op.tipe == TipeToken.KURANG:
            self.emit(Op.PUSH_CONST, -1)
            self.emit(Op.MUL)
        else: raise NotImplementedError(f"Operator unary {node.op.nilai} belum didukung")

    def visit_Tunggu(self, node: ast.Tunggu):
        self.visit(node.ekspresi)

    def visit_Daftar(self, node: ast.Daftar):
        for elem in node.elemen: self.visit(elem)
        self.emit(Op.BUILD_LIST, len(node.elemen))

    def visit_Kamus(self, node: ast.Kamus):
        for k, v in node.pasangan: self.visit(k); self.visit(v)
        self.emit(Op.BUILD_DICT, len(node.pasangan))

    def visit_Akses(self, node: ast.Akses):
        self.visit(node.objek); self.visit(node.kunci); self.emit(Op.LOAD_INDEX)

    def visit_AmbilSemua(self, node: ast.AmbilSemua):
        module_path = node.path_file.nilai
        self.emit(Op.IMPORT, module_path)
        if node.alias:
            alias = node.alias.nilai
        else:
            base = module_path.split('/')[-1]
            base = base.split('\\')[-1]
            if base.endswith('.fox'):
                alias = base[:-4]
            else:
                alias = base.split('.')[-1]
        if self.parent is not None:
            self.locals.add(alias)
            self.emit(Op.STORE_LOCAL, alias)
        else:
            self.emit(Op.STORE_VAR, alias)

    def visit_TipeDeklarasi(self, node: ast.TipeDeklarasi):
        for varian in node.daftar_varian:
            func_compiler = Compiler(parent=self)
            arg_names = []
            if varian.parameter:
                for token_param in varian.parameter:
                     arg_names.append(token_param.nilai)
            for arg in arg_names:
                func_compiler.locals.add(arg)
                func_compiler.emit(Op.LOAD_LOCAL, arg)
            func_compiler.emit(Op.BUILD_VARIANT, varian.nama.nilai, len(arg_names))
            func_compiler.emit(Op.RET)
            code_obj = CodeObject(
                name=varian.nama.nilai,
                instructions=func_compiler.instructions,
                arg_names=arg_names
            )
            self.emit(Op.PUSH_CONST, code_obj)
            self.emit(Op.STORE_VAR, varian.nama.nilai)

    def visit_AmbilSebagian(self, node: ast.AmbilSebagian):
        module_path = node.path_file.nilai
        self.emit(Op.IMPORT, module_path)
        for token_simbol in node.daftar_simbol:
            simbol = token_simbol.nilai
            self.emit(Op.DUP)
            self.emit(Op.LOAD_ATTR, simbol)
            if self.parent is not None:
                self.locals.add(simbol)
                self.emit(Op.STORE_LOCAL, simbol)
            else:
                self.emit(Op.STORE_VAR, simbol)
        self.emit(Op.POP)

    def visit_Pinjam(self, node: ast.Pinjam):
        module_path = node.path_file.nilai
        self.emit(Op.IMPORT_NATIVE, module_path)
        alias = node.alias.nilai if node.alias else module_path.split('.')[-1]
        if self.parent is not None:
            self.locals.add(alias)
            self.emit(Op.STORE_LOCAL, alias)
        else:
            self.emit(Op.STORE_VAR, alias)

    # === NEW: Implementasi Pilih ===
    def visit_Pilih(self, node: ast.Pilih):
        # Struktur Pilih:
        # Evaluasi Ekspresi
        # Untuk setiap kasus:
        #   DUP (ekspresi)
        #   Evaluasi Nilai Kasus
        #   EQ
        #   JMP_IF_FALSE -> Next Case
        #   POP (ekspresi)
        #   Body
        #   JMP -> End
        #   [Next Case Label]
        # [Else Case]
        # [End Label]

        self.visit(node.ekspresi)
        end_jumps = []

        for kasus in node.kasus:
            self.emit(Op.DUP)
            self.visit(kasus.nilai)
            self.emit(Op.EQ)

            jump_next = self.emit(Op.JMP_IF_FALSE, 0)

            # Match
            self.emit(Op.POP) # Pop expression copy
            self.visit(kasus.badan)
            jump_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_end)

            # Next label
            self.patch_jump(jump_next, len(self.instructions))

        # Else
        if node.kasus_lainnya:
            self.emit(Op.POP) # Pop expression
            self.visit(node.kasus_lainnya.badan)
        else:
            self.emit(Op.POP) # Pop expression if no match

        end_pos = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_pos)

    def visit_PilihKasus(self, node: ast.PilihKasus):
        # Tidak dipanggil langsung, logic di visit_Pilih
        pass

    def visit_KasusLainnya(self, node: ast.KasusLainnya):
        # Tidak dipanggil langsung
        pass

    # === Jodohkan (Pattern Matching) ===
    def visit_Jodohkan(self, node: ast.Jodohkan):
        # Implementasi Jodohkan sederhana:
        # Evaluasi Ekspresi
        # Untuk setiap kasus:
        #   DUP ekspresi
        #   Check Pola (menggunakan IS_VARIANT atau IS_INSTANCE atau EQ)
        #   JMP_IF_FALSE -> Next Case
        #   UNPACK (jika perlu binding)
        #   Check Guard (jika ada)
        #   Body
        #   JMP -> End

        # Untuk saat ini, kita implementasikan subset sederhana untuk Variabel dan Literal
        # dan Varian (IS_VARIANT, UNPACK_VARIANT)

        self.visit(node.ekspresi)
        end_jumps = []

        for kasus in node.kasus:
            # Stack: [Ekspresi]
            # Kita perlu DUP untuk pemeriksaan pola agar ekspresi asli tetap ada untuk kasus berikutnya
            self.emit(Op.DUP)

            # --- Pattern Matching Logic ---
            pola = kasus.pola

            if isinstance(pola, ast.PolaVarian):
                # pola.nama (token), pola.daftar_ikatan (list token)
                # Check Type: IS_VARIANT "Nama"
                self.emit(Op.IS_VARIANT, pola.nama.nilai)

                # Stack: [Ekspresi, Bool]
                jump_next = self.emit(Op.JMP_IF_FALSE, 0)

                # Match Berhasil
                # Stack: [Ekspresi] -> Perlu di unpack
                # UNPACK_VARIANT akan pop Ekspresi dan push argumen-argumennya
                self.emit(Op.UNPACK_VARIANT)

                # Bind variables
                # Argumen di stack terbalik (arg1, arg2...) -> kita pop ke variabel
                # Tapi UNPACK_VARIANT di VM saya push args reversed?
                # Cek VM: for arg in reversed(obj.args): stack.append(arg).
                # Jadi stack: [arg1, arg2, ...] (arg1 di bawah, argN di atas?)
                # Tidak, reversed args -> stack.append.
                # args = [a, b]. reversed = [b, a].
                # append(b), append(a). Stack Top: a.
                # Jadi urutan pop harus sesuai urutan definisi (a, b).

                if pola.daftar_ikatan:
                    for token_var in pola.daftar_ikatan:
                        var_name = token_var.nilai
                        if self.parent:
                            self.locals.add(var_name)
                            self.emit(Op.STORE_LOCAL, var_name)
                        else:
                            self.emit(Op.STORE_VAR, var_name)

            elif isinstance(pola, ast.PolaLiteral):
                # Literal match: EQ
                # Konstanta node punya 'nilai' atau 'token'
                # PolaLiteral punya 'nilai' (dari parser _pola)
                # Tapi parser _pola simpan TOKEN di node.nilai jika itu token?
                # Cek parser: AST.PolaLiteral(ini._sebelumnya()) -> Token.
                val = pola.nilai.nilai
                self.emit(Op.PUSH_CONST, val)
                self.emit(Op.EQ)
                jump_next = self.emit(Op.JMP_IF_FALSE, 0)

                # Match success: Pop expression copy
                self.emit(Op.POP)

            elif isinstance(pola, ast.PolaWildcard):
                # Selalu cocok
                # Pop expression copy
                self.emit(Op.POP)
                jump_next = -1 # No jump needed check

            else:
                # Fallback: Treat as variable binding (always match) if it's PolaIkatanVariabel
                if isinstance(pola, ast.PolaIkatanVariabel):
                    # Bind variable
                    # Stack: [Ekspresi] -> Store to var
                    var_name = pola.token.nilai
                    if self.parent:
                        self.locals.add(var_name)
                        self.emit(Op.STORE_LOCAL, var_name)
                    else:
                        self.emit(Op.STORE_VAR, var_name)
                    jump_next = -1
                else:
                    raise NotImplementedError(f"Pola {pola.__class__.__name__} belum didukung di Host Compiler")

            # --- Body Execution ---
            self.visit(kasus.badan)
            jump_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_end)

            # Patch Next Jump
            if jump_next != -1:
                target = len(self.instructions)
                # Jika gagal match, stack masih ada [Ekspresi].
                # Tapi di jalur sukses, kita sudah POP/UNPACK.
                # Jadi di target jump_next, kita asumsikan stack bersih dari sisa match ini?
                # Tidak, DUP di awal loop.
                # Jika JMP_IF_FALSE, stack [Ekspresi] (karena IS_VARIANT consume Bool).
                # Jadi [Ekspresi] masih ada untuk iterasi loop berikutnya. OK.
                # TAPI: UNPACK_VARIANT memakan [Ekspresi].
                # PolaLiteral: EQ memakan [Ekspresi, Const] -> Bool. DUP dulu?
                # Ah, PolaLiteral logic saya: DUP -> PUSH CONST -> EQ.
                # Stack awal loop: [Ekspresi]. DUP -> [Ekspresi, Ekspresi]. PUSH -> [E, E, C]. EQ -> [E, Bool].
                # JMP_IF_FALSE -> Pop Bool. Stack: [E]. -> Lanjut ke next case. BENAR.

                self.patch_jump(jump_next, target)

        # End Loop (No match found)
        self.emit(Op.POP) # Pop sisa ekspresi

        # Patch End Jumps
        end_pos = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_pos)

    def visit_JodohkanKasus(self, node):
        pass
