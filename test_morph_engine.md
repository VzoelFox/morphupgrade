# Rekapitulasi Rangkaian Tes untuk Morph Engine

Dokumen ini menyediakan ringkasan dari semua tes yang ada untuk `morph_engine`. Tujuannya adalah untuk memberikan gambaran umum tentang cakupan tes saat ini dan sebagai referensi cepat untuk pengembangan di masa depan.

---

## `tests/test_arrays.py`

File ini adalah kerangka untuk tes yang berkaitan dengan fitur array.
*(Belum ada tes yang diimplementasikan)*

---

## `tests/test_closures.py`

File ini adalah kerangka untuk tes yang berkaitan dengan fitur closures.
*(Belum ada tes yang diimplementasikan)*

---

## `tests/test_errors.py`

File ini adalah kerangka untuk tes yang berkaitan dengan penanganan kesalahan (error handling).
*(Belum ada tes yang diimplementasikan)*

---

## `tests/test_ffi.py`

Tes untuk Foreign Function Interface (FFI) yang memungkinkan MORPH berinteraksi dengan kode Python.

- `test_ffi_load_module_and_access_variable`: Menguji pemuatan modul Python dan akses variabel.
- `test_ffi_call_simple_function`: Menguji pemanggilan fungsi Python sederhana.
- `test_ffi_complex_type_conversion`: Menguji konversi tipe data kompleks seperti list dan dictionary.
- `test_ffi_unsupported_return_type_is_wrapped`: Memastikan tipe data Python yang tidak didukung dibungkus dengan benar.
- `test_ffi_python_exception_handling`: Memastikan eksepsi dari Python ditangkap sebagai `KesalahanRuntime`.
- `test_ffi_class_instantiation_and_method_call`: Menguji pembuatan instance kelas Python dan pemanggilan metodenya.
- `test_ffi_write_assignment`: Menguji penulisan kembali nilai ke properti objek Python.
- `test_ffi_nested_data_conversion`: Menguji konversi tipe data bersarang.
- `test_ffi_better_object_representation`: Memastikan objek FFI memiliki representasi teks yang informatif.

---

## `tests/test_integration.py`

Tes integrasi end-to-end yang menjalankan program `.fox` secara lengkap.

- `test_complex_program_with_functions`: Menguji program kompleks yang menggunakan fungsi, rekursi, dan pemanggilan bersarang.
- `test_while_loop_integration`: Menguji fungsionalitas perulangan `selama`.
- `test_dictionary_integration`: Menguji fungsionalitas kamus (dictionary), termasuk pembuatan, akses, dan assignment.
- `test_pilih_statement_integration`: Menguji fungsionalitas struktur kontrol `pilih` (switch/match).

---

## `tests/test_leksikal.py`

Tes unit untuk komponen Leksikal (Lexer/Tokenizer).

### `TestBasicTokenization`
- `test_keywords_recognized`: Memastikan semua kata kunci (keywords) dikenali dengan benar.
- `test_identifier_simple`: Menguji tokenisasi pengenal (identifiers) yang valid.
- `test_boolean_values`: Memastikan token `benar` dan `salah` memiliki nilai boolean Python yang sesuai.

### `TestOperatorsAndPunctuation`
- `test_operator_recognition`: Menguji semua operator aritmatika dan perbandingan.
- `test_punctuation`: Menguji tanda baca seperti kurung dan koma.

### `TestNumberParsing`
- `test_integer_basic`: Menguji tokenisasi angka bulat (integer).
- `test_float_basic`: Menguji tokenisasi angka desimal (float).
- `test_float_invalid_leading_dot`: Memastikan format float seperti `.123` tidak valid.
- `test_float_invalid_trailing_dot`: Memastikan format float seperti `123.` tidak valid.
- `test_float_multiple_dots`: Memastikan format float seperti `1.2.3` tidak valid.

