"""
SKELETON SELF-HOSTING: TRANSPILER
=================================
File ini berisi draf kode Morph untuk Transpiler (misal: Morph -> Python atau Morph -> Bytecode).
"""

MORPH_SOURCE = r"""
# core/transpiler.fox
# Transpiler Morph ke Python (sebagai contoh target)

ambil_semua "core/ast.fox" sebagai AST

kelas TranspilerPy maka
    biar indentasi

    fungsi init() maka
        ini.indentasi = 0
    akhir

    fungsi transpile(node) maka
        pilih tipe(node)
        ketika AST.Program maka
            biar out = ""
            untuk stmt dalam node.pernyataan maka
                out = out + ini.transpile(stmt) + "\n"
            akhir
            kembali out
        ketika AST.PernyataanBiar maka
            kembali node.nama.nilai + " = " + ini.transpile(node.nilai)
        ketika AST.IntegerLiteral maka
            kembali str(node.nilai)
        # ...
        lainnya maka
            kembali "# TODO: " + tipe(node)
        akhir
    akhir
akhir
"""
