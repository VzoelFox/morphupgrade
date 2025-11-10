type token = {
  lexeme: string;
  line: int;
  col: int;
} [@@deriving show, yojson]

type expr =
  | Konstanta of token
  | Identitas of token
  | FoxBinary of expr * token * expr
  [@@deriving show, yojson]

type stmt =
  | DeklarasiVariabel of token * token * expr option (* keyword * name * initializer *)
  | Assignment of token * expr (* name * value *)
  [@@deriving show, yojson]

type bagian = {
  daftar_pernyataan: stmt list;
} [@@deriving show, yojson]
