open Ast

let position_to_json pos =
  `Assoc [
    ("baris", `Int pos.line);
    ("kolom", `Int pos.col);
  ]

let location_to_json loc =
  `Assoc [
    ("mulai", position_to_json loc.start_pos);
    ("akhir", position_to_json loc.end_pos);
  ]

let token_to_json token =
  let nilai_json = match token.nilai with
    | None -> `Null
    | Some v -> `String v
  in
  `Assoc [
    ("tipe", `String token.tipe);
    ("nilai", nilai_json);
    ("baris", `Int token.baris);
    ("kolom", `Int token.kolom);
  ]

let literal_to_json = function
  | Angka f -> `Assoc [("tipe", `String "angka"); ("nilai", `Float f)]
  | Teks s -> `Assoc [("tipe", `String "teks"); ("nilai", `String s)]
  | Benar -> `Assoc [("tipe", `String "boolean"); ("nilai", `Bool true)]
  | Salah -> `Assoc [("tipe", `String "boolean"); ("nilai", `Bool false)]
  | Nil -> `Assoc [("tipe", `String "nil"); ("nilai", `Null)]

let rec expr_to_json e =
  let desc_json = match e.edesc with
    | Konstanta lit ->
      `Assoc [
        ("node_type", `String "konstanta");
        ("literal", literal_to_json lit);
      ]
    | Identitas token ->
      `Assoc [
        ("node_type", `String "identitas");
        ("token", token_to_json token);
      ]
    | FoxBinary (left, op, right) ->
      `Assoc [
        ("node_type", `String "fox_binary");
        ("kiri", expr_to_json left);
        ("operator", token_to_json op);
        ("kanan", expr_to_json right);
      ]
    | FoxUnary (op, operand) ->
      `Assoc [
        ("node_type", `String "fox_unary");
        ("operator", token_to_json op);
        ("kanan", expr_to_json operand);
      ]
    | PanggilFungsi (callee, token, args) ->
      `Assoc [
        ("node_type", `String "panggil_fungsi");
        ("callee", expr_to_json callee);
        ("token", token_to_json token);
        ("argumen", `List (List.map expr_to_json args));
      ]
  in
  `Assoc [
    ("deskripsi", desc_json);
    ("lokasi", location_to_json e.eloc);
  ]

let rec stmt_to_json s =
  let desc_json = match s.sdesc with
    | DeklarasiVariabel (keyword, name, init) ->
      `Assoc [
        ("node_type", `String "deklarasi_variabel");
        ("jenis_deklarasi", token_to_json keyword);
        ("nama", token_to_json name);
        ("nilai", match init with None -> `Null | Some e -> expr_to_json e);
      ]
    | Assignment (name, value) ->
      `Assoc [
        ("node_type", `String "assignment");
        ("nama", token_to_json name);
        ("nilai", expr_to_json value);
      ]
    | Tulis args ->
      `Assoc [
        ("node_type", `String "tulis");
        ("argumen", `List (List.map expr_to_json args));
      ]
    | PernyataanEkspresi e ->
      `Assoc [
        ("node_type", `String "pernyataan_ekspresi");
        ("ekspresi", expr_to_json e);
      ]
    | JikaMaka(cond, then_b, elif_chain, else_b) ->
      `Assoc [
        ("node_type", `String "jika_maka");
        ("kondisi", expr_to_json cond);
        ("blok_maka", `List (List.map stmt_to_json then_b));
        ("rantai_lain_jika", `List (List.map (fun (c, b) -> `Assoc [("kondisi", expr_to_json c); ("blok", `List (List.map stmt_to_json b))]) elif_chain));
        ("blok_lain", match else_b with Some b -> `List (List.map stmt_to_json b) | None -> `Null)
      ]
    | Selama(token, cond, body) ->
      `Assoc [
        ("node_type", `String "selama");
        ("token", token_to_json token);
        ("kondisi", expr_to_json cond);
        ("badan", `List (List.map stmt_to_json body))
      ]
    | FungsiDeklarasi(name, params, body) ->
      `Assoc [
        ("node_type", `String "fungsi_deklarasi");
        ("nama", token_to_json name);
        ("parameter", `List (List.map token_to_json params));
        ("badan", `List (List.map stmt_to_json body))
      ]
    | PernyataanKembalikan(kw, value) ->
      `Assoc [
        ("node_type", `String "pernyataan_kembalikan");
        ("kata_kunci", token_to_json kw);
        ("nilai", match value with Some e -> expr_to_json e | None -> `Null)
      ]
  in
  `Assoc [
    ("deskripsi", desc_json);
    ("lokasi", location_to_json s.sloc);
  ]

let program_to_json prog =
  `Assoc [
    ("version", `String "0.1.0");
    ("program", `Assoc [
      ("body", `List (List.map stmt_to_json prog.body));
    ]);
  ]

let to_json = program_to_json
