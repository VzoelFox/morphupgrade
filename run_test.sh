#!/bin/bash
set -e # Keluar segera jika ada perintah yang gagal

# Periksa apakah argumen file input diberikan
if [ -z "$1" ]; then
  echo "Penggunaan: $0 <path_ke_file.fox>"
  exit 1
fi

INPUT_FILE=$1
OUTPUT_JSON="output.json"
COMPILER_EXE="universal/_build/default/main.exe"
PYTHON_ENTRY_POINT="transisi.Morph" # Menggunakan interpreter utama

# 1. Compile OCaml -> JSON
echo "===== Tahap 1: Kompilasi MORPH ke JSON AST ====="
eval $(opam env)
$COMPILER_EXE "$INPUT_FILE" "$OUTPUT_JSON"
echo "Kompilasi berhasil. Output JSON disimpan di $OUTPUT_JSON"
echo ""

# 2. Execute JSON AST -> Python Interpreter
echo "===== Tahap 2: Eksekusi AST oleh Interpreter Python ====="
# Menjalankan interpreter utama, tetapi dengan flag untuk memuat dari ocaml
PYTHONPATH=. python3 -m "$PYTHON_ENTRY_POINT" --use-ocaml-loader "$OUTPUT_JSON"
echo ""
echo "===== Tes Integrasi Selesai ====="
