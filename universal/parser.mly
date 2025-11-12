%{
open Ast

(* Helper to create a location from Menhir's positions *)
let make_loc startp endp =
  let start_pos = { line = startp.Lexing.pos_lnum; col = startp.Lexing.pos_cnum - startp.Lexing.pos_bol + 1 } in
  let end_pos = { line = endp.Lexing.pos_lnum; col = endp.Lexing.pos_cnum - endp.Lexing.pos_bol + 1 } in
  { start_pos; end_pos }

%}

/* Tokens with values and positions */
%token <float * int * int> ANGKA
%token <string * int * int> NAMA
%token <string * int * int> TEKS

/* Keywords, Operators, Delimiters with position */
%token <int * int> JIKA MAKA LAIN AKHIR SELAMA
%token <int * int> FUNGSI KEMBALI
%token <int * int> KELAS WARISI INI INDUK
%token <int * int> ASINK TUNGGU
%token <int * int> TIPE JODOHKAN DENGAN
%token <int * int> PINJAM AMBIL_SEMUA AMBIL_SEBAGIAN DARI SEBAGAI
%token <int * int> BIAR TETAP UBAH
%token <int * int> TULIS AMBIL
%token <int * int> BENAR SALAH NIL
%token <int * int> DAN ATAU
%token <int * int> KETIKA LAINNYA PILIH

%token <int * int> PLUS MINUS BINTANG GARIS_MIRING PANGKAT PERSEN TIDAK
%token <int * int> SAMA_DENGAN TIDAK_SAMA
%token <int * int> KURANG_DARI LEBIH_DARI KURANG_SAMA LEBIH_SAMA
%token <int * int> EQUAL

%token <int * int> LPAREN RPAREN LBRACKET RBRACKET LBRACE RBRACE
%token <int * int> KOMA DOT COLON SEMICOLON PIPE

/* Special */
%token NEWLINE
%token EOF

/* Precedence - LOWEST to HIGHEST */
%left ATAU
%left DAN
%left SAMA_DENGAN TIDAK_SAMA
%left KURANG_DARI LEBIH_DARI KURANG_SAMA LEBIH_SAMA
%left PLUS MINUS
%left BINTANG GARIS_MIRING PERSEN
%right PANGKAT
%nonassoc TIDAK

/* Rule return types */
%type <Ast.ast_token> comparison_op
%type <string * int * int> var_keyword

/* Entry point */
%start <Ast.program> program

%%

/* ========== PROGRAM ========== */
program:
  | nl* stmts = statement_list EOF
    { { body = stmts } }

/* Helper: optional newlines */
nl:
  | NEWLINE { () }

/* Helper: one or more newlines */
nls:
  | NEWLINE+ { () }

/* ========== STATEMENT LIST ========== */
statement_list:
  | (* empty *)
    { [] }
  | stmt = statement nl* rest = statement_list
    { stmt :: rest }

/* ========== STATEMENTS ========== */
statement:
  /* Variable declaration */
  | kw_data = var_keyword name = NAMA EQUAL value = expr
    {
      let (kw, kwl, kwc) = kw_data in
      let (n, nl, nc) = name in
      let sdesc = DeklarasiVariabel (
        { tipe = kw; nilai = None; baris = kwl; kolom = kwc },
        { tipe = "NAMA"; nilai = Some n; baris = nl; kolom = nc },
        Some value
      ) in
      { sdesc; sloc = make_loc $startpos $endpos }
    }

  /* Assignment */
  | UBAH name = NAMA EQUAL value = expr
    {
      let (n, l, c) = name in
      let sdesc = Assignment (
        { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c },
        value
      ) in
      { sdesc; sloc = make_loc $startpos $endpos }
    }

  /* Print statement */
  | TULIS LPAREN args = argument_list RPAREN
    { { sdesc = Tulis args; sloc = make_loc $startpos $endpos } }

  /* If-then-else */
  | JIKA cond = expr MAKA nls
    then_body = statement_list
    elifs = elif_chain
    else_opt = else_block?
    AKHIR
    { { sdesc = JikaMaka (cond, then_body, elifs, else_opt); sloc = make_loc $startpos $endpos } }

  /* While loop */
  | pos=SELAMA cond = expr MAKA nls
    body = statement_list
    AKHIR
    {
      let (l,c) = pos in
      let token = { tipe = "SELAMA"; nilai = None; baris = l; kolom = c } in
      { sdesc = Selama (token, cond, body); sloc = make_loc $startpos $endpos }
    }

  /* Function declaration */
  | FUNGSI name = NAMA LPAREN params = param_list RPAREN MAKA nls
    body = statement_list
    AKHIR
    {
      let (n, l, c) = name in
      let name_token = { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c } in
      let sdesc = FungsiDeklarasi (name_token, params, body) in
      { sdesc; sloc = make_loc $startpos $endpos }
    }

  /* Return statement */
  | pos=KEMBALI value = expr?
    {
      let (l,c) = pos in
      let token = { tipe = "KEMBALI"; nilai = None; baris = l; kolom = c } in
      { sdesc = PernyataanKembalikan (token, value); sloc = make_loc $startpos $endpos }
    }

  /* Expression statement */
  | e = expr
    { { sdesc = PernyataanEkspresi e; sloc = e.eloc } }

/* Variable keyword helper */
var_keyword:
  | pos=BIAR  { let (l,c) = pos in "BIAR", l, c }
  | pos=TETAP { let (l,c) = pos in "TETAP", l, c }

/* Elif chain */
elif_chain:
  | (* empty *)
    { [] }
  | LAIN JIKA cond = expr MAKA nls body = statement_list rest = elif_chain
    { (cond, body) :: rest }

/* Else block */
else_block:
  | LAIN nls body = statement_list
    { body }

/* Parameter list */
param_list:
  | (* empty *)
    { [] }
  | p = NAMA
    {
      let (n, l, c) = p in
      [{ tipe = "NAMA"; nilai = Some n; baris = l; kolom = c }]
    }
  | p = NAMA KOMA rest = param_list
    {
      let (n, l, c) = p in
      { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c } :: rest
    }

/* Argument list */
argument_list:
  | (* empty *)
    { [] }
  | e = expr
    { [e] }
  | e = expr KOMA rest = argument_list
    { e :: rest }

/* ========== EXPRESSIONS ========== */
expr:
  | e = comparison_expr { e }

comparison_expr:
  | e = additive_expr { e }
  | left = comparison_expr op = comparison_op right = additive_expr
    { { edesc = FoxBinary (left, op, right); eloc = make_loc $startpos $endpos } }

comparison_op:
  | pos=SAMA_DENGAN  { let (l,c) = pos in { tipe = "SAMA_DENGAN"; nilai = None; baris = l; kolom = c } }
  | pos=TIDAK_SAMA   { let (l,c) = pos in { tipe = "TIDAK_SAMA"; nilai = None; baris = l; kolom = c } }
  | pos=KURANG_DARI  { let (l,c) = pos in { tipe = "KURANG_DARI"; nilai = None; baris = l; kolom = c } }
  | pos=LEBIH_DARI   { let (l,c) = pos in { tipe = "LEBIH_DARI"; nilai = None; baris = l; kolom = c } }
  | pos=KURANG_SAMA  { let (l,c) = pos in { tipe = "KURANG_SAMA"; nilai = None; baris = l; kolom = c } }
  | pos=LEBIH_SAMA   { let (l,c) = pos in { tipe = "LEBIH_SAMA"; nilai = None; baris = l; kolom = c } }

additive_expr:
  | e = multiplicative_expr { e }
  | left = additive_expr pos=PLUS right = multiplicative_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "PLUS"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }
  | left = additive_expr pos=MINUS right = multiplicative_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "MINUS"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }

