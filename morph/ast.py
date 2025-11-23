"""
SKELETON SELF-HOSTING: AST
==========================
File ini berisi draf kode Morph untuk Definisi AST.
Ini adalah padanan dari `transisi/absolute_sntx_morph.py` tetapi ditulis dalam sintaks Morph.
"""

MORPH_SOURCE = r"""
# core/ast.fox
# Struktur AST (Abstract Syntax Tree)

kelas Node maka
    fungsi token_literal() maka
        kembali ""
    akhir

    fungsi string() maka
        kembali ""
    akhir
akhir

kelas Pernyataan warisi Node maka
    fungsi pernyataan_node() maka akhir
akhir

kelas Ekspresi warisi Node maka
    fungsi ekspresi_node() maka akhir
akhir

kelas Program warisi Node maka
    biar pernyataan

    fungsi init() maka
        ini.pernyataan = []
    akhir

    fungsi token_literal() maka
        jika panjang(ini.pernyataan) > 0 maka
            kembali ini.pernyataan[0].token_literal()
        lain
            kembali ""
        akhir
    akhir

    fungsi string() maka
        biar out = ""
        untuk p dalam ini.pernyataan maka
            out = out + p.string()
        akhir
        kembali out
    akhir
akhir

kelas PernyataanBiar warisi Pernyataan maka
    biar token
    biar nama
    biar nilai

    fungsi init(token, nama, nilai) maka
        ini.token = token
        ini.nama = nama
        ini.nilai = nilai
    akhir

    fungsi token_literal() maka
        kembali ini.token.literal
    akhir

    fungsi string() maka
        biar out = ini.token_literal() + " " + ini.nama.string() + " = "
        jika ini.nilai != nil maka
            out = out + ini.nilai.string()
        akhir
        out = out + ";"
        kembali out
    akhir
akhir
"""
