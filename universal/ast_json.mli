(*
  Interface untuk serializer AST ke JSON.
*)

(** [to_json prog] mengkonversi AST [prog] menjadi representasi JSON. *)
val to_json : Ast.program -> Yojson.Basic.t
