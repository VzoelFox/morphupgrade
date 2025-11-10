{
open Parser
open Lexing

}

rule token = parse
  | [' ' '\t'] +   { token lexbuf }
  | '\n'           { new_line lexbuf; token lexbuf }
  | '('            { LPAREN }
  | ')'            { RPAREN }
  | ['0'-'9']+ as n { LITERAL_ANGKA n }
  | '+'            { PLUS }
  | '-'            { MINUS }
  | '*'            { BINTANG }
  | '/'            { GARIS_MIRING }
  | '^'            { PANGKAT }
  | '%'            { PERSEN }
  | '='            { SAMA_DENGAN }
  | "biar"         { BIAR }
  | "ubah"         { UBAH }
  | ['a'-'z' 'A'-'Z' '_'] ['a'-'z' 'A'-'Z' '0'-'9' '_']* as id { IDENTIFIER id }
  | eof            { EOF }
