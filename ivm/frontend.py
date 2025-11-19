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
        """Memanggil metode visit yang sesuai untuk node dan meneruskan info baris."""
        method_name = f'visit_{node.__class__.__name__}'
        visitor_method = getattr(self, method_name, self._visit_generic)
        hir_node = visitor_method(node)

        # Coba dapatkan nomor baris dari token pertama yang tersedia di node AST
        line = -1
        if hasattr(node, 'token') and hasattr(node.token, 'baris'):
            line = node.token.baris
        elif hasattr(node, 'nama') and hasattr(node.nama, 'baris'):
            line = node.nama.baris
        elif hasattr(node, 'kata_kunci') and hasattr(node.kata_kunci, 'baris'):
            line = node.kata_kunci.baris

        if isinstance(hir_node, hir.HIRNode) and hir_node.line == -1:
            hir_node.line = line

        return hir_node

    def _visit_generic(self, node: ast.MRPH):
        raise NotImplementedError(f"HIRConverter belum mendukung node AST: {node.__class__.__name__}")

    # --- Implementasi Visitor ---

    def visit_Tulis(self, node: ast.Tulis) -> hir.ExpressionStatement:
        call_expr = hir.Call(
            target=hir.Global(name='tulis'),
            args=[self._visit(arg) for arg in node.argumen]
        )
        hir_node = hir.ExpressionStatement(expression=call_expr)
        if call_expr.args:
            hir_node.line = call_expr.args[0].line
        return hir_node

    def visit_Bagian(self, node: ast.Bagian) -> hir.Program:
        body = []
        for stmt in node.daftar_pernyataan:
            visited_stmt = self._visit(stmt)
            if visited_stmt:
                body.append(visited_stmt)
        return hir.Program(body=body)

    def visit_PernyataanEkspresi(self, node: ast.PernyataanEkspresi) -> hir.ExpressionStatement:
        expr = self._visit(node.ekspresi)
        hir_node = hir.ExpressionStatement(expression=expr)
        hir_node.line = expr.line
        return hir_node

    def visit_PanggilFungsi(self, node: ast.PanggilFungsi) -> hir.Call:
        target = self._visit(node.callee)
        args = [self._visit(arg) for arg in node.argumen]
        return hir.Call(target=target, args=args)

    def visit_FoxBinary(self, node: ast.FoxBinary) -> hir.BinaryOperation:
        left = self._visit(node.kiri)
        right = self._visit(node.kanan)
        op = node.op.nilai
        hir_node = hir.BinaryOperation(op=op, left=left, right=right)
        hir_node.line = node.op.baris
        return hir_node

    def visit_Konstanta(self, node: ast.Konstanta) -> hir.Constant:
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
            name = node.target.token.nilai
            if name not in self.symbol_table:
                raise NameError(f"Variabel '{name}' untuk diubah nilainya belum didefinisikan.")
            index = self.symbol_table[name]
            hir_target = hir.Local(name=name, index=index)
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
        return hir.Global(name=name)

    def visit_JikaMaka(self, node: ast.JikaMaka) -> hir.If:
        condition = self._visit(node.kondisi)
        then_block = self._visit(node.blok_maka)
        else_block = None
        if node.blok_lain:
            else_block = self._visit(node.blok_lain)
        if node.rantai_lain_jika:
            current_else = else_block
            for i in range(len(node.rantai_lain_jika) - 1, -1, -1):
                cond, block = node.rantai_lain_jika[i]
                nested_if = hir.If(
                    condition=self._visit(cond),
                    then_block=self._visit(block),
                    else_block=current_else
                )
                current_else = hir.Program(body=[nested_if])
            else_block = current_else
        return hir.If(condition=condition, then_block=then_block, else_block=else_block)

    def _visit_function_body(self, node: ast.FungsiDeklarasi, is_method: bool) -> hir.Function:
        name = node.nama.nilai
        parameters = [p.nilai for p in node.parameter]
        old_symbol_table = self.symbol_table
        old_local_count = self.local_count
        self.symbol_table = {}
        self.local_count = 0
        if is_method:
            self.symbol_table['ini'] = self.local_count
            self.local_count += 1
        for param_name in parameters:
            self.symbol_table[param_name] = self.local_count
            self.local_count += 1
        body = self._visit(node.badan)
        self.symbol_table = old_symbol_table
        self.local_count = old_local_count
        return hir.Function(name=name, parameters=parameters, body=body)

    def visit_FungsiDeklarasi(self, node: ast.FungsiDeklarasi) -> hir.StoreGlobal:
        func_expr = self._visit_function_body(node, is_method=False)
        return hir.StoreGlobal(name=func_expr.name, value=func_expr)

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

    def visit_Berhenti(self, node: ast.Berhenti) -> hir.Break:
        return hir.Break()

    def visit_Lanjutkan(self, node: ast.Lanjutkan) -> hir.Continue:
        return hir.Continue()

    def visit_Kamus(self, node: ast.Kamus) -> hir.DictLiteral:
        pairs = []
        for key_node, value_node in node.pasangan:
            hir_key = self._visit(key_node)
            hir_value = self._visit(value_node)
            pairs.append((hir_key, hir_value))
        return hir.DictLiteral(pairs=pairs)

    def visit_AmbilSemua(self, node: ast.AmbilSemua) -> hir.Import:
        path = node.path_file.nilai
        if not node.alias:
            raise NotImplementedError("Impor tanpa alias belum didukung di HIR converter.")
        alias = node.alias.nilai
        return hir.Import(path=path, alias=alias)

    def visit_Pinjam(self, node: ast.Pinjam) -> hir.Borrow:
        path = node.path_file.nilai
        if not node.alias:
            raise SyntaxError("'pinjam' harus menggunakan alias 'sebagai'.")
        alias = node.alias.nilai
        return hir.Borrow(path=path, alias=alias)

    def visit_AmbilProperti(self, node: ast.AmbilProperti) -> hir.GetProperty:
        target = self._visit(node.objek)
        attribute = node.nama.nilai
        return hir.GetProperty(target=target, attribute=attribute)

    def visit_Kelas(self, node: ast.Kelas) -> hir.ClassDeclaration:
        name = node.nama.nilai
        superclass = None
        if node.superkelas:
            superclass = self._visit(node.superkelas)
        methods = []
        for method_node in node.metode:
            methods.append(self._visit_function_body(method_node, is_method=True))
        return hir.ClassDeclaration(name=name, superclass=superclass, methods=methods)

    def visit_Ini(self, node: ast.Ini) -> hir.This:
        return hir.This()

    def visit_Induk(self, node: ast.Induk) -> hir.Super:
        return hir.Super(method=node.metode.nilai)

    def visit_Pilih(self, node: ast.Pilih) -> hir.Switch:
        expression = self._visit(node.ekspresi)
        cases = []
        for case_node in node.kasus:
            # Normalisasi nilai kasus menjadi list
            case_values = case_node.nilai if isinstance(case_node.nilai, list) else [case_node.nilai]
            for val_node in case_values:
                hir_val = self._visit(val_node)
                hir_body = self._visit(case_node.badan)
                cases.append(hir.Case(value=hir_val, body=hir_body))

        default = None
        if node.kasus_lainnya:
            default = self._visit(node.kasus_lainnya.badan)

        return hir.Switch(expression=expression, cases=cases, default=default)

    def visit_JodohkanLiteral(self, node: ast.JodohkanLiteral) -> hir.MatchStatement:
        subject = self._visit(node.subjek)
        cases = []
        for case_node in node.kasus:
            pattern = self._visit(case_node.nilai)
            body = self._visit(case_node.badan)
            cases.append(hir.MatchCase(pattern=pattern, body=body))
        return hir.MatchStatement(subject=subject, cases=cases)
