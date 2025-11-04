# compiler/codegen_llvm.py

from llvmlite import ir
from .runtime import RuntimeManager

# Mengimpor node AST dari engine interpreter yang sudah ada
# Ini menunjukkan penggunaan kembali komponen yang ada
from morph_engine.node_ast import (
    NodeProgram, NodeAngka, NodeDeklarasiVariabel, NodePengenal, NodePanggilFungsi,
    NodeOperasiBiner
)
from morph_engine.token_morph import TipeToken

class LLVMCodeGenerator:
    def __init__(self):
        self.module = ir.Module("morph_program")
        self.runtime = RuntimeManager(self.module)
        self.builder = None
        self.symbol_table = {}  # Akan diperluas untuk menangani scope

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

        # Catat pointer variabel di tabel simbol untuk referensi nanti
        self.symbol_table[nama_var] = var_ptr

    def visit_NodePengenal(self, node: NodePengenal):
        """
        Visitor untuk mengakses nilai variabel.
        """
        nama_var = node.token.nilai
        var_ptr = self.symbol_table.get(nama_var)

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

        # Jika tipe tidak cocok atau bukan integer, lemparkan error
        raise TypeError("Operasi aritmatika saat ini hanya mendukung integer.")
