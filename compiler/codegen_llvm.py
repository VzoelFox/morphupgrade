# compiler/codegen_llvm.py

from llvmlite import ir
from .runtime import RuntimeManager

# Mengimpor node AST dari engine interpreter yang sudah ada
# Ini menunjukkan penggunaan kembali komponen yang ada
from morph_engine.node_ast import (
    NodeProgram, NodeAngka, NodeDeklarasiVariabel, NodePengenal, NodePanggilFungsi,
    NodeOperasiBiner, NodeJikaMaka
)
from morph_engine.token_morph import TipeToken

class LLVMCodeGenerator:
    def __init__(self):
        self.module = ir.Module("morph_program")
        self.runtime = RuntimeManager(self.module)
        self.builder = None
        self.symbol_stack = [{}]  # Stack of scopes, dimulai dengan global scope

    def enter_scope(self):
        """Masuk ke scope baru."""
        self.symbol_stack.append({})

    def exit_scope(self):
        """Keluar dari scope saat ini."""
        self.symbol_stack.pop()

    def lookup_variable(self, name):
        """
        Mencari variabel di semua scope, dari yang terdalam hingga terluar.
        """
        for scope in reversed(self.symbol_stack):
            if name in scope:
                return scope[name]
        return None

    def generate_code(self, ast):
        """
        Titik masuk utama untuk menghasilkan kode LLVM dari AST.
        """
        # Setup fungsi 'main'
        # define i32 @main()
        func_type = ir.FunctionType(ir.IntType(32), [])
        main_func = ir.Function(self.module, func_type, name="main")
        block = main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)

        # Mulai proses kompilasi dari root AST
        self.visit(ast)

        # Setiap fungsi 'main' harus mengembalikan nilai integer (exit code)
        # ret i32 0
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

        return self.module

    def visit(self, node):
        """
        Metode visitor generik untuk dispatch ke metode yang sesuai
        berdasarkan tipe node AST.
        """
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Visitor untuk {type(node).__name__} belum diimplementasikan.")

    # --- Pengunjung Node AST ---

    def visit_NodeProgram(self, node: NodeProgram):
        """
        Visitor untuk node program utama.
        Mengeksekusi setiap pernyataan secara berurutan.
        """
        for stmt in node.daftar_pernyataan:
            self.visit(stmt)

    def visit_NodeAngka(self, node: NodeAngka):
        """
        Visitor untuk literal angka (integer atau float).
        """
        if isinstance(node.nilai, int):
            return ir.Constant(ir.IntType(32), node.nilai)
        elif isinstance(node.nilai, float):
            return ir.Constant(ir.DoubleType(), node.nilai)
        # Tipe lain tidak didukung saat ini
        raise TypeError(f"Tipe angka tidak dikenal: {type(node.nilai)}")

    def visit_NodeDeklarasiVariabel(self, node: NodeDeklarasiVariabel):
        """
        Visitor untuk deklarasi variabel ('biar').
        """
        nama_var = node.nama_variabel.nilai
        nilai_var = self.visit(node.nilai)

        # Alokasikan memori di stack untuk variabel
        # %nama_var = alloca i32
        var_ptr = self.builder.alloca(nilai_var.type, name=nama_var)

        # Simpan nilai awal ke dalam memori yang dialokasikan
        # store i32 %nilai, i32* %nama_var
        self.builder.store(nilai_var, var_ptr)

        # Catat pointer variabel di scope teratas (paling dalam)
        self.symbol_stack[-1][nama_var] = var_ptr

    def visit_NodePengenal(self, node: NodePengenal):
        """
        Visitor untuk mengakses nilai variabel.
        """
        nama_var = node.token.nilai
        var_ptr = self.lookup_variable(nama_var)

        if not var_ptr:
            raise NameError(f"Variabel '{nama_var}' belum dideklarasikan.")

        # Muat nilai dari memori
        # %nilai = load i32, i32* %nama_var
        return self.builder.load(var_ptr, name=nama_var)

    def visit_NodePanggilFungsi(self, node: NodePanggilFungsi):
        """
        Visitor untuk pemanggilan fungsi.
        Saat ini, hanya mendukung 'tulis()' secara khusus.
        """
        nama_fungsi = node.nama_fungsi.nilai

        if nama_fungsi == 'tulis':
            if len(node.daftar_argumen) != 1:
                raise ValueError("Fungsi 'tulis' hanya menerima satu argumen.")

            arg_val = self.visit(node.daftar_argumen[0])
            arg_type = arg_val.type

            # Dapatkan format string dari runtime manager
            format_str_ptr = self.runtime.get_printf_format(arg_type)

            # Panggil fungsi printf
            # call i32 (i8*, ...) @printf(i8* %format, i32 %arg)
            return self.builder.call(self.runtime.printf, [format_str_ptr, arg_val])
        else:
            raise NotImplementedError(f"Fungsi '{nama_fungsi}' belum diimplementasikan di compiler.")

    def visit_NodeOperasiBiner(self, node: NodeOperasiBiner):
        """
        Visitor untuk operasi biner (aritmatika).
        """
        kiri = self.visit(node.kiri)
        kanan = self.visit(node.kanan)
        operator = node.operator.tipe

        # Saat ini hanya mendukung operasi integer
        # Logika untuk float akan ditambahkan nanti
        if isinstance(kiri.type, ir.IntType) and isinstance(kanan.type, ir.IntType):
            if operator == TipeToken.TAMBAH:
                return self.builder.add(kiri, kanan, name="addtmp")
            elif operator == TipeToken.KURANG:
                return self.builder.sub(kiri, kanan, name="subtmp")
            elif operator == TipeToken.KALI:
                return self.builder.mul(kiri, kanan, name="multmp")
            elif operator == TipeToken.BAGI:
                # Untuk integer, kita gunakan signed division
                return self.builder.sdiv(kiri, kanan, name="divtmp")
            # Operasi Perbandingan
            elif operator in [TipeToken.SAMA_DENGAN_SAMA, TipeToken.TIDAK_SAMA, TipeToken.LEBIH_KECIL,
                              TipeToken.LEBIH_BESAR, TipeToken.LEBIH_KECIL_SAMA, TipeToken.LEBIH_BESAR_SAMA]:
                op_map = {
                    TipeToken.SAMA_DENGAN_SAMA: "==",
                    TipeToken.TIDAK_SAMA: "!=",
                    TipeToken.LEBIH_KECIL: "<",
                    TipeToken.LEBIH_BESAR: ">",
                    TipeToken.LEBIH_KECIL_SAMA: "<=",
                    TipeToken.LEBIH_BESAR_SAMA: ">="
                }
                return self.builder.icmp_signed(op_map[operator], kiri, kanan, name="cmptmp")

        # Jika tipe tidak cocok atau bukan integer, lemparkan error
        raise TypeError("Operasi biner saat ini hanya mendukung integer.")

    def visit_NodeJikaMaka(self, node):
        """
        Visitor untuk pernyataan jika-maka-lain.
        Menghasilkan basic blocks dan conditional branches.
        """
        # Dapatkan fungsi 'main' saat ini untuk menambahkan blok baru
        func = self.builder.function

        # Buat blok untuk setiap cabang
        maka_bb = func.append_basic_block('maka')
        lain_bb = func.append_basic_block('lain')
        merge_bb = func.append_basic_block('setelah_jika')

        # 1. Evaluasi Kondisi Utama
        kondisi_val = self.visit(node.kondisi)
        # Buat conditional branch
        self.builder.cbranch(kondisi_val, maka_bb, lain_bb)

        # 2. Isi Blok 'maka'
        self.builder.position_at_start(maka_bb)
        self.enter_scope()
        for stmt in node.blok_maka:
            self.visit(stmt)
        self.exit_scope()
        self.builder.branch(merge_bb) # Lompat ke akhir setelah selesai

        # 3. Isi Blok 'lain' (bisa berisi 'lain jika' atau 'lain')
        self.builder.position_at_start(lain_bb)

        current_lain_bb = lain_bb

        # Proses rantai 'lain jika'
        for i, (kondisi_lj, blok_lj) in enumerate(node.rantai_lain_jika):
            # Buat blok untuk cabang 'lain jika' saat ini dan cabang berikutnya
            maka_lj_bb = func.append_basic_block(f'maka_lain_jika_{i}')
            next_lain_bb = func.append_basic_block(f'lain_berikutnya_{i}')

            # Evaluasi kondisi 'lain jika' dan buat branch
            kondisi_lj_val = self.visit(kondisi_lj)
            self.builder.cbranch(kondisi_lj_val, maka_lj_bb, next_lain_bb)

            # Isi blok 'maka' dari 'lain jika'
            self.builder.position_at_start(maka_lj_bb)
            self.enter_scope()
            for stmt in blok_lj:
                self.visit(stmt)
            self.exit_scope()
            self.builder.branch(merge_bb)

            # Pindah ke blok 'lain' berikutnya untuk iterasi selanjutnya
            self.builder.position_at_start(next_lain_bb)
            current_lain_bb = next_lain_bb

        # Proses blok 'lain' terakhir (jika ada)
        if node.blok_lain:
            self.enter_scope()
            for stmt in node.blok_lain:
                self.visit(stmt)
            self.exit_scope()

        # Semua cabang dari 'lain' (termasuk 'lain jika' yang gagal)
        # harus lompat ke merge block
        self.builder.branch(merge_bb)

        # Posisikan builder di akhir untuk melanjutkan sisa program
        self.builder.position_at_start(merge_bb)
