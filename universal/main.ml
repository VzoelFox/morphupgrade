let () =
  if Array.length Sys.argv < 3 then (
    Printf.eprintf "Usage: %s <input_file> <output_file>\n" Sys.argv.(0);
    exit 1
  );

  let filename = Sys.argv.(1) in
  let outname = Sys.argv.(2) in
  let ic = open_in filename in
  let lexbuf = Lexing.from_channel ic in

  (* Set lexbuf filename for better error messages *)
  lexbuf.Lexing.lex_curr_p <- {
    lexbuf.Lexing.lex_curr_p with
    Lexing.pos_fname = filename
  };

  try
    let ast = Parser.program Lexer.token lexbuf in
    close_in ic;

    Printf.eprintf "=== PARSER SUCCESS ===\n";
    let json = Ast_json.to_json ast in
    let oc = open_out outname in
    Yojson.Basic.pretty_to_channel oc json;
    close_out oc

  with
  | Lexer.LexError msg ->
      Printf.eprintf "Lexer error: %s\n" msg;
      close_in ic;
      exit 1
  | Parser.Error ->
      let pos = lexbuf.Lexing.lex_curr_p in
      Printf.eprintf "Parse error at line %d, column %d\n"
        pos.Lexing.pos_lnum
        (pos.Lexing.pos_cnum - pos.Lexing.pos_bol);
      close_in ic;
      exit 1
  | e ->
      Printf.eprintf "Unexpected error: %s\n" (Printexc.to_string e);
      close_in ic;
      exit 1
