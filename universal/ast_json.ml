open Ast

(* Konversi token_tipe enum ke string sesuai spesifikasi *)
let token_tipe_to_string = function
  | BIAR -> "BIAR" | UBAH -> "UBAH"
  | PLUS -> "PLUS" | MINUS -> "MINUS" | BINTANG -> "BINTANG" | GARIS_MIRING -> "GARIS_MIRING"
  | PANGKAT -> "PANGKAT" | PERSEN -> "PERSEN" | SAMA_DENGAN -> "SAMA_DENGAN"
  | TULIS -> "TULIS"
  | LITERAL_ANGKA -> "ANGKA" | IDENTIFIER -> "NAMA"
  | LPAREN -> "LPAREN" | RPAREN -> "RPAREN" | KOMA -> "KOMA" | EOF -> "EOF"

(* Serialisasi nilai token *)
let value_to_json = function
  | VAngka f -> `Float f
  | VTeks s -> `String s
  | VKosong -> `Null

(* Serialisasi token menjadi JSON *)
let ast_token_to_json (t: ast_token) : Yojson.Basic.t =
  `Assoc [
    ("tipe", `String (token_tipe_to_string t.tipe));
    ("nilai", value_to_json t.nilai);
    ("baris", `Int t.baris);
    ("kolom", `Int t.kolom)
  ]

(* Forward declaration untuk fungsi rekursif *)
let rec expr_to_json (e: expr) : Yojson.Basic.t =
  match e with
  | Konstanta token ->
    `Assoc [
      ("node_type", `String "Konstanta");
      ("token", ast_token_to_json token);
      ("nilai", value_to_json token.nilai)
    ]
  | Identitas t ->
    `Assoc [
      ("node_type", `String "Identitas");
      ("token", ast_token_to_json t)
    ]
  | FoxBinary (kiri, op, kanan) ->
    `Assoc [
      ("node_type", `String "FoxBinary");
      ("kiri", expr_to_json kiri);
      ("operator", ast_token_to_json op);
      ("kanan", expr_to_json kanan)
    ]
  | PanggilFungsi (callee, args) ->
    `Assoc [
      ("node_type", `String "PanggilFungsi");
      ("callee", expr_to_json callee);
      ("argumen", `List (List.map expr_to_json args))
    ]

and stmt_to_json (s: stmt) : Yojson.Basic.t =
  match s with
  | DeklarasiVariabel (kw, nama, nilai_opt) ->
    let nilai_json =
      match nilai_opt with
      | Some expr -> expr_to_json expr
      | None -> `Null
    in
    `Assoc [
      ("node_type", `String "DeklarasiVariabel");
      ("jenis_deklarasi", ast_token_to_json kw);
      ("nama", ast_token_to_json nama);
      ("nilai", nilai_json)
    ]
  | Assignment (nama, nilai) ->
    `Assoc [
      ("node_type", `String "Assignment");
      ("nama", ast_token_to_json nama);
      ("nilai", expr_to_json nilai)
    ]
  | Tulis args ->
    `Assoc [
      ("node_type", `String "Tulis");
      ("argumen", `List (List.map expr_to_json args))
    ]
  | PernyataanEkspresi expr ->
    `Assoc [
      ("node_type", `String "PernyataanEkspresi");
      ("ekspresi", expr_to_json expr)
    ]

(* Serialisasi program menjadi JSON *)
let program_to_json (p: program) : Yojson.Basic.t =
  `Assoc [
    ("node_type", `String "Program");
    ("body", `List (List.map stmt_to_json p.daftar_pernyataan))
  ]

(* Fungsi utama untuk membuat amplop JSON lengkap *)
let to_json (prog: program) : Yojson.Basic.t =
  `Assoc [
    ("format_version", `String "1.0");
    ("compiler_version", `String "0.1.0"); (* Placeholder version *)
    ("status", `String "success");
    ("ast", program_to_json prog);
    ("errors", `Null)
  ]
