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

    def visit_Assignment(self, node: ast.Assignment) -> hir.Statement:
        nilai = self._visit(node.nilai)

        if isinstance(node.target, ast.Identitas):
            name = node.target.nama
            if name not in self.symbol_table:
                # TODO: Mendukung assignment global juga di masa depan.
                raise NameError(f"Variabel '{name}' untuk diubah nilainya belum didefinisikan (hanya lokal yang didukung saat ini).")

            index = self.symbol_table[name]
            hir_target = hir.Local(name=name, index=index)
            # Untuk assignment variabel, kita bungkus dalam ExpressionStatement
            # karena Assignment HIR adalah sebuah Expression.
            assignment_expr = hir.Assignment(target=hir_target, value=nilai)
            return hir.ExpressionStatement(expression=assignment_expr)

        elif isinstance(node.target, ast.Akses):
            hir_target = self._visit(node.target.objek)
            hir_index = self._visit(node.target.kunci)
            return hir.StoreIndex(target=hir_target, index=hir_index, value=nilai)

        elif isinstance(node.target, ast.AmbilProperti):
            hir_target = self._visit(node.target.objek)
            attribute_name = node.target.nama.nilai
            return hir.SetProperty(target=hir_target, attribute=attribute_name, value=nilai)

        else:
            raise NotImplementedError(f"Assignment ke target tipe {type(node.target).__name__} belum didukung.")

    def visit_Identitas(self, node: ast.Identitas) -> hir.Expression:
        name = node.token.nilai
        if name in self.symbol_table:
            index = self.symbol_table[name]
            return hir.Local(name=name, index=index)

        # Jika tidak ditemukan di lokal, asumsikan global
        return hir.Global(name=name)

    def visit_JikaMaka(self, node: ast.JikaMaka) -> hir.If:
        condition = self._visit(node.kondisi)
        then_block = self._visit(node.blok_maka)

        # Untuk saat ini, abaikan 'lain' dan 'lain jika'
        else_block = None
        if node.blok_lain:
            # Di masa depan, kita akan memproses node.blok_lain di sini
            pass

        return hir.If(condition=condition, then_block=then_block, else_block=else_block)

    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi) -> hir.StoreGlobal:
        name = node.nama.nilai
        parameters = [p.nilai for p in node.parameter]

        # Simpan state scope saat ini
        old_symbol_table = self.symbol_table
        old_local_count = self.local_count

        # Buat scope baru untuk fungsi
        self.symbol_table = {}
        self.local_count = 0

        # Tambahkan parameter ke scope baru
        for param_name in parameters:
            self.symbol_table[param_name] = self.local_count
            self.local_count += 1

        # Konversi body fungsi dalam scope baru
        body = self._visit(node.badan)

        # Kembalikan state scope
        self.symbol_table = old_symbol_table
        self.local_count = old_local_count

        # Buat HIR Function Expression
        func_expr = hir.Function(
            name=name,
            parameters=parameters,
            body=body
        )

        # Bungkus dalam StoreGlobal Statement
        return hir.StoreGlobal(name=name, value=func_expr)

    def visit_PernyataanKembalikan(self, node: ast.PernyataanKembalikan) -> hir.Return:
        value = self._visit(node.nilai) if node.nilai else None
        return hir.Return(value=value)

    def visit_Daftar(self, node: ast.Daftar) -> hir.ListLiteral:
        elements = [self._visit(elem) for elem in node.elemen]
        return hir.ListLiteral(elements=elements)

    def visit_Akses(self, node: ast.Akses) -> hir.IndexAccess:
        target = self._visit(node.objek)
        index = self._visit(node.kunci)
        return hir.IndexAccess(target=target, index=index)

    def visit_Selama(self, node: ast.Selama) -> hir.While:
        condition = self._visit(node.kondisi)
        body = self._visit(node.badan)
        return hir.While(condition=condition, body=body)

    def visit_Kamus(self, node: ast.Kamus) -> hir.DictLiteral:
        pairs = []
        for key_node, value_node in node.pasangan:
            hir_key = self._visit(key_node)
            hir_value = self._visit(value_node)
            pairs.append((hir_key, hir_value))
        return hir.DictLiteral(pairs=pairs)

    def visit_AmbilSemua(self, node: ast.AmbilSemua) -> hir.Import:
        path = node.path_file.nilai
        # Asumsikan alias selalu ada untuk saat ini, sesuai dengan `ambil_semua ... sebagai ...`
        if not node.alias:
            raise NotImplementedError("Impor tanpa alias belum didukung di HIR converter.")
        alias = node.alias.nilai
        return hir.Import(path=path, alias=alias)

    def visit_AmbilProperti(self, node: ast.AmbilProperti) -> hir.GetProperty:
        target = self._visit(node.objek)
        attribute = node.nama.nilai
        return hir.GetProperty(target=target, attribute=attribute)

    def visit_Kelas(self, node: ast.Kelas) -> hir.ClassDeclaration:
        # Untuk saat ini, kita hanya menangani nama. Metode akan diabaikan.
        name = node.nama.nilai
        return hir.ClassDeclaration(name=name)
