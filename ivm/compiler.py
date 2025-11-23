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
        Compiler untuk coba-tangkap dengan multiple handlers dan finally.

        Structure:
        [Try Block]
        ...
        PUSH_TRY <handler_start>
        [Body]
        POP_TRY
        JMP <finally_block_success> (atau end jika tidak ada finally)

        <handler_start>:
        # Stack: [Error]

        # Handler 1:
        # Check Guard?
        # If match -> execute -> JMP <finally_block_error>
        # Else -> JMP Next Handler

        # ...

        # Default Handler (Rethrow if no match?)
        THROW (Rethrow)

        <finally_block_success>:
        [Finally Body]
        JMP <end>

        <finally_block_error>:
        [Finally Body]
        JMP <end>

        <end>:
        """
        # Sederhanakan dulu: Single Try, Multiple Catch sequensial logic di dalam satu Handler Block VM.
        # VM hanya support satu PUSH_TRY target.
        # Jadi compiler harus generate kode dispatcher di handler target.

        push_try_idx = self.emit(Op.PUSH_TRY, 0)

        # --- TRY BLOCK ---
        self.visit(node.blok_coba)
        self.emit(Op.POP_TRY)

        # Jump to Finally (Success Path)
        jump_to_finally = self.emit(Op.JMP, 0)

        # --- CATCH BLOCK (Dispatcher) ---
        handler_start = len(self.instructions)
        self.patch_jump(push_try_idx, handler_start)

        # Stack: [ErrorObj]
        # Kita simpan error object di variabel temp atau DUP untuk setiap guard check?
        # Asumsi: Exception Handlers di Morph selalu menangkap ke variabel dulu.

        # Generate Catch handlers
        end_catch_jumps = []

        for tangkap in node.daftar_tangkap:
            # Stack: [ErrorObj]
            # Binding nama error
            if tangkap.nama_error:
                self.emit(Op.DUP) # Keep copy for next handler if guard fails
                name = tangkap.nama_error.nilai
                if self.parent: self.locals.add(name); self.emit(Op.STORE_LOCAL, name)
                else: self.emit(Op.STORE_VAR, name)

            # Guard Check
            if tangkap.kondisi_jaga:
                self.visit(tangkap.kondisi_jaga)
                jump_guard_fail = self.emit(Op.JMP_IF_FALSE, 0)

                # Guard Pass: POP Copy Error (jika ada) dan Execute Body
                self.emit(Op.POP) # Pop Error Copy
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)

                # Guard Fail target
                target_guard_fail = len(self.instructions)
                self.patch_jump(jump_guard_fail, target_guard_fail)
                # Stack: [ErrorObj] (Original) - Lanjut ke handler berikutnya
            else:
                # No Guard: Execute Body langsung
                self.emit(Op.POP) # Pop Error Obj (sudah di bind)
                self.visit(tangkap.badan)
                jump_end_catch = self.emit(Op.JMP, 0)
                end_catch_jumps.append(jump_end_catch)
                # Karena ini catch-all, handler berikutnya unreachable (dead code), break loop
                break

        # Jika fallthrough semua catch (rethrow)
        # Stack: [ErrorObj]
        if len(node.daftar_tangkap) > 0: # Jika ada handler tapi tidak cocok
             self.emit(Op.THROW)
        else:
             # Jika tidak ada catch block (try-finally only)
             # Stack: [ErrorObj]. Kita simpan dulu, exec finally, lalu throw?
             # Kompleks. Asumsikan minimal satu catch atau rethrow.
             self.emit(Op.THROW)

        # Patch all catch exits to Finally
        finally_start = len(self.instructions)
        self.patch_jump(jump_to_finally, finally_start)
        for jmp in end_catch_jumps:
            self.patch_jump(jmp, finally_start)

        # --- FINALLY BLOCK ---
        if node.blok_akhirnya:
            self.visit(node.blok_akhirnya)

    def visit_Lemparkan(self, node: ast.Lemparkan):
        if node.jenis:
            # Sugar: lemparkan "Pesan" jenis "Tipe"
            # Construct Dict Error: {"pesan": <expr>, "jenis": <jenis>}
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
        elif op == TipeToken.LEBIH_SAMA: self.emit(Op.GTE)
        elif op == TipeToken.KURANG_SAMA: self.emit(Op.LTE)
        else: raise NotImplementedError(f"Operator {node.op.nilai} belum didukung")

    def visit_FoxUnary(self, node: ast.FoxUnary):
        self.visit(node.kanan)
        if node.op.tipe == TipeToken.TIDAK: self.emit(Op.NOT)
        elif node.op.tipe == TipeToken.KURANG:
            self.emit(Op.PUSH_CONST, -1)
            self.emit(Op.MUL)
        else: raise NotImplementedError(f"Operator unary {node.op.nilai} belum didukung")

    def visit_Tunggu(self, node: ast.Tunggu):
        # Temporary mock for async await
        self.visit(node.ekspresi)

    def compile_pattern_match(self, pola: ast.Pola, jump_fail_list: list):
        """
        Mencocokkan stack top dengan pola.
        Asumsi: Stack Top adalah Subject yang akan dimatch.
        Strategy: SNAPSHOT/ROLLBACK.
        """
        if isinstance(pola, ast.PolaLiteral):
            self.emit(Op.DUP)
            self.visit(pola.nilai)
            self.emit(Op.EQ)
            jump = self.emit(Op.JMP_IF_FALSE, 0)
            jump_fail_list.append(jump)
            # Success: Subject masih di Top. Harus di-POP.
            self.emit(Op.POP)

        elif isinstance(pola, ast.PolaWildcard):
            # Success: Subject masih di Top. POP.
            self.emit(Op.POP)

        elif isinstance(pola, ast.PolaIkatanVariabel):
            name = pola.token.nilai
            if self.parent is not None:
                self.locals.add(name)
                self.emit(Op.STORE_LOCAL, name)
            else:
                self.emit(Op.STORE_VAR, name)
            # Success: Subject sudah consumed oleh STORE.

        elif isinstance(pola, ast.PolaDaftar):
            # 1. Cek Tipe
            self.emit(Op.DUP)
            self.emit(Op.IS_INSTANCE, "Daftar")
            jump_type = self.emit(Op.JMP_IF_FALSE, 0)
            jump_fail_list.append(jump_type)

            # 2. Cek Panjang
            has_rest = pola.pola_sisa is not None
            min_len = len(pola.daftar_pola)
            self.emit(Op.DUP)
            self.emit(Op.CHECK_LEN_MIN if has_rest else Op.CHECK_LEN, min_len)
            jump_len = self.emit(Op.JMP_IF_FALSE, 0)
            jump_fail_list.append(jump_len)

            # 3. Unpack
            self.emit(Op.UNPACK_SEQUENCE, min_len)
            # Stack sekarang berisi items. Subject (List) sudah di-POP oleh UNPACK.

            for sub_pola in pola.daftar_pola:
                # Match sub-item (Top Stack)
                self.compile_pattern_match(sub_pola, jump_fail_list)

            # Success: All items matched. List is still at Stack Top (because UNPACK peeked).
            # Must POP it to clean up.
            self.emit(Op.POP)

    def visit_Jodohkan(self, node: ast.Jodohkan):
        self.visit(node.ekspresi) # Push Subject
        end_jumps = []

        for kasus in node.kasus:
            # Start Case: Stack [Subject]
            self.emit(Op.SNAPSHOT) # Simpan posisi stack (len=1)
            self.emit(Op.DUP) # Stack: [Subject, Copy]

            jump_fail_list = []
            self.compile_pattern_match(kasus.pola, jump_fail_list)

            # Jika match sukses, cek Guard
            # Saat sukses, stack harusnya bersih dari Copy/Items, sisa [Subject] + Guard expression
            # Tapi tunggu, compile_pattern_match menjamin Copy/Items consumed.
            # Sisa: [Subject] (karena Snapshot di-pop/restore di failure path, tapi success path belum).
            # Snapshot masih ada di frame.snapshots.

            if kasus.jaga:
                self.visit(kasus.jaga)
                jump_guard = self.emit(Op.JMP_IF_FALSE, 0)
                jump_fail_list.append(jump_guard)

            # MATCH SUCCESS
            self.emit(Op.DISCARD_SNAPSHOT) # Buang snapshot karena tidak perlu rollback
            self.emit(Op.POP) # Buang Subject Asli (karena kita masuk body)

            self.visit(kasus.badan)
            jump_end = self.emit(Op.JMP, 0)
            end_jumps.append(jump_end)

            # MATCH FAIL (Rollback)
            restore_label = self.emit(Op.RESTORE) # Stack kembali ke [Subject]

            for jmp in jump_fail_list:
                self.patch_jump(jmp, restore_label)

        # Default Fail (jika semua gagal)
        self.emit(Op.POP) # Pop Subject

        # Patch End Jumps
        end_target = len(self.instructions)
        for jmp in end_jumps:
            self.patch_jump(jmp, end_target)

    def visit_Daftar(self, node: ast.Daftar):
        for elem in node.elemen: self.visit(elem)
        self.emit(Op.BUILD_LIST, len(node.elemen))

    def visit_Kamus(self, node: ast.Kamus):
        for k, v in node.pasangan: self.visit(k); self.visit(v)
        self.emit(Op.BUILD_DICT, len(node.pasangan))

    def visit_Akses(self, node: ast.Akses):
        self.visit(node.objek); self.visit(node.kunci); self.emit(Op.LOAD_INDEX)


    def visit_AmbilSemua(self, node: ast.AmbilSemua):
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

    def visit_Pinjam(self, node: ast.Pinjam):
        # Path file (string)
        module_path = node.path_file.nilai

        # Opcode IMPORT will load the module (FFI or Fox)
        self.emit(Op.IMPORT, module_path)

        # Alias handling
        alias = node.alias.nilai if node.alias else module_path.split('.')[-1]

        if self.parent is not None:
            self.locals.add(alias)
            self.emit(Op.STORE_LOCAL, alias)
        else:
            self.emit(Op.STORE_VAR, alias)
