(*
  Interface untuk serializer AST ke JSON.
*)

(** [program_to_json prog] mengkonversi AST [prog] menjadi representasi JSON. *)
val program_to_json : Ast.program -> Yojson.Basic.t

(** [to_json prog] mengkonversi AST [prog] menjadi representasi JSON. *)
val to_json : Ast.program -> Yojson.Basic.t
