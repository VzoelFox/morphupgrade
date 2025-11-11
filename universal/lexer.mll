{
open Parser  (* Menggunakan tipe token yang dibuat oleh Menhir *)
open Lexing

}

rule token = parse
  | [' ' '\t'] +   { token lexbuf }
  | '\n'           { new_line lexbuf; token lexbuf }
  | '('            { LPAREN }
  | ')'            { RPAREN }
  | ','            { KOMA }
  | ':'            { COLON }
  | '['            { LBRACKET }
  | ']'            { RBRACKET }
  | '{'            { LBRACE }
  | '}'            { RBRACE }
  | '.'            { DOT }
  | '|'            { PIPE }
  | ['0'-'9']+ as n { LITERAL_ANGKA n }
  | '+'            { PLUS }
  | '-'            { MINUS }
  | '*'            { BINTANG }
  | '/'            { GARIS_MIRING }
  | '^'            { PANGKAT }
  | '%'            { PERSEN }
  | '='            { SAMA_DENGAN }
  | "jika"         { JIKA }
  | "maka"         { MAKA }
  | "lain"         { LAIN }
  | "akhir"        { AKHIR }
  | "selama"       { SELAMA }
  | "fungsi"       { FUNGSI }
  | "kelas"        { KELAS }
  | "warisi"       { WARISI }
  | "ini"          { INI }
  | "induk"        { INDUK }
  | "kembali"      { KEMBALI }
  | "asink"        { ASINK }
  | "tunggu"       { TUNGGU }
  | "tipe"         { TIPE }
  | "jodohkan"     { JODOHKAN }
  | "dengan"       { DENGAN }
  | "pinjam"       { PINJAM }
  | "ambil_semua"  { AMBIL_SEMUA }
  | "ambil_sebagian" { AMBIL_SEBAGIAN }
  | "dari"         { DARI }
  | "sebagai"      { SEBAGAI }
  | "biar"         { BIAR }
  | "ubah"         { UBAH }
  | "tulis"        { TULIS }
  | ['a'-'z' 'A'-'Z' '_'] ['a'-'z' 'A'-'Z' '0'-'9' '_']* as id { IDENTIFIER id }
  | eof            { EOF }
