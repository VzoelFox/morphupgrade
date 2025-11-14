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
  | Daftar of expr list
  | Kamus of (expr * expr) list
  | Akses of expr * expr
  | AmbilProperti of expr * ast_token
  | AturProperti of expr * ast_token * expr
  | Ini of ast_token
  | Induk of ast_token
  | Tunggu of ast_token * expr

(* Pattern Matching *)
type pattern = {
  pdesc: pattern_desc;
  ploc: location;
}
and pattern_desc =
  | PolaLiteral of literal_value
  | PolaVarian of ast_token * pattern list (* Varian name and its pattern arguments *)
  | PolaWildcard
  | PolaIkatanVariabel of ast_token
  | PolaDaftar of pattern list * pattern option (* elements and optional rest pattern *)

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
  | Kelas of ast_token * expr option * stmt list
  | TipeDeklarasi of ast_token * (ast_token * ast_token list) list
  | Jodohkan of expr * (pattern * expr option * stmt list) list (* target * (pattern * guard * body) list *)
  | Pilih of expr * (expr list * stmt list) list * stmt list option
  | AmbilSemua of ast_token * ast_token option
  | AmbilSebagian of ast_token list * ast_token
  | Pinjam of ast_token * ast_token option
  | FungsiAsinkDeklarasi of ast_token * ast_token list * stmt list

type program = {
  body: stmt list;
}

(* Helper for dummy location *)
let dummy_pos = { line = -1; col = -1 }
let dummy_loc = { start_pos = dummy_pos; end_pos = dummy_pos }
