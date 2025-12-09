"""
SKELETON SELF-HOSTING: LEXER
============================
File ini berisi draf kode Morph untuk Lexer (Analisis Leksikal).
Ini adalah padanan dari `transisi/lx.py` tetapi ditulis dalam sintaks Morph.
"""

MORPH_SOURCE = r"""
# core/lx.fox
# Lexer Morph yang ditulis dalam Morph

ambil_semua "core/morph_t.fox" sebagai T

kelas Lexer maka
    biar masukan
    biar posisi
    biar posisi_baca
    biar ch
    biar baris
    biar kolom

    fungsi init(masukan_kode) maka
        ini.masukan = masukan_kode
        ini.posisi = 0
        ini.posisi_baca = 0
        ini.ch = ""
        ini.baris = 1
        ini.kolom = 1
        ini.baca_karakter()
    akhir

    fungsi baca_karakter() maka
        jika ini.posisi_baca >= panjang(ini.masukan) maka
            ini.ch = 0 # EOF
        lain
            ini.ch = ini.masukan[ini.posisi_baca]
        akhir

        ini.posisi = ini.posisi_baca
        ini.posisi_baca = ini.posisi_baca + 1
        ini.kolom = ini.kolom + 1
    akhir

    fungsi intip_karakter() maka
        jika ini.posisi_baca >= panjang(ini.masukan) maka
            kembali 0
        lain
            kembali ini.masukan[ini.posisi_baca]
        akhir
    akhir

    fungsi token_berikutnya() maka
        biar tok = nil
        ini.lewati_spasi()

        pilih ini.ch
        ketika "=" maka
            jika ini.intip_karakter() == "=" maka
                ini.baca_karakter()
                tok = T.Token(T.EQ, "==", ini.baris, ini.kolom)
            lain
                tok = T.Token(T.ASSIGN, "=", ini.baris, ini.kolom)
            akhir
        ketika "+" maka
            tok = T.Token(T.PLUS, "+", ini.baris, ini.kolom)
        ketika "-" maka
            tok = T.Token(T.MINUS, "-", ini.baris, ini.kolom)
        ketika "!" maka
            jika ini.intip_karakter() == "=" maka
                ini.baca_karakter()
                tok = T.Token(T.NOT_EQ, "!=", ini.baris, ini.kolom)
            lain
                tok = T.Token(T.BANG, "!", ini.baris, ini.kolom)
            akhir
        ketika "*" maka
            tok = T.Token(T.ASTERISK, "*", ini.baris, ini.kolom)
        ketika "/" maka
            tok = T.Token(T.SLASH, "/", ini.baris, ini.kolom)
        ketika "<" maka
            tok = T.Token(T.LT, "<", ini.baris, ini.kolom)
        ketika ">" maka
            tok = T.Token(T.GT, ">", ini.baris, ini.kolom)
        ketika ";" maka
            tok = T.Token(T.SEMICOLON, ";", ini.baris, ini.kolom)
        ketika "(" maka
            tok = T.Token(T.LPAREN, "(", ini.baris, ini.kolom)
        ketika ")" maka
            tok = T.Token(T.RPAREN, ")", ini.baris, ini.kolom)
        ketika "," maka
            tok = T.Token(T.COMMA, ",", ini.baris, ini.kolom)
        ketika "{" maka
            tok = T.Token(T.LBRACE, "{", ini.baris, ini.kolom)
        ketika "}" maka
            tok = T.Token(T.RBRACE, "}", ini.baris, ini.kolom)
        ketika 0 maka
            tok = T.Token(T.EOF, "", ini.baris, ini.kolom)
        lainnya maka
            jika adl_huruf(ini.ch) maka
                biar ident = ini.baca_identifier()
                biar tipe = T.cari_keyword(ident)
                kembali T.Token(tipe, ident, ini.baris, ini.kolom)
            lain jika adl_digit(ini.ch) maka
                biar num = ini.baca_angka()
                kembali T.Token(T.INT, num, ini.baris, ini.kolom)
            lain
                tok = T.Token(T.ILLEGAL, ini.ch, ini.baris, ini.kolom)
            akhir
        akhir

        ini.baca_karakter()
        kembali tok
    akhir

    fungsi baca_identifier() maka
        biar posisi_awal = ini.posisi
        selama adl_huruf(ini.ch) maka
            ini.baca_karakter()
        akhir
        kembali ini.masukan[posisi_awal : ini.posisi]
    akhir

    fungsi baca_angka() maka
        biar posisi_awal = ini.posisi
        selama adl_digit(ini.ch) maka
            ini.baca_karakter()
        akhir
        kembali ini.masukan[posisi_awal : ini.posisi]
    akhir

    fungsi lewati_spasi() maka
        selama ini.ch == " " atau ini.ch == "\t" atau ini.ch == "\n" atau ini.ch == "\r" maka
            jika ini.ch == "\n" maka
                ini.baris = ini.baris + 1
                ini.kolom = 0
            akhir
            ini.baca_karakter()
        akhir
    akhir
akhir

fungsi adl_huruf(ch) maka
    kembali ("a" <= ch dan ch <= "z") atau ("A" <= ch dan ch <= "Z") atau ch == "_"
akhir

fungsi adl_digit(ch) maka
    kembali "0" <= ch dan ch <= "9"
akhir
"""
