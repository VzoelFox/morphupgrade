type position = {
  line: int;
  col: int;
}

type location = {
  start_pos: position;
  end_pos: position;
}

type ast_token = {
  tipe: string;
  nilai: string option;
  baris: int;
  kolom: int;
}

(* Literal values *)
type literal_value =
  | Angka of float
  | Teks of string
  | Benar
  | Salah
  | Nil

(* Expression *)
type expr = {
  edesc: expr_desc;
  eloc: location;
}
and expr_desc =
  | Konstanta of literal_value
  | Identitas of ast_token
  | FoxBinary of expr * ast_token * expr
  | FoxUnary of ast_token * expr
  | PanggilFungsi of expr * ast_token * expr list

(* Statement *)
type stmt = {
  sdesc: stmt_desc;
  sloc: location;
}
and stmt_desc =
  | DeklarasiVariabel of ast_token * ast_token * expr option
  | Assignment of ast_token * expr
  | Tulis of expr list
  | PernyataanEkspresi of expr
  | JikaMaka of expr * stmt list * (expr * stmt list) list * stmt list option
  | Selama of ast_token * expr * stmt list
  | FungsiDeklarasi of ast_token * ast_token list * stmt list
  | PernyataanKembalikan of ast_token * expr option

type program = {
  body: stmt list;
}

(* Helper for dummy location *)
let dummy_pos = { line = -1; col = -1 }
let dummy_loc = { start_pos = dummy_pos; end_pos = dummy_pos }
