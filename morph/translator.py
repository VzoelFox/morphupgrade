"""
SKELETON SELF-HOSTING: INTERPRETER (TRANSLATOR)
===============================================
File ini berisi draf kode Morph untuk Interpreter/Evaluator.
Ini adalah padanan dari `transisi/translator.py` (sekarang `transisi/penerjemah/`) tetapi ditulis dalam sintaks Morph.
"""

MORPH_SOURCE = r"""
# core/translator.fox
# Interpreter Morph yang ditulis dalam Morph (Tree-walking evaluator)

ambil_semua "core/ast.fox" sebagai AST
ambil_semua "core/object.fox" sebagai OBJ

biar NULL = OBJ.Null()
biar TRUE = OBJ.Boolean(benar)
biar FALSE = OBJ.Boolean(salah)

fungsi evaluasi(node, env) maka
    pilih tipe(node)
    ketika AST.Program maka
        kembali evaluasi_program(node, env)
    ketika AST.PernyataanBiar maka
        biar val = evaluasi(node.nilai, env)
        jika adl_error(val) maka kembali val akhir
        env.set(node.nama.nilai, val)
    ketika AST.Identifier maka
        kembali evaluasi_identifier(node, env)
    # ...
    lainnya maka
        kembali error("node tidak dikenal: " + tipe(node))
    akhir
akhir

fungsi evaluasi_program(program, env) maka
    biar hasil = NULL
    untuk stmt dalam program.pernyataan maka
        hasil = evaluasi(stmt, env)
        jika tipe(hasil) == OBJ.RETURN_VALUE maka
            kembali hasil.nilai
        lain jika tipe(hasil) == OBJ.ERROR maka
            kembali hasil
        akhir
    akhir
    kembali hasil
akhir

fungsi evaluasi_identifier(node, env) maka
    biar val = env.get(node.nilai)
    jika val != nil maka
        kembali val
    lain
        kembali error("identifier tidak ditemukan: " + node.nilai)
    akhir
akhir
"""
