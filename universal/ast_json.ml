open Ast

let to_json (bagian: bagian) : Yojson.Basic.t =
  Yojson.Safe.to_basic (bagian_to_yojson bagian)
