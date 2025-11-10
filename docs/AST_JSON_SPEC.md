# MORPH AST JSON Specification v1.0

Dokumen ini mendefinisikan struktur format JSON yang digunakan sebagai *Intermediate Representation* (IR) antara compiler OCaml dan interpreter Python untuk bahasa MORPH.

## Meta Structure

Setiap output JSON dari compiler harus memiliki struktur dasar (amplop) seperti ini:

```json
{
  "format_version": "1.0",
  "compiler_version": "string",
  "status": "success" | "error",
  "ast": "Program | null",
  "errors": "[Error] | null"
}
```

- `format_version`: Versi dari spesifikasi JSON ini. Harus divalidasi oleh interpreter.
- `compiler_version`: Versi compiler OCaml yang menghasilkan output ini.
- `status`: Menandakan apakah kompilasi berhasil atau gagal.
- `ast`: *Abstract Syntax Tree* dari program jika `status` adalah `success`.
- `errors`: Daftar error jika `status` adalah `error`.

## Token Format

Semua token dalam AST akan mengikuti format berikut:

```json
{
  "tipe": "string (nama dari TipeToken enum)",
  "nilai": "any",
  "baris": "int",
  "kolom": "int"
}
```

- `tipe`: Representasi string dari enum `TipeToken` di Python (contoh: `"BIAR"`, `"NAMA"`, `"ANGKA"`).
- `nilai`: Nilai literal dari token (contoh: `"biar"`, `"x"`, `10`).
- `baris`, `kolom`: Posisi token di file sumber.

## Node Structures

### Root Node

```json
{
  "node_type": "Program",
  "body": "[Statement]"
}
```

### Expression Nodes

#### `Konstanta`
Merepresentasikan nilai literal.

```json
{
  "node_type": "Konstanta",
  "token": "Token",
  "nilai": "any"
}
```
- `token`: Token asli dari sumber.
- `nilai`: Nilai Python yang sudah di-parse (misalnya, `10`, `true`, `"hello"`).

#### `FoxBinary`
Merepresentasikan operasi biner.

```json
{
  "node_type": "FoxBinary",
  "kiri": "Expr",
  "operator": "Token",
  "kanan": "Expr"
}
```

### Statement Nodes

#### `DeklarasiVariabel`
Merepresentasikan deklarasi variabel (`biar` atau `tetap`).

```json
{
  "node_type": "DeklarasiVariabel",
  "jenis_deklarasi": "Token (BIAR atau TETAP)",
  "nama": "Token (NAMA)",
  "nilai": "Expr | null"
}
```
