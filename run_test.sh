#!/bin/bash
set -e # Keluar segera jika ada perintah yang gagal

# Periksa apakah argumen file input diberikan
if [ -z "$1" ]; then
  echo "Penggunaan: $0 <path_ke_file.fox>"
  exit 1
fi

INPUT_FILE=$1
PYTHON_ENTRY_POINT="transisi.Morph"

# Jalankan file .fox langsung dengan interpreter Python
echo "===== Menjalankan: $INPUT_FILE ====="
PYTHONPATH=. python3 -m "$PYTHON_ENTRY_POINT" "$INPUT_FILE"
echo ""
echo "===== Eksekusi Selesai ====="
