"""
SKELETON SELF-HOSTING: PARSER
=============================
File ini berisi draf kode Morph untuk Parser (Analisis Sintaksis).
Ini adalah padanan dari `transisi/crusher.py` tetapi ditulis dalam sintaks Morph.
"""

MORPH_SOURCE = r"""
# core/crusher.fox
# Parser Morph yang ditulis dalam Morph

ambil_semua "core/morph_t.fox" sebagai T
ambil_semua "core/lx.fox" sebagai Lex
ambil_semua "core/ast.fox" sebagai AST

kelas Parser maka
    biar lexer
    biar token_sekarang
    biar token_berikutnya

    fungsi init(l) maka
        ini.lexer = l
        ini.maju_token()
        ini.maju_token()
    akhir

    fungsi maju_token() maka
        ini.token_sekarang = ini.token_berikutnya
        ini.token_berikutnya = ini.lexer.token_berikutnya()
    akhir

    fungsi parse_program() maka
        biar program = AST.Program()
        program.pernyataan = []

        selama ini.token_sekarang.tipe != T.EOF maka
            biar stmt = ini.parse_pernyataan()
            jika stmt != nil maka
                program.pernyataan.tambah(stmt)
            akhir
            ini.maju_token()
        akhir

        kembali program
    akhir

    fungsi parse_pernyataan() maka
        pilih ini.token_sekarang.tipe
        ketika T.BIAR maka
            kembali ini.parse_pernyataan_biar()
        ketika T.KEMBALI maka
            kembali ini.parse_pernyataan_kembali()
        lainnya maka
            kembali ini.parse_pernyataan_ekspresi()
        akhir
    akhir

    fungsi parse_pernyataan_biar() maka
        biar token_stmt = ini.token_sekarang

        jika tidak ini.harapkan_berikutnya(T.IDENTIFIER) maka
            kembali nil
        akhir

        biar nama = AST.Identitas(ini.token_sekarang, ini.token_sekarang.literal)

        jika tidak ini.harapkan_berikutnya(T.ASSIGN) maka
            kembali nil
        akhir

        ini.maju_token()
        biar nilai = ini.parse_ekspresi(LOWEST)

        jika ini.token_berikutnya_adalah(T.SEMICOLON) maka
            ini.maju_token()
        akhir

        kembali AST.PernyataanBiar(token_stmt, nama, nilai)
    akhir

    # ... (Implementasi metode parse lainnya) ...

    fungsi harapkan_berikutnya(tipe_token) maka
        jika ini.token_berikutnya.tipe == tipe_token maka
            ini.maju_token()
            kembali benar
        lain
            ini.error_token_berikutnya(tipe_token)
            kembali salah
        akhir
    akhir
akhir
"""
