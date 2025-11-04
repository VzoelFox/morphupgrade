# compiler/codegen_llvm.py
from llvmlite import ir, binding

from morph_engine import node_ast as ast
from morph_engine.token_morph import TipeToken

class LLVMCodeGenerator:
    def __init__(self):
        self.module = ir.Module("morph_program")
        self.builder = None
        self.values = {}

        self.tipe_int = ir.IntType(32)
        self.tipe_double = ir.DoubleType()

    def generate_code(self, node):
        assert isinstance(node, ast.NodeProgram), "Node akar harus NodeProgram"

        # Tipe default untuk main adalah int, tapi bisa berubah jika
        # ekspresi terakhir adalah float.
        return_type = self.tipe_int
        last_stmt_value = None

        # Jika ada pernyataan, coba tentukan tipe return dari yang terakhir
        if node.daftar_pernyataan:
            # Simplifikasi: asumsikan tipe pernyataan terakhir menentukan tipe return main
            # Ini akan disempurnakan di masa depan.
            last_stmt_node = node.daftar_pernyataan[-1]
            if isinstance(last_stmt_node, ast.NodeAngka) and isinstance(last_stmt_node.nilai, float):
                 return_type = self.tipe_double
            # Perluasan untuk OperasiBiner akan lebih kompleks, untuk sekarang tetap int.

        tipe_fungsi_main = ir.FunctionType(return_type, [])
        fungsi_main = ir.Function(self.module, tipe_fungsi_main, name="main")
        blok_entry = fungsi_main.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(blok_entry)

        for stmt in node.daftar_pernyataan:
            last_stmt_value = self.visit(stmt)

        # FIX: Kembalikan nilai dari statement terakhir, bukan 0.
        # Jika tidak ada statement, defaultnya akan mengembalikan 0 (atau 0.0).
        if last_stmt_value:
            # Jika tipe return main berbeda, perlu ada cast (TODO)
            self.builder.ret(last_stmt_value)
        else:
            # Program kosong mengembalikan 0
            self.builder.ret(ir.Constant(return_type, 0))

        return self.module

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Tidak ada metode visitor untuk node: {type(node).__name__}')

    def visit_NodeProgram(self, node):
        pass

    def visit_NodeAngka(self, node):
        nilai = node.token.nilai
        if isinstance(nilai, int):
            return ir.Constant(self.tipe_int, nilai)
        elif isinstance(nilai, float):
            return ir.Constant(self.tipe_double, nilai)
        raise TypeError(f"Tipe data tidak dikenal untuk NodeAngka: {type(nilai)}")

    def visit_NodeOperasiBiner(self, node):
        kiri = self.visit(node.kiri)
        kanan = self.visit(node.kanan)
        op = node.operator.tipe

        # TODO: Implementasikan operasi float (fadd, fsub, dll.)
        # Saat ini hanya mendukung integer.
        if op == TipeToken.TAMBAH:
            return self.builder.add(kiri, kanan, 'addtmp')
        elif op == TipeToken.KURANG:
            return self.builder.sub(kiri, kanan, 'subtmp')
        elif op == TipeToken.KALI:
            return self.builder.mul(kiri, kanan, 'multmp')
        elif op == TipeToken.BAGI:
            return self.builder.sdiv(kiri, kanan, 'divtmp')
        else:
            raise ValueError(f"Operator biner tidak didukung: {op}")
