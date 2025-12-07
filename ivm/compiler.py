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
        child_compiler = Compiler(parent=self.compiler)
        for param in node.parameter:
            child_compiler.locals.add(param.nilai)
        analyzer = ScopeAnalyzer(child_compiler)
        analyzer.visit(node.badan)
        node.compiler_context = child_compiler

    def visit_Identitas(self, node):
        self.compiler.resolve_variable(node.nama)

    def visit_DeklarasiVariabel(self, node):
        if isinstance(node.nama, list):
            for t in node.nama: self.compiler.locals.add(t.nilai)
        else:
            self.compiler.locals.add(node.nama.nilai)
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

    def compile(self, node: ast.MRPH, filename: str = "<module>", is_main_script: bool = False) -> CodeObject:
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
        if node.superkelas:
            self.visit(node.superkelas)
        else:
            self.emit(Op.PUSH_CONST, None)
        for method_node in node.metode:
            self.emit(Op.PUSH_CONST, method_node.nama.nilai)
            self.visit_FungsiDeklarasi(method_node, is_method=True)
        self.emit(Op.BUILD_DICT, len(node.metode))
        self.emit(Op.BUILD_CLASS)
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
    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi, is_method: bool = False):
        if hasattr(node, 'compiler_context'):
             analyzed_compiler = node.compiler_context
        else:
             analyzer = ScopeAnalyzer(self)
             analyzer.visit_FungsiDeklarasi(node)
             analyzed_compiler = node.compiler_context

        func_compiler = analyzed_compiler
        arg_names = [param.nilai for param in node.parameter]
        if is_method: arg_names.insert(0, "ini")

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

        if closure_cells:
            for name in closure_cells:
                self.emit(Op.LOAD_CLOSURE, name)
            self.emit(Op.BUILD_LIST, len(closure_cells))

        self.emit(Op.PUSH_CONST, code_obj)
        self.emit(Op.MAKE_FUNCTION, 1 if closure_cells else 0)

        if not is_method:
            self.emit(Op.STORE_VAR, node.nama.nilai)

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi):
        if isinstance(node.callee, ast.Identitas):
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

            # --- String Intrinsics Mapping ---
            elif node.callee.nama == "_intrinsik_str_kecil":
                if len(node.argumen) != 1: raise SyntaxError("_intrinsik_str_kecil butuh 1 argumen")
                self.visit(node.argumen[0])
                self.emit(Op.STR_LOWER)
                return
            elif node.callee.nama == "_intrinsik_str_besar":
                if len(node.argumen) != 1: raise SyntaxError("_intrinsik_str_besar butuh 1 argumen")
                self.visit(node.argumen[0])
                self.emit(Op.STR_UPPER)
                return
            elif node.callee.nama == "_intrinsik_str_temukan":
                if len(node.argumen) != 2: raise SyntaxError("_intrinsik_str_temukan butuh 2 argumen")
                self.visit(node.argumen[0])
                self.visit(node.argumen[1])
                self.emit(Op.STR_FIND)
                return
            elif node.callee.nama == "_intrinsik_str_ganti":
                if len(node.argumen) != 3: raise SyntaxError("_intrinsik_str_ganti butuh 3 argumen")
                self.visit(node.argumen[0])
                self.visit(node.argumen[1])
                self.visit(node.argumen[2])
                self.emit(Op.STR_REPLACE)
                return

            # --- System Intrinsics ---
            elif node.callee.nama == "_sys_waktu":
                self.emit(Op.SYS_TIME)
                return
            elif node.callee.nama == "_sys_tidur":
                self.visit(node.argumen[0])
                self.emit(Op.SYS_SLEEP)
                return
            elif node.callee.nama == "_sys_platform":
                self.emit(Op.SYS_PLATFORM)
                return

            # --- Network Intrinsics ---
            elif node.callee.nama == "_net_socket":
                self.visit(node.argumen[0]) # family
                self.visit(node.argumen[1]) # type
                self.emit(Op.NET_SOCKET_NEW)
                return
            elif node.callee.nama == "_net_konek":
                self.visit(node.argumen[0]) # sock
                self.visit(node.argumen[1]) # host
                self.visit(node.argumen[2]) # port
                self.emit(Op.NET_CONNECT)
                return
            elif node.callee.nama == "_net_kirim":
                self.visit(node.argumen[0]) # sock
                self.visit(node.argumen[1]) # data
                self.emit(Op.NET_SEND)
                return
            elif node.callee.nama == "_net_terima":
                self.visit(node.argumen[0]) # sock
                self.visit(node.argumen[1]) # size
                self.emit(Op.NET_RECV)
                return
            elif node.callee.nama == "_net_tutup":
                self.visit(node.argumen[0])
                self.emit(Op.NET_CLOSE)
                return

            # --- File I/O Intrinsics ---
            elif node.callee.nama == "_io_buka":
                self.visit(node.argumen[0]) # path
                self.visit(node.argumen[1]) # mode
                self.emit(Op.IO_OPEN)
                return
            elif node.callee.nama == "_io_baca":
                self.visit(node.argumen[0]) # file
                self.visit(node.argumen[1]) # size
                self.emit(Op.IO_READ)
                return
            elif node.callee.nama == "_io_tulis":
                self.visit(node.argumen[0]) # file
                self.visit(node.argumen[1]) # content
                self.emit(Op.IO_WRITE)
                return
            elif node.callee.nama == "_io_tutup":
                self.visit(node.argumen[0])
                self.emit(Op.IO_CLOSE)
                return
            elif node.callee.nama == "_io_ada":
                self.visit(node.argumen[0])
                self.emit(Op.IO_EXISTS)
                return
            elif node.callee.nama == "_io_hapus":
                self.visit(node.argumen[0])
                self.emit(Op.IO_DELETE)
                return
            elif node.callee.nama == "_io_daftar":
                self.visit(node.argumen[0])
                self.emit(Op.IO_LIST)
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
        self.emit(Op.PUSH_CONST, "\u001b[0m")
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
                self.emit(Op.DUP)
                name = tangkap.nama_error.nilai
                if self.parent: self.locals.add(name); self.emit(Op.STORE_LOCAL, name)
                else: self.emit(Op.STORE_VAR, name)
            if tangkap.kondisi_jaga:
                self.visit(tangkap.kondisi_jaga)
                jump_guard_fail = self.emit(Op.JMP_IF_FALSE, 0)
                self.emit(Op.POP)
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)
                target_guard_fail = len(self.instructions)
                self.patch_jump(jump_guard_fail, target_guard_fail)
            else:
                self.emit(Op.POP)
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)
                break
        if len(node.daftar_tangkap) > 0: self.emit(Op.THROW)
        else: self.emit(Op.THROW)
        finally_start = len(self.instructions)
        self.patch_jump(jump_to_finally, finally_start)
        for jmp in end_catch_jumps: self.patch_jump(jmp, finally_start)
        if node.blok_akhirnya: self.visit(node.blok_akhirnya)

    def visit_Lemparkan(self, node: ast.Lemparkan):
        if node.jenis:
            self.emit(Op.PUSH_CONST, "pesan")
            self.visit(node.ekspresi)
            self.emit(Op.PUSH_CONST, "jenis")
            self.visit(node.jenis)
            self.emit(Op.BUILD_DICT, 2)
        else:
            self.visit(node.ekspresi)
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
        if hasattr(node, 'token'): self.emit(Op.PUSH_CONST, node.token.nilai)
        else: self.emit(Op.PUSH_CONST, node.nilai)

    def resolve_variable(self, name: str) -> str:
        if name in self.locals: return 'local'
        if self.parent:
            parent_scope = self.parent.resolve_variable(name)
            if parent_scope in ('local', 'cell', 'free'):
                if parent_scope == 'local':
                    if name not in self.parent.cell_vars: self.parent.cell_vars.append(name)
                if name not in self.free_vars: self.free_vars.append(name)
                return 'free'
        return 'global'

    def visit_Identitas(self, node: ast.Identitas):
        name = node.nama
        scope = self.resolve_variable(name)
        if scope == 'local':
            if name in self.cell_vars: self.emit(Op.LOAD_DEREF, name)
            else: self.emit(Op.LOAD_LOCAL, name)
        elif scope == 'free': self.emit(Op.LOAD_DEREF, name)
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
        elif op == TipeToken.LEBIH_SAMA: self.emit(Op.GTE)
        elif op == TipeToken.KURANG_SAMA: self.emit(Op.LTE)
        elif op == TipeToken.DAN: self.emit(Op.AND)
        elif op == TipeToken.ATAU: self.emit(Op.OR)
        # Bitwise Mappings
        elif op == TipeToken.BIT_AND: self.emit(Op.BIT_AND)
        elif op == TipeToken.BIT_OR: self.emit(Op.BIT_OR)
        elif op == TipeToken.BIT_XOR: self.emit(Op.BIT_XOR)
        elif op == TipeToken.GESER_KIRI: self.emit(Op.LSHIFT)
        elif op == TipeToken.GESER_KANAN: self.emit(Op.RSHIFT)
        else: raise NotImplementedError(f"Operator {node.op.nilai} belum didukung")

    def visit_FoxUnary(self, node: ast.FoxUnary):
        self.visit(node.kanan)
        if node.op.tipe == TipeToken.TIDAK: self.emit(Op.NOT)
        elif node.op.tipe == TipeToken.KURANG:
            self.emit(Op.PUSH_CONST, -1)
            self.emit(Op.MUL)
        elif node.op.tipe == TipeToken.BIT_NOT: self.emit(Op.BIT_NOT)
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

    def visit_EkspresiIrisan(self, node: ast.EkspresiIrisan):
        self.visit(node.objek)
        if node.awal:
            self.visit(node.awal)
        else:
            self.emit(Op.PUSH_CONST, None)

        if node.akhir:
            self.visit(node.akhir)
        else:
            self.emit(Op.PUSH_CONST, None)

        self.emit(Op.SLICE)

    def visit_AmbilSemua(self, node: ast.AmbilSemua):
        module_path = node.path_file.nilai
        self.emit(Op.IMPORT, module_path)
        if node.alias: alias = node.alias.nilai
        else:
            base = module_path.replace('\\', '/').split('/')[-1]
            alias = base[:-4] if base.endswith('.fox') else base.split('.')[-1]
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

    def visit_Pilih(self, node: ast.Pilih):
        self.visit(node.ekspresi)
        end_jumps = []
        for kasus in node.kasus:
            self.emit(Op.DUP)
            self.visit(kasus.nilai)
            self.emit(Op.EQ)
            jump_next = self.emit(Op.JMP_IF_FALSE, 0)
            self.emit(Op.POP)
            self.visit(kasus.badan)
            jump_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_end)
            self.patch_jump(jump_next, len(self.instructions))
        if node.kasus_lainnya:
            self.emit(Op.POP)
            self.visit(node.kasus_lainnya.badan)
        else:
            self.emit(Op.POP)
        end_pos = len(self.instructions)
        for jmp in end_jumps: self.patch_jump(jmp, end_pos)

    def visit_PilihKasus(self, node: ast.PilihKasus): pass
    def visit_KasusLainnya(self, node: ast.KasusLainnya): pass

    def visit_Jodohkan(self, node: ast.Jodohkan):
        self.visit(node.ekspresi)
        end_jumps = []
        for kasus in node.kasus:
            self.emit(Op.DUP)
            pola = kasus.pola
            jump_next = -1
            if isinstance(pola, ast.PolaVarian):
                self.emit(Op.IS_VARIANT, pola.nama.nilai)
                jump_next = self.emit(Op.JMP_IF_FALSE, 0)
                self.emit(Op.UNPACK_VARIANT)
                if pola.daftar_ikatan:
                    for token_var in pola.daftar_ikatan:
                        var_name = token_var.nilai
                        if self.parent: self.locals.add(var_name); self.emit(Op.STORE_LOCAL, var_name)
                        else: self.emit(Op.STORE_VAR, var_name)
            elif isinstance(pola, ast.PolaLiteral):
                val = pola.nilai.nilai
                self.emit(Op.PUSH_CONST, val)
                self.emit(Op.EQ)
                jump_next = self.emit(Op.JMP_IF_FALSE, 0)
                self.emit(Op.POP)
            elif isinstance(pola, ast.PolaWildcard):
                self.emit(Op.POP)
            elif isinstance(pola, ast.PolaIkatanVariabel):
                var_name = pola.token.nilai
                if self.parent: self.locals.add(var_name); self.emit(Op.STORE_LOCAL, var_name)
                else: self.emit(Op.STORE_VAR, var_name)
            else:
                raise NotImplementedError(f"Pola {pola.__class__.__name__} belum didukung")
            self.visit(kasus.badan)
            jump_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_end)
            if jump_next != -1: self.patch_jump(jump_next, len(self.instructions))
        self.emit(Op.POP)
        end_pos = len(self.instructions)
        for jmp in end_jumps: self.patch_jump(jmp, end_pos)

    def visit_JodohkanKasus(self, node: ast.JodohkanKasus): pass
