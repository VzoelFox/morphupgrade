# Update Patch 16: The Bytes & Bitwise Fix

**Tanggal:** 12 Desember 2025 (Estimasi)
**Engineer:** Jules AI
**Founder:** Vzoel Fox's (Lutpan)

Patch ini adalah langkah monumental menuju **Self-Hosting**. Kami telah menyingkirkan salah satu penghalang terbesar: ketergantungan pada Python `builtins` untuk manipulasi byte. Selain itu, kami memperbaiki bug fundamental pada Rust VM terkait operasi Bitwise.

## 1. Native Bytes Support (Rust VM)

Rust VM kini memiliki tipe data `Constant::Bytes` (sebelumnya hanya String atau List of Ints).
*   **Tipe Baru:** `Bytes(Vec<u8>)`.
*   **Operasi:** Dukungan untuk konkatenasi (`ADD`), indexing (`LOAD_INDEX`), slicing (`SLICE`), panjang (`LEN`), dan penulisan file (`IO_WRITE`).
*   **Keuntungan:** Compiler Morph kini bisa menghasilkan file biner `.mvm` langsung dari Rust VM dengan efisien.

## 2. Refactor `bytes.fox` (Dependency Removal)

Modul `greenfield/cotc/bytes.fox` telah ditulis ulang sepenuhnya.
*   **Hapus `pinjam "builtins"`:** Tidak ada lagi ketergantungan pada Python API.
*   **Backend Syscalls:** Menggunakan antarmuka `_backend` standar (`sys_bytes_dari_list`, `sys_bytes_ke_list`) yang diimplementasikan di kedua VM (Python & Rust).
*   **Manual UTF-8 Encoding:** Implementasi encoding string ke bytes dilakukan secara manual di Morph (dengan bantuan bitwise ops) untuk independensi total.

## 3. Perbaikan Kritis: Opcode Bitwise

Ditemukan bahwa Rust VM sebelumnya **tidak mengimplementasikan** opcode Bitwise (69-74) dan salah memetakan opcode Logika. Hal ini menyebabkan perhitungan bitwise (seperti saat packing integer ke bytes) gagal total (menghasilkan 255/FF).

*   **Fixed:** Implementasi Opcode 69-74 (`BIT_AND`, `BIT_OR`, `BIT_XOR`, `BIT_NOT`, `LSHIFT`, `RSHIFT`).
*   **Fixed:** Pemisahan Opcode Logika (15-17: `NOT`, `AND`, `OR`) dari Opcode Bitwise.

## 4. Syscall Backend Baru

Interface `_backend` diperluas untuk mendukung operasi bytes lintas VM:
*   `sys_bytes_dari_list(list)`: Konversi `[int]` -> `Bytes`.
*   `sys_bytes_ke_list(bytes)`: Konversi `Bytes` -> `[int]`.
*   `sys_bytes_decode(bytes, encoding)`: Decode bytes ke string.
*   `sys_list_append(list, item)`: Helper untuk operasi list performa tinggi.

---
*Langkah selanjutnya: Mencoba menjalankan Compiler Morph sepenuhnya di atas Rust VM.*
