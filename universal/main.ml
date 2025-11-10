let () =
  (* Periksa argumen baris perintah *)
  if Array.length Sys.argv <> 3 then
    (Printf.eprintf "Penggunaan: %s <file_input.fox> <file_output.json>\n" Sys.argv.(0);
     exit 1);

  let input_file = Sys.argv.(1) in
  let output_file = Sys.argv.(2) in

  (* Baca file input *)
  let in_channel = open_in input_file in
  let lexbuf = Lexing.from_channel in_channel in

  try
    (* Parse input untuk menghasilkan AST *)
    let ast = Parser.program Lexer.token lexbuf in
    close_in in_channel;

    (* Ubah AST menjadi JSON *)
    let json_ast = Ast_json.to_json ast in

    (* Tulis JSON ke file output *)
    let out_channel = open_out output_file in
    Yojson.Basic.to_channel out_channel json_ast;
    close_out out_channel;

    Printf.printf "Berhasil meng-compile %s ke %s\n" input_file output_file

  with
  | e ->
      close_in_noerr in_channel;
      let pos = lexbuf.lex_curr_p in
      Printf.eprintf "Error pada baris %d, kolom %d: %s\n"
        pos.pos_lnum
        (pos.pos_cnum - pos.pos_bol + 1)
        (Printexc.to_string e);
      exit 1
