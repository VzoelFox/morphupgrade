(*
  File ini mendefinisikan tipe data untuk Abstract Syntax Tree (AST).
*)

(* Tipe enumerasi untuk *jenis* token. Didefinisikan di sini untuk
   digunakan oleh ast_token dan serializer. *)
type token_type =
  | BIAR | UBAH
  | PLUS | MINUS | BINTANG | GARIS_MIRING | PANGKAT | PERSEN
  | SAMA_DENGAN
  | TULIS
  | LITERAL_ANGKA | IDENTIFIER
  | LPAREN | RPAREN | KOMA
  | EOF

(* Tipe untuk nilai-nilai literal yang sebenarnya di dalam program MORPH *)
type value =
  | VAngka of float
  | VTeks of string
  | VKosong

(*
  Record untuk token di level AST. Namanya `ast_token` untuk menghindari
  konflik dengan tipe `token` internal yang dibuat oleh Menhir.
*)
type ast_token = {
  tipe: token_type;
  nilai: value;
  literal: string; (* Teks asli dari source *)
  baris: int;
  kolom: int;
}

(* Tipe-tipe untuk node Expression (Ekspresi) di dalam AST *)
type expr =
  | Konstanta of ast_token
  | Identitas of ast_token
  | FoxBinary of expr * ast_token * expr
  | PanggilFungsi of expr * expr list (* callee * argumen *)

(* Tipe-tipe untuk node Statement (Pernyataan) di dalam AST *)
type stmt =
  | DeklarasiVariabel of ast_token * ast_token * expr option (* keyword * nama * nilai *)
  | Assignment of ast_token * expr (* nama * nilai *)
  | Tulis of expr list
  | PernyataanEkspresi of expr

(* Tipe untuk node root dari AST, merepresentasikan seluruh program *)
type program = {
  daftar_pernyataan: stmt list;
}
