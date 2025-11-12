%{
open Ast
%}

/* Tokens */
%token <float * int * int> ANGKA
%token <string * int * int> NAMA
%token <string * int * int> TEKS

/* Keywords */
%token JIKA MAKA LAIN AKHIR SELAMA
%token FUNGSI KEMBALI
%token KELAS WARISI INI INDUK
%token ASINK TUNGGU
%token TIPE JODOHKAN DENGAN
%token PINJAM AMBIL_SEMUA AMBIL_SEBAGIAN DARI SEBAGAI
%token BIAR TETAP UBAH
%token TULIS AMBIL
%token BENAR SALAH NIL
%token DAN ATAU TIDAK
%token KETIKA LAINNYA PILIH

/* Operators */
%token PLUS MINUS BINTANG GARIS_MIRING PANGKAT PERSEN
%token SAMA_DENGAN TIDAK_SAMA
%token KURANG_DARI LEBIH_DARI KURANG_SAMA LEBIH_SAMA
%token EQUAL

/* Delimiters */
%token LPAREN RPAREN LBRACKET RBRACKET LBRACE RBRACE
%token KOMA DOT COLON SEMICOLON PIPE

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
  | kw = var_keyword name = NAMA EQUAL value = expr
    {
      let (n, l, c) = name in
      DeklarasiVariabel (
        { tipe = kw; nilai = None; baris = 0; kolom = 0 },
        { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c },
        Some value
      )
    }

  /* Assignment */
  | UBAH name = NAMA EQUAL value = expr
    {
      let (n, l, c) = name in
      Assignment (
        { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c },
        value
      )
    }

  /* Print statement */
  | TULIS LPAREN args = argument_list RPAREN
    { Tulis args }

  /* If-then-else */
  | JIKA cond = expr MAKA nls
    then_body = statement_list
    elifs = elif_chain
    else_opt = else_block?
    AKHIR
    { JikaMaka (cond, then_body, elifs, else_opt) }

  /* While loop */
  | SELAMA cond = expr MAKA nls
    body = statement_list
    AKHIR
    {
      let token = { tipe = "SELAMA"; nilai = None; baris = 0; kolom = 0 } in
      Selama (token, cond, body)
    }

  /* Function declaration */
  | FUNGSI name = NAMA LPAREN params = param_list RPAREN MAKA nls
    body = statement_list
    AKHIR
    {
      let (n, l, c) = name in
      let name_token = { tipe = "NAMA"; nilai = Some n; baris = l; kolom = c } in
      FungsiDeklarasi (name_token, params, body)
    }

  /* Return statement */
  | KEMBALI value = expr?
    {
      let token = { tipe = "KEMBALI"; nilai = None; baris = 0; kolom = 0 } in
      PernyataanKembalikan (token, value)
    }

  /* Expression statement */
  | e = expr
    { PernyataanEkspresi e }

/* Variable keyword helper */
var_keyword:
  | BIAR  { "BIAR" }
  | TETAP { "TETAP" }

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
    { FoxBinary (left, op, right) }

comparison_op:
  | SAMA_DENGAN  { { tipe = "SAMA_DENGAN"; nilai = None; baris = 0; kolom = 0 } }
  | TIDAK_SAMA   { { tipe = "TIDAK_SAMA"; nilai = None; baris = 0; kolom = 0 } }
  | KURANG_DARI  { { tipe = "KURANG_DARI"; nilai = None; baris = 0; kolom = 0 } }
  | LEBIH_DARI   { { tipe = "LEBIH_DARI"; nilai = None; baris = 0; kolom = 0 } }
  | KURANG_SAMA  { { tipe = "KURANG_SAMA"; nilai = None; baris = 0; kolom = 0 } }
  | LEBIH_SAMA   { { tipe = "LEBIH_SAMA"; nilai = None; baris = 0; kolom = 0 } }

additive_expr:
  | e = multiplicative_expr { e }
  | left = additive_expr PLUS right = multiplicative_expr
    { FoxBinary (left, { tipe = "PLUS"; nilai = None; baris = 0; kolom = 0 }, right) }
  | left = additive_expr MINUS right = multiplicative_expr
    { FoxBinary (left, { tipe = "MINUS"; nilai = None; baris = 0; kolom = 0 }, right) }

multiplicative_expr:
  | e = power_expr { e }
  | left = multiplicative_expr BINTANG right = power_expr
    { FoxBinary (left, { tipe = "BINTANG"; nilai = None; baris = 0; kolom = 0 }, right) }
  | left = multiplicative_expr GARIS_MIRING right = power_expr
    { FoxBinary (left, { tipe = "GARIS_MIRING"; nilai = None; baris = 0; kolom = 0 }, right) }
  | left = multiplicative_expr PERSEN right = power_expr
    { FoxBinary (left, { tipe = "PERSEN"; nilai = None; baris = 0; kolom = 0 }, right) }

power_expr:
  | e = unary_expr { e }
  | left = unary_expr PANGKAT right = power_expr
    { FoxBinary (left, { tipe = "PANGKAT"; nilai = None; baris = 0; kolom = 0 }, right) }

unary_expr:
  | e = postfix_expr { e }
  | MINUS e = unary_expr
    { FoxUnary ({ tipe = "MINUS"; nilai = None; baris = 0; kolom = 0 }, e) }
  | TIDAK e = unary_expr
    { FoxUnary ({ tipe = "TIDAK"; nilai = None; baris = 0; kolom = 0 }, e) }

postfix_expr:
  | e = primary_expr { e }
  | callee = postfix_expr LPAREN args = argument_list RPAREN
    {
      let token = { tipe = "LPAREN"; nilai = None; baris = 0; kolom = 0 } in
      PanggilFungsi (callee, token, args)
    }

primary_expr:
  | n = ANGKA
    {
      let (value, l, c) = n in
      Konstanta { tipe = "ANGKA"; nilai = Some (string_of_float value); baris = l; kolom = c }
    }
  | n = NAMA
    {
      let (name, l, c) = n in
      Identitas { tipe = "NAMA"; nilai = Some name; baris = l; kolom = c }
    }
  | s = TEKS
    {
      let (str, l, c) = s in
      Konstanta { tipe = "TEKS"; nilai = Some str; baris = l; kolom = c }
    }
  | BENAR
    { Konstanta { tipe = "BENAR"; nilai = Some "true"; baris = 0; kolom = 0 } }
  | SALAH
    { Konstanta { tipe = "SALAH"; nilai = Some "false"; baris = 0; kolom = 0 } }
  | NIL
    { Konstanta { tipe = "NIL"; nilai = None; baris = 0; kolom = 0 } }
  | LPAREN e = expr RPAREN
    { e }
