# ivm/frontend.py
"""
Frontend Compiler: Mengubah AST dari Parser menjadi HIR.
"""
from transisi import absolute_sntx_morph as ast
from . import hir

class HIRConverter:
    def __init__(self):
        self.symbol_table = {}
        self.local_count = 0

    def convert(self, ast_node: ast.MRPH):
        """Metode utama untuk memulai konversi."""
        return self._visit(ast_node)

    def _visit(self, node: ast.MRPH):
        """Memanggil metode visit yang sesuai untuk node."""
        method_name = f'visit_{node.__class__.__name__}'
        visitor_method = getattr(self, method_name, self._visit_generic)
        return visitor_method(node)

    def _visit_generic(self, node: ast.MRPH):
        raise NotImplementedError(f"HIRConverter belum mendukung node AST: {node.__class__.__name__}")

    # --- Implementasi Visitor ---

    def visit_Tulis(self, node: ast.Tulis) -> hir.ExpressionStatement:
        # Ubah `tulis(arg)` menjadi HIR.Call yang dibungkus dalam ExpressionStatement
        call_expr = hir.Call(
            target=hir.Global(name='tulis'),
            args=[self._visit(arg) for arg in node.argumen]
        )
        return hir.ExpressionStatement(expression=call_expr)

    def visit_Bagian(self, node: ast.Bagian) -> hir.Program:
        body = [self._visit(stmt) for stmt in node.daftar_pernyataan]
        return hir.Program(body=body)

    def visit_PernyataanEkspresi(self, node: ast.PernyataanEkspresi) -> hir.ExpressionStatement:
        expr = self._visit(node.ekspresi)
        return hir.ExpressionStatement(expression=expr)

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi) -> hir.Call:
        target = self._visit(node.callee)
        args = [self._visit(arg) for arg in node.argumen]
        return hir.Call(target=target, args=args)

    def visit_FoxBinary(self, node: ast.FoxBinary) -> hir.BinaryOperation:
        left = self._visit(node.kiri)
        right = self._visit(node.kanan)
        # TODO: Perlu memetakan TipeToken ke operator string
        op_map = {'+': '+'}
        op = op_map.get(node.op.nilai, node.op.nilai)
        return hir.BinaryOperation(op=op, left=left, right=right)

    def visit_Konstanta(self, node: ast.Konstanta) -> hir.Constant:
        # Node Konstanta bisa berisi Token atau nilai primitif langsung
        if hasattr(node.nilai, 'nilai'):
            return hir.Constant(value=node.nilai.nilai)
        return hir.Constant(value=node.nilai)

    def visit_DeklarasiVariabel(self, node: ast.DeklarasiVariabel) -> hir.VarDeclaration:
        name = node.nama.nilai
        if name in self.symbol_table:
            raise NameError(f"Variabel '{name}' sudah didefinisikan sebelumnya.")

        index = self.local_count
        self.symbol_table[name] = index
        self.local_count += 1

        initializer = self._visit(node.nilai)
        return hir.VarDeclaration(name=name, initializer=initializer)

    def visit_Assignment(self, node: ast.Assignment) -> hir.Assignment:
        # Untuk saat ini, kita hanya mendukung assignment ke nama variabel (Token)
        if not isinstance(node.nama, ast.Token):
             raise NotImplementedError(f"Assignment ke target tipe {type(node.nama)} belum didukung.")

        name = node.nama.nilai
        if name not in self.symbol_table:
            raise NameError(f"Variabel '{name}' untuk diubah nilainya belum didefinisikan.")

        index = self.symbol_table[name]
        target = hir.Local(name=name, index=index)
        value = self._visit(node.nilai)

        return hir.Assignment(target=target, value=value)

    def visit_Identitas(self, node: ast.Identitas) -> hir.Expression:
        name = node.token.nilai
        if name in self.symbol_table:
            index = self.symbol_table[name]
            return hir.Local(name=name, index=index)

        # Jika tidak ditemukan di lokal, asumsikan global
        return hir.Global(name=name)
