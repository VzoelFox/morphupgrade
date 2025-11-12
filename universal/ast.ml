type ast_token = {
  tipe: string;
  nilai: string option;
  baris: int;
  kolom: int;
}

type expr =
  | Konstanta of ast_token
  | Identitas of ast_token
  | FoxBinary of expr * ast_token * expr
  | FoxUnary of ast_token * expr
  | PanggilFungsi of expr * ast_token * expr list

type stmt =
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
