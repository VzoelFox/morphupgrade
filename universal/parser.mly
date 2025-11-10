%{
open Ast

(* Helper untuk membuat token dengan informasi lokasi dari Menhir *)
let make_tok_at start_pos end_pos lexeme =
  {
    lexeme = lexeme;
    line = start_pos.Lexing.pos_lnum;
    col = start_pos.Lexing.pos_cnum - start_pos.Lexing.pos_bol + 1;
  }
%}

/* Daftar Token */
%token <string> LITERAL_ANGKA IDENTIFIER
%token PLUS MINUS BINTANG GARIS_MIRING PANGKAT PERSEN
%token SAMA_DENGAN
%token BIAR UBAH
%token LPAREN RPAREN
%token EOF

/* Presedensi dan Asosiativas Operator */
%right PANGKAT
%left BINTANG GARIS_MIRING PERSEN
%left PLUS MINUS

%start <Ast.bagian> program
%%

/* Aturan Grammar */
program:
  | stmts=list(stmt) EOF { { daftar_pernyataan = stmts } }
;

stmt:
  | kw=BIAR id=IDENTIFIER SAMA_DENGAN init=expr
    { DeklarasiVariabel(make_tok_at $startpos(kw) $endpos(kw) "biar", make_tok_at $startpos(id) $endpos(id) id, Some init) }
  | kw=UBAH id=IDENTIFIER SAMA_DENGAN value=expr
    { Assignment(make_tok_at $startpos(id) $endpos(id) id, value) }
;

expr:
  | e1=expr op=PLUS e2=expr         { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "+", e2) }
  | e1=expr op=MINUS e2=expr        { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "-", e2) }
  | e1=expr op=BINTANG e2=expr      { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "*", e2) }
  | e1=expr op=GARIS_MIRING e2=expr { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "/", e2) }
  | e1=expr op=PANGKAT e2=expr      { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "^", e2) }
  | e1=expr op=PERSEN e2=expr       { FoxBinary(e1, make_tok_at $startpos(op) $endpos(op) "%", e2) }
  | n=LITERAL_ANGKA                 { Konstanta (make_tok_at $startpos(n) $endpos(n) n) }
  | id=IDENTIFIER                   { Identitas (make_tok_at $startpos(id) $endpos(id) id) }
  | LPAREN e=expr RPAREN            { e }
;