### `TestStringParsing`
- `test_string_basic`: Menguji tokenisasi string sederhana.
- `test_string_empty`: Menguji string kosong.
- `test_string_escape_quote`: Menguji escape sequence untuk kutip ganda (`"`).
- `test_string_escape_backslash`: Menguji escape sequence untuk garis miring terbalik (`\`).
- `test_string_escape_newline`: Menguji escape sequence untuk baris baru (`\n`).
- `test_string_unterminated`: Memastikan string yang tidak ditutup menghasilkan token `TIDAK_DIKENAL`.

### `TestComments`
- `test_comment_single_line`: Memastikan komentar di akhir baris diabaikan.
- `test_comment_entire_line`: Memastikan baris yang sepenuhnya berisi komentar diabaikan.

### `TestLexerErrors`
- `test_invalid_character`: Memastikan karakter yang tidak valid menghasilkan token `TIDAK_DIKENAL`.
- `test_error_has_line_info`: Memastikan token error memiliki informasi baris dan kolom yang benar.

### `TestEdgeCases`
- `test_empty_source`: Memastikan kode sumber kosong tidak menyebabkan error.
- `test_whitespace_only`: Memastikan kode yang hanya berisi spasi tidak menyebabkan error.
- `test_newline_tracking`: Memastikan lexer melacak nomor baris dengan benar.
- `test_robustness_whitespace_only_source_returns_valid_list`: Validasi untuk memastikan input spasi mengembalikan list token yang valid.
- `test_robustness_no_return_value_bug`: Validasi untuk memastikan metode `buat_token()` tidak pernah mengembalikan `None`.

---

## `tests/test_modules.py`

Tes untuk sistem impor modul.

- `test_import_all_simple`: Menguji `ambil_semua` untuk mengimpor semua simbol dari modul.
- `test_import_with_alias`: Menguji `ambil_semua ... sebagai` untuk mengimpor modul ke dalam sebuah namespace.
- `test_import_partial`: Menguji `ambil_sebagian ... dari` untuk mengimpor simbol-simbol tertentu.

---

## `tests/test_penerjemah.py`

Tes unit untuk komponen Penerjemah (Interpreter).

### `TestArithmeticOperators`
- `test_modulo_operator`: Menguji operator modulo (`%`).
- `test_exponent_operator`: Menguji operator pangkat (`^`).
- `test_precedence`: Menguji urutan prioritas operator.
- `test_right_associativity_for_exponent`: Memastikan operator pangkat bersifat asosiatif kanan (e.g., `2^3^2` adalah `2^(3^2)`).

### `TestArithmeticErrors`
- `test_modulo_by_zero`: Memastikan modulo dengan nol menghasilkan `KesalahanRuntime`.
- `test_division_by_zero`: Memastikan pembagian dengan nol menghasilkan `KesalahanRuntime`.
- `test_type_error_for_arithmetic`: Memastikan operasi aritmatika pada tipe non-numerik menghasilkan `KesalahanRuntime`.

### `TestExecutionLimits`
- `test_execution_timeout`: Memastikan interpreter berhenti jika melebihi batas waktu eksekusi maksimal.

---

## `tests/test_penerjemah_bawaan.py`

Tes untuk fungsi-fungsi bawaan (built-in functions).

- `test_ambil_dengan_prompt`: Menguji fungsi `ambil()` dengan pesan prompt.
- `test_ambil_tanpa_prompt`: Menguji fungsi `ambil()` tanpa pesan prompt.
- `test_ambil_handle_eof`: Memastikan `ambil()` mengembalikan string kosong saat `EOFError`.
- `test_ambil_dalam_ekspresi_dan_tulis`: Menguji penggunaan `ambil()` di dalam ekspresi lain.
- `test_ambil_prompt_dari_variabel`: Memastikan prompt untuk `ambil()` bisa berasal dari sebuah variabel.
- `test_ambil_dengan_argumen_bukan_teks_gagal`: Memastikan `ambil()` gagal jika prompt bukan string.

---

## `tests/test_pengurai.py`

Tes unit untuk komponen Pengurai (Parser).

### `TestVariableDeclarations`
- `test_simple_variable_declaration`: Menguji parsing deklarasi `biar`.
- `test_constant_variable_declaration`: Menguji parsing deklarasi `tetap`.

### `TestControlFlow`
- `test_simple_if_statement`: Menguji parsing `jika-maka-akhir`.
- `test_if_else_statement`: Menguji parsing `jika-maka-lain-akhir`.
- `test_if_elseif_else_statement`: Menguji parsing `jika-maka-lain jika-maka-lain-akhir`.
- `test_nested_if_statement`: Menguji parsing `jika` bersarang.

### `TestParserIntegrity`
- `test_parse_empty_source_returns_empty_program_node`: Memastikan input kosong menghasilkan AST program yang valid dan kosong.

---

## `tests/unit/test_parser_recovery.py`

Tes untuk mekanisme pemulihan kesalahan (error recovery) pada parser.

- `test_parser_error_recovery`: Memastikan parser dapat pulih dari kesalahan sintaks dan melaporkan beberapa kesalahan sekaligus.

---

## `tests/unit/test_performance.py`

Tes untuk mengukur dan mencegah regresi kinerja.

- `test_recursion_performance`: Mengukur kinerja pemanggilan fungsi rekursif yang dalam untuk memastikan tidak ada penurunan kinerja yang signifikan.
