(* universal/ast_json.ml *)
open Ast

let token_to_json token =
  (* Parse nilai to determine correct JSON type *)
  let nilai_json = match token.nilai with
    | None -> `Null
    | Some v ->
      (* Try integer first *)
      (try
        let i = int_of_string v in
        `Int i
      with Failure _ ->
        (* Try float *)
        (try
          let f = float_of_string v in
          `Float f
        with Failure _ ->
          (* Default to string *)
          `String v
        )
      )
  in
  `Assoc [
    ("tipe", `String token.tipe);
    ("nilai", nilai_json);
    ("baris", `Int token.baris);
    ("kolom", `Int token.kolom);
  ]

let rec expr_to_json = function
  | Konstanta token ->
    `Assoc [
      ("node_type", `String "Konstanta");
      ("token", token_to_json token);
    ]

  | Identitas token ->
    `Assoc [
      ("node_type", `String "Identitas");
      ("token", token_to_json token);
    ]

  | FoxBinary (left, op, right) ->
    `Assoc [
      ("node_type", `String "FoxBinary");
      ("kiri", expr_to_json left);
      ("operator", token_to_json op);
      ("kanan", expr_to_json right);
    ]

  | FoxUnary (op, operand) ->
    `Assoc [
      ("node_type", `String "FoxUnary");
      ("operator", token_to_json op);
      ("kanan", expr_to_json operand);
    ]

  | PanggilFungsi (callee, token, args) ->
    `Assoc [
      ("node_type", `String "PanggilFungsi");
      ("callee", expr_to_json callee);
      ("token", token_to_json token);
      ("argumen", `List (List.map expr_to_json args));
    ]

let rec stmt_to_json = function
  | DeklarasiVariabel (keyword, name, init) ->
    `Assoc [
      ("node_type", `String "DeklarasiVariabel");
      ("jenis_deklarasi", token_to_json keyword);
      ("nama", token_to_json name);
      ("nilai", match init with
        | None -> `Null
        | Some e -> expr_to_json e
      );
    ]

  | Assignment (name, value) ->
    `Assoc [
      ("node_type", `String "Assignment");
      ("nama", token_to_json name);
      ("nilai", expr_to_json value);
    ]

  | Tulis args ->
    `Assoc [
      ("node_type", `String "Tulis");
      ("argumen", `List (List.map expr_to_json args));
    ]

  | PernyataanEkspresi e ->
    `Assoc [
      ("node_type", `String "PernyataanEkspresi");
      ("ekspresi", expr_to_json e);
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

  | JikaMaka (cond, then_body, elif_chain, else_body) ->
    `Assoc [
      ("node_type", `String "JikaMaka");
      ("kondisi", expr_to_json cond);
      ("blok_maka", `List (List.map stmt_to_json then_body));
      ("rantai_lain_jika", `List (List.map (fun (c, b) ->
        `Assoc [
          ("kondisi", expr_to_json c);
          ("blok", `List (List.map stmt_to_json b));
        ]
      ) elif_chain));
      ("blok_lain", match else_body with
        | None -> `Null
        | Some stmts -> `List (List.map stmt_to_json stmts)
      );
    ]

  | Selama (token, cond, body) ->
    `Assoc [
      ("node_type", `String "Selama");
      ("token", token_to_json token);
      ("kondisi", expr_to_json cond);
      ("badan", `List (List.map stmt_to_json body));
    ]

  | FungsiDeklarasi (name, params, body) ->
    `Assoc [
      ("node_type", `String "FungsiDeklarasi");
      ("nama", token_to_json name);
      ("parameter", `List (List.map token_to_json params));
      ("badan", `List (List.map stmt_to_json body));
    ]

  | PernyataanKembalikan (keyword, value) ->
    `Assoc [
      ("node_type", `String "PernyataanKembalikan");
      ("kata_kunci", token_to_json keyword);
      ("nilai", match value with
        | None -> `Null
        | Some e -> expr_to_json e
      );
    ]

let program_to_json prog =
  `Assoc [
    ("ast", `Assoc [
      ("body", `List (List.map stmt_to_json prog.body));
    ]);
  ]

let to_json = program_to_json
