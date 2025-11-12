{
open Parser

exception LexError of string

let get_lexing_position lexbuf =
  let pos = Lexing.lexeme_start_p lexbuf in
  (pos.Lexing.pos_lnum, pos.Lexing.pos_cnum - pos.Lexing.pos_bol + 1)
}

(* Regex Definitions *)
let whitespace = [' ' '\t' '\r']
let newline = '\n'
let digit = ['0'-'9']
let alpha = ['a'-'z' 'A'-'Z' '_']
let alphanum = alpha | digit

(* Main tokenizer rule *)
rule token = parse
  (* CRITICAL: Handle whitespace WITHOUT newline *)
  | whitespace+     { token lexbuf }

  (* CRITICAL: Handle newline SEPARATELY and return token *)
  | newline         { Lexing.new_line lexbuf; NEWLINE }

  (* Comments - consume until newline but DON'T consume newline itself *)
  | "//" [^ '\n']*  { token lexbuf }
  | '#' [^ '\n']*   { token lexbuf }

  (* Keywords - ORDER MATTERS! Longest first *)
  | "ambil_semua"    { AMBIL_SEMUA }
  | "ambil_sebagian" { AMBIL_SEBAGIAN }
  | "jika"      { JIKA }
  | "maka"      { MAKA }
  | "lain"      { LAIN }
  | "akhir"     { AKHIR }
  | "selama"    { SELAMA }
  | "fungsi"    { FUNGSI }
  | "kelas"     { KELAS }
  | "warisi"    { WARISI }
  | "ini"       { INI }
  | "induk"     { INDUK }
  | "kembali"   { KEMBALI }
  | "asink"     { ASINK }
  | "tunggu"    { TUNGGU }
  | "tipe"      { TIPE }
  | "jodohkan"  { JODOHKAN }
  | "dengan"    { DENGAN }
  | "pinjam"    { PINJAM }
  | "dari"      { DARI }
  | "sebagai"   { SEBAGAI }
  | "biar"      { BIAR }
  | "tetap"     { TETAP }
  | "ubah"      { UBAH }
  | "tulis"     { TULIS }
  | "ambil"     { AMBIL }
  | "benar"     { BENAR }
  | "salah"     { SALAH }
  | "nil"       { NIL }
  | "dan"       { DAN }
  | "atau"      { ATAU }
  | "tidak"     { TIDAK }
  | "ketika"    { KETIKA }
  | "lainnya"   { LAINNYA }
  | "pilih"     { PILIH }

  (* Operators - Two-char operators BEFORE single-char *)
  | "=="        { SAMA_DENGAN }
  | "!="        { TIDAK_SAMA }
  | "<="        { KURANG_SAMA }
  | ">="        { LEBIH_SAMA }
  | "="         { EQUAL }
  | "+"         { PLUS }
  | "-"         { MINUS }
  | "*"         { BINTANG }
  | "/"         { GARIS_MIRING }
  | "^"         { PANGKAT }
  | "%"         { PERSEN }
  | "<"         { KURANG_DARI }
  | ">"         { LEBIH_DARI }
  | "!"         { TIDAK }

  (* Delimiters *)
  | "("         { LPAREN }
  | ")"         { RPAREN }
  | "["         { LBRACKET }
  | "]"         { RBRACKET }
  | "{"         { LBRACE }
  | "}"         { RBRACE }
  | ","         { KOMA }
  | "."         { DOT }
  | ":"         { COLON }
  | ";"         { SEMICOLON }
  | "|"         { PIPE }

  (* String literals *)
  | '"'         { read_string (Buffer.create 16) lexbuf }

  (* Numbers *)
  | digit+ ('.' digit+)? as num
    {
      let line, col = get_lexing_position lexbuf in
      let value = float_of_string num in
      ANGKA (value, line, col)
    }

  (* Identifiers *)
  | alpha alphanum* as id
    {
      let line, col = get_lexing_position lexbuf in
      NAMA (id, line, col)
    }

  (* End of file *)
  | eof         { EOF }

  (* ERROR CASE - CRITICAL: Must be LAST *)
  | _ as c
    {
      let line, col = get_lexing_position lexbuf in
      let msg = Printf.sprintf "Unexpected character '%c' at line %d, column %d" c line col in
      raise (LexError msg)
    }

(* String literal handler *)
and read_string buf = parse
  | '"'
    {
      let line, col = get_lexing_position lexbuf in
      TEKS (Buffer.contents buf, line, col)
    }
  | '\\' 'n'      { Buffer.add_char buf '\n'; read_string buf lexbuf }
  | '\\' 't'      { Buffer.add_char buf '\t'; read_string buf lexbuf }
  | '\\' '"'      { Buffer.add_char buf '"'; read_string buf lexbuf }
  | '\\' '\\'     { Buffer.add_char buf '\\'; read_string buf lexbuf }
  | newline       { Lexing.new_line lexbuf; Buffer.add_char buf '\n'; read_string buf lexbuf }
  | eof           { raise (LexError "Unterminated string") }
  | _ as c        { Buffer.add_char buf c; read_string buf lexbuf }
