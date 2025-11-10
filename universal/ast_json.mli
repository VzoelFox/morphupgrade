(**
 * Serializer untuk mengubah AST menjadi format JSON.
 *)

(** [to_json ast] mengubah AST [ast] dari tipe [Ast.bagian] menjadi objek Yojson. *)
val to_json : Ast.bagian -> Yojson.Basic.t
