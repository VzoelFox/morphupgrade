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
  | "ambil_semua"    { let line, col = get_lexing_position lexbuf in AMBIL_SEMUA (line, col) }
  | "ambil_sebagian" { let line, col = get_lexing_position lexbuf in AMBIL_SEBAGIAN (line, col) }
  | "jika"      { let line, col = get_lexing_position lexbuf in JIKA (line, col) }
  | "maka"      { let line, col = get_lexing_position lexbuf in MAKA (line, col) }
  | "lain"      { let line, col = get_lexing_position lexbuf in LAIN (line, col) }
  | "akhir"     { let line, col = get_lexing_position lexbuf in AKHIR (line, col) }
  | "selama"    { let line, col = get_lexing_position lexbuf in SELAMA (line, col) }
  | "fungsi"    { let line, col = get_lexing_position lexbuf in FUNGSI (line, col) }
  | "kelas"     { let line, col = get_lexing_position lexbuf in KELAS (line, col) }
  | "warisi"    { let line, col = get_lexing_position lexbuf in WARISI (line, col) }
  | "ini"       { let line, col = get_lexing_position lexbuf in INI (line, col) }
  | "induk"     { let line, col = get_lexing_position lexbuf in INDUK (line, col) }
  | "kembali"   { let line, col = get_lexing_position lexbuf in KEMBALI (line, col) }
  | "asink"     { let line, col = get_lexing_position lexbuf in ASINK (line, col) }
  | "tunggu"    { let line, col = get_lexing_position lexbuf in TUNGGU (line, col) }
  | "tipe"      { let line, col = get_lexing_position lexbuf in TIPE (line, col) }
  | "jodohkan"  { let line, col = get_lexing_position lexbuf in JODOHKAN (line, col) }
  | "dengan"    { let line, col = get_lexing_position lexbuf in DENGAN (line, col) }
  | "pinjam"    { let line, col = get_lexing_position lexbuf in PINJAM (line, col) }
  | "dari"      { let line, col = get_lexing_position lexbuf in DARI (line, col) }
  | "sebagai"   { let line, col = get_lexing_position lexbuf in SEBAGAI (line, col) }
  | "biar"      { let line, col = get_lexing_position lexbuf in BIAR (line, col) }
  | "tetap"     { let line, col = get_lexing_position lexbuf in TETAP (line, col) }
  | "ubah"      { let line, col = get_lexing_position lexbuf in UBAH (line, col) }
  | "tulis"     { let line, col = get_lexing_position lexbuf in TULIS (line, col) }
  | "ambil"     { let line, col = get_lexing_position lexbuf in AMBIL (line, col) }
  | "benar"     { let line, col = get_lexing_position lexbuf in BENAR (line, col) }
  | "salah"     { let line, col = get_lexing_position lexbuf in SALAH (line, col) }
  | "nil"       { let line, col = get_lexing_position lexbuf in NIL (line, col) }
  | "dan"       { let line, col = get_lexing_position lexbuf in DAN (line, col) }
  | "atau"      { let line, col = get_lexing_position lexbuf in ATAU (line, col) }
  | "tidak"     { let line, col = get_lexing_position lexbuf in TIDAK (line, col) }
  | "ketika"    { let line, col = get_lexing_position lexbuf in KETIKA (line, col) }
  | "lainnya"   { let line, col = get_lexing_position lexbuf in LAINNYA (line, col) }
  | "pilih"     { let line, col = get_lexing_position lexbuf in PILIH (line, col) }

  (* Operators - Two-char operators BEFORE single-char *)
  | "..."       { let line, col = get_lexing_position lexbuf in TITIK_TIGA (line, col) }
  | "=="        { let line, col = get_lexing_position lexbuf in SAMA_DENGAN (line, col) }
  | "!="        { let line, col = get_lexing_position lexbuf in TIDAK_SAMA (line, col) }
  | "<="        { let line, col = get_lexing_position lexbuf in KURANG_SAMA (line, col) }
  | ">="        { let line, col = get_lexing_position lexbuf in LEBIH_SAMA (line, col) }
  | "="         { let line, col = get_lexing_position lexbuf in EQUAL (line, col) }
  | "+"         { let line, col = get_lexing_position lexbuf in PLUS (line, col) }
  | "-"         { let line, col = get_lexing_position lexbuf in MINUS (line, col) }
  | "*"         { let line, col = get_lexing_position lexbuf in BINTANG (line, col) }
  | "/"         { let line, col = get_lexing_position lexbuf in GARIS_MIRING (line, col) }
  | "^"         { let line, col = get_lexing_position lexbuf in PANGKAT (line, col) }
  | "%"         { let line, col = get_lexing_position lexbuf in PERSEN (line, col) }
  | "<"         { let line, col = get_lexing_position lexbuf in KURANG_DARI (line, col) }
  | ">"         { let line, col = get_lexing_position lexbuf in LEBIH_DARI (line, col) }
  | "!"         { let line, col = get_lexing_position lexbuf in TIDAK (line, col) }

  (* Delimiters *)
  | "("         { let line, col = get_lexing_position lexbuf in LPAREN (line, col) }
  | ")"         { let line, col = get_lexing_position lexbuf in RPAREN (line, col) }
  | "["         { let line, col = get_lexing_position lexbuf in LBRACKET (line, col) }
  | "]"         { let line, col = get_lexing_position lexbuf in RBRACKET (line, col) }
  | "{"         { let line, col = get_lexing_position lexbuf in LBRACE (line, col) }
  | "}"         { let line, col = get_lexing_position lexbuf in RBRACE (line, col) }
  | ","         { let line, col = get_lexing_position lexbuf in KOMA (line, col) }
  | "."         { let line, col = get_lexing_position lexbuf in DOT (line, col) }
  | ":"         { let line, col = get_lexing_position lexbuf in COLON (line, col) }
  | ";"         { let line, col = get_lexing_position lexbuf in SEMICOLON (line, col) }
  | "|"         { let line, col = get_lexing_position lexbuf in PIPE (line, col) }

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
