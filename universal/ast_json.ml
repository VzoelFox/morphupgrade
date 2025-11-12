open Ast

let token_to_json (t: ast_token) : Yojson.Basic.t =
  `Assoc (
    [
      ("tipe", `String t.tipe);
      ("baris", `Int t.baris);
      ("kolom", `Int t.kolom);
    ] @
    (match t.nilai with
     | Some v -> [("nilai", `String v)]
     | None -> [])
  )

let rec expr_to_json (e: expr) : Yojson.Basic.t =
  match e with
  | Konstanta token ->
    `Assoc [
      ("node_type", `String "Konstanta");
      ("token", token_to_json token)
    ]
  | Identitas token ->
    `Assoc [
      ("node_type", `String "Identitas");
      ("token", token_to_json token)
    ]
  | FoxBinary (kiri, op, kanan) ->
    `Assoc [
      ("node_type", `String "FoxBinary");
      ("kiri", expr_to_json kiri);
      ("operator", token_to_json op);
      ("kanan", expr_to_json kanan)
    ]
  | FoxUnary (op, kanan) ->
    `Assoc [
      ("node_type", `String "FoxUnary");
      ("operator", token_to_json op);
      ("kanan", expr_to_json kanan)
    ]
  | PanggilFungsi (callee, token, args) ->
    `Assoc [
      ("node_type", `String "PanggilFungsi");
      ("callee", expr_to_json callee);
      ("token", token_to_json token);
      ("argumen", `List (List.map expr_to_json args))
    ]

and stmt_to_json (s: stmt) : Yojson.Basic.t =
  match s with
  | DeklarasiVariabel (kw, nama, nilai_opt) ->
    `Assoc [
      ("node_type", `String "DeklarasiVariabel");
      ("jenis_deklarasi", token_to_json kw);
      ("nama", token_to_json nama);
      ("nilai", match nilai_opt with Some e -> expr_to_json e | None -> `Null)
    ]
  | Assignment (nama, nilai) ->
    `Assoc [
      ("node_type", `String "Assignment");
      ("nama", token_to_json nama);
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
  | JikaMaka(cond, then_b, elif_chain, else_b) ->
    `Assoc [
      ("node_type", `String "JikaMaka");
      ("kondisi", expr_to_json cond);
      ("blok_maka", `List (List.map stmt_to_json then_b));
      ("rantai_lain_jika", `List (List.map (fun (c, b) -> `Assoc [("kondisi", expr_to_json c); ("blok", `List (List.map stmt_to_json b))]) elif_chain));
      ("blok_lain", match else_b with Some b -> `List (List.map stmt_to_json b) | None -> `Null)
    ]
  | Selama(token, cond, body) ->
    `Assoc [
      ("node_type", `String "Selama");
      ("token", token_to_json token);
      ("kondisi", expr_to_json cond);
      ("badan", `List (List.map stmt_to_json body))
    ]
  | FungsiDeklarasi(name, params, body) ->
    `Assoc [
      ("node_type", `String "FungsiDeklarasi");
      ("nama", token_to_json name);
      ("parameter", `List (List.map token_to_json params));
      ("badan", `List (List.map stmt_to_json body))
    ]
  | PernyataanKembalikan(kw, value) ->
    `Assoc [
      ("node_type", `String "PernyataanKembalikan");
      ("kata_kunci", token_to_json kw);
      ("nilai", match value with Some e -> expr_to_json e | None -> `Null)
    ]

let program_to_json (p: program) : Yojson.Basic.t =
  `Assoc [
    ("body", `List (List.map stmt_to_json p.body))
  ]

let to_json (prog: program) : Yojson.Basic.t =
  `Assoc [
    ("ast", program_to_json prog)
  ]
