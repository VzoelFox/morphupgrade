%{
open Ast

(*
  Helper untuk membuat AST token (record kaya) dari informasi yang diberikan
  oleh parser (tipe token, nilai literal, dan posisi).
*)
let make_ast_token tipe literal nilai start_pos _end_pos : ast_token =
  {
    tipe = tipe;
    nilai = nilai;
    literal = literal;
    baris = start_pos.Lexing.pos_lnum;
    kolom = start_pos.Lexing.pos_cnum - start_pos.Lexing.pos_bol + 1;
  }
%}

/*
  Deklarasi token untuk Menhir. Tipe data di sini (misal: <string>)
  dibuat oleh Menhir menjadi tipe `Parser.token`.
*/
%token <string> LITERAL_ANGKA IDENTIFIER
%token PLUS MINUS BINTANG GARIS_MIRING PANGKAT PERSEN
%token SAMA_DENGAN
%token BIAR UBAH TULIS
%token LPAREN RPAREN KOMA LBRACKET RBRACKET LBRACE RBRACE
%token DOT PIPE COLON
%token JIKA MAKA LAIN AKHIR SELAMA
%token FUNGSI KELAS WARISI INI INDUK KEMBALI
%token ASINK TUNGGU
%token TIPE JODOHKAN DENGAN
%token PINJAM AMBIL_SEMUA AMBIL_SEBAGIAN DARI SEBAGAI
%token EOF

/* Mendefinisikan titik masuk utama dan tipe yang dihasilkannya (root AST) */
%start <Ast.program> program
%%

/* Aturan Grammar */

program:
  | stmts=list(stmt) EOF { { daftar_pernyataan = stmts } }
;

stmt:
  | _kw=BIAR id=IDENTIFIER _eq=SAMA_DENGAN init=expr
    {
      let kw_tok = make_ast_token BIAR "biar" VKosong $startpos(_kw) $endpos(_kw) in
      let id_tok = make_ast_token IDENTIFIER id (VTeks id) $startpos(id) $endpos(id) in
      DeklarasiVariabel(kw_tok, id_tok, Some init)
    }
  | _kw=UBAH id=IDENTIFIER _eq=SAMA_DENGAN value=expr
    {
      let id_tok = make_ast_token IDENTIFIER id (VTeks id) $startpos(id) $endpos(id) in
      Assignment(id_tok, value)
    }
  | _kw=TULIS _lp=LPAREN args=separated_list(KOMA, expr) _rp=RPAREN
    {
      Tulis(args)
    }
;

expr:
  | e1=expr _op=PLUS e2=expr
    { FoxBinary(e1, make_ast_token PLUS "+" VKosong $startpos(_op) $endpos(_op), e2) }
  | e1=expr _op=MINUS e2=expr
    { FoxBinary(e1, make_ast_token MINUS "-" VKosong $startpos(_op) $endpos(_op), e2) }
  | e1=expr _op=BINTANG e2=expr
    { FoxBinary(e1, make_ast_token BINTANG "*" VKosong $startpos(_op) $endpos(_op), e2) }
  | e1=expr _op=GARIS_MIRING e2=expr
    { FoxBinary(e1, make_ast_token GARIS_MIRING "/" VKosong $startpos(_op) $endpos(_op), e2) }
  | e1=expr _op=PANGKAT e2=expr
    { FoxBinary(e1, make_ast_token PANGKAT "^" VKosong $startpos(_op) $endpos(_op), e2) }
  | e1=expr _op=PERSEN e2=expr
    { FoxBinary(e1, make_ast_token PERSEN "%" VKosong $startpos(_op) $endpos(_op), e2) }
  | n=LITERAL_ANGKA
    {
      let v = float_of_string n in
      let tok = make_ast_token LITERAL_ANGKA n (VAngka v) $startpos(n) $endpos(n) in
      Konstanta tok
    }
  | id=IDENTIFIER
    {
      let tok = make_ast_token IDENTIFIER id (VTeks id) $startpos(id) $endpos(id) in
      Identitas tok
    }
  | _lp=LPAREN e=expr _rp=RPAREN
    { e }
;