multiplicative_expr:
  | e = power_expr { e }
  | left = multiplicative_expr pos=BINTANG right = power_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "BINTANG"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }
  | left = multiplicative_expr pos=GARIS_MIRING right = power_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "GARIS_MIRING"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }
  | left = multiplicative_expr pos=PERSEN right = power_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "PERSEN"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }

power_expr:
  | e = unary_expr { e }
  | left = unary_expr pos=PANGKAT right = power_expr
    { let (l,c) = pos in { edesc = FoxBinary (left, { tipe = "PANGKAT"; nilai = None; baris = l; kolom = c }, right); eloc = make_loc $startpos $endpos } }

unary_expr:
  | e = postfix_expr { e }
  | pos=MINUS e = unary_expr
    { let (l,c) = pos in { edesc = FoxUnary ({ tipe = "MINUS"; nilai = None; baris = l; kolom = c }, e); eloc = make_loc $startpos $endpos } }
  | pos=TIDAK e = unary_expr
    { let (l,c) = pos in { edesc = FoxUnary ({ tipe = "TIDAK"; nilai = None; baris = l; kolom = c }, e); eloc = make_loc $startpos $endpos } }

postfix_expr:
  | e = primary_expr { e }
  | callee = postfix_expr pos=LPAREN args = argument_list RPAREN
    {
      let (l,c) = pos in
      let token = { tipe = "LPAREN"; nilai = None; baris = l; kolom = c } in
      let loc = make_loc $startpos $endpos in
      { edesc = PanggilFungsi (callee, token, args); eloc = loc }
    }

primary_expr:
  | n = ANGKA
    {
      let (value, _, _) = n in
      let loc = make_loc $startpos $endpos in
      { edesc = Konstanta (Angka value); eloc = loc }
    }
  | n = NAMA
    {
      let (name, l, c) = n in
      let loc = make_loc $startpos $endpos in
      { edesc = Identitas { tipe = "NAMA"; nilai = Some name; baris = l; kolom = c }; eloc = loc }
    }
  | s = TEKS
    {
      let (str, _, _) = s in
      let loc = make_loc $startpos $endpos in
      { edesc = Konstanta (Teks str); eloc = loc }
    }
  | BENAR
    { { edesc = Konstanta Benar; eloc = make_loc $startpos $endpos } }
  | SALAH
    { { edesc = Konstanta Salah; eloc = make_loc $startpos $endpos } }
  | NIL
    { { edesc = Konstanta Nil; eloc = make_loc $startpos $endpos } }
  | LPAREN e = expr RPAREN
    { e }
