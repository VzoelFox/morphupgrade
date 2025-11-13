open Ast

let location_to_json (loc: location) : Yojson.Basic.t =
  `Assoc [
    ("start_line", `Int loc.start_pos.line);
    ("start_col", `Int loc.start_pos.col);
    ("end_line", `Int loc.end_pos.line);
    ("end_col", `Int loc.end_pos.col);
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
    | Daftar elemen ->
      `Assoc [
        ("node_type", `String "daftar");
        ("elemen", `List (List.map expr_to_json elemen));
      ]
    | Kamus pasangan ->
      `Assoc [
        ("node_type", `String "kamus");
        ("pasangan", `List (List.map (fun (k, v) -> `Assoc [("kunci", expr_to_json k); ("nilai", expr_to_json v)]) pasangan));
      ]
    | Akses (objek, kunci) ->
      `Assoc [
        ("node_type", `String "akses");
        ("objek", expr_to_json objek);
        ("kunci", expr_to_json kunci);
      ]
    | AmbilProperti (objek, nama) ->
      `Assoc [
        ("node_type", `String "ambil_properti");
        ("objek", expr_to_json objek);
        ("nama", token_to_json nama);
      ]
    | AturProperti (objek, nama, nilai) ->
      `Assoc [
        ("node_type", `String "atur_properti");
        ("objek", expr_to_json objek);
        ("nama", token_to_json nama);
        ("nilai", expr_to_json nilai);
      ]
    | Ini token ->
      `Assoc [
        ("node_type", `String "ini");
        ("token", token_to_json token);
      ]
    | Induk token ->
        `Assoc [
            ("node_type", `String "induk");
            ("token", token_to_json token);
        ]
    | Tunggu (token, expr) ->
        `Assoc [
            ("node_type", `String "tunggu");
            ("token", token_to_json token);
            ("ekspresi", expr_to_json expr);
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
    | Kelas (nama, superkelas, metode) ->
      `Assoc [
        ("node_type", `String "kelas");
        ("nama", token_to_json nama);
        ("superkelas", match superkelas with None -> `Null | Some s -> expr_to_json s);
        ("metode", `List (List.map stmt_to_json metode));
      ]
    | TipeDeklarasi (nama, varian) ->
      `Assoc [
        ("node_type", `String "tipe_deklarasi");
        ("nama", token_to_json nama);
        ("varian", `List (List.map (fun (n, p) -> `Assoc [("nama", token_to_json n); ("parameter", `List (List.map token_to_json p))]) varian));
      ]
    | Jodohkan (target, kasus) ->
      `Assoc [
        ("node_type", `String "jodohkan");
        ("target", expr_to_json target);
        ("kasus", `List (List.map (fun (p, b, s) -> `Assoc [("pola", expr_to_json p); ("ikatan", `List (List.map token_to_json b)); ("badan", `List (List.map stmt_to_json s))]) kasus));
      ]
    | Pilih (target, kasus, lainnya) ->
        `Assoc [
            ("node_type", `String "pilih");
            ("target", expr_to_json target);
            ("kasus", `List (List.map (fun (v, s) -> `Assoc [("nilai", `List (List.map expr_to_json v)); ("badan", `List (List.map stmt_to_json s))]) kasus));
            ("lainnya", match lainnya with None -> `Null | Some s -> `List (List.map stmt_to_json s));
        ]
    | AmbilSemua (path, alias) ->
        `Assoc [
            ("node_type", `String "ambil_semua");
            ("path", token_to_json path);
            ("alias", match alias with None -> `Null | Some a -> token_to_json a);
        ]
    | AmbilSebagian (symbols, path) ->
        `Assoc [
            ("node_type", `String "ambil_sebagian");
            ("symbols", `List (List.map token_to_json symbols));
            ("path", token_to_json path);
        ]
    | Pinjam (path, alias) ->
        `Assoc [
            ("node_type", `String "pinjam");
            ("path", token_to_json path);
            ("alias", match alias with None -> `Null | Some a -> token_to_json a);
        ]
    | FungsiAsinkDeklarasi (nama, params, body) ->
        `Assoc [
            ("node_type", `String "fungsi_asink_deklarasi");
            ("nama", token_to_json nama);
            ("parameter", `List (List.map token_to_json params));
            ("badan", `List (List.map stmt_to_json body));
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
