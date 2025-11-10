(** Antarmuka publik untuk library morph_compiler. *)

(** Modul yang mendefinisikan tipe Abstract Syntax Tree (AST). *)
module Ast : module type of Ast

(** Modul Lexer yang dihasilkan oleh ocamllex. *)
module Lexer : module type of Lexer

(** Modul Parser yang dihasilkan oleh menhir. *)
module Parser : module type of Parser

(** Modul untuk serialisasi AST ke JSON. *)
module Ast_json : module type of Ast_json
