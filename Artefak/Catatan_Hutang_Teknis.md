# Catatan Hutang Teknis (Technical Debt) & Fokus Masa Depan
# Diperbarui: Patch 14 (Rust VM Exception Handling)

## 1. Kestabilan Rust VM (Critical)

### A. Panic pada Operasi Matematika (ADD Mismatch)
Implementasi opcode `ADD` (4) masih menggunakan `panic!` jika tipe operand tidak cocok (misal Integer + String).
*   **Dampak:** VM crash pada operasi yang tidak valid.
*   **Solusi:** Ubah menjadi pelemparan exception (`THROW` dengan pesan TypeError) atau paksa konversi string (implicit).

### B. Reference Cycles (Memory Leak)
Struktur `Function` menyimpan `globals` (Rc), dan `globals` menyimpan `Function` (Rc).
*   **Dampak:** Memori tidak pernah dibebaskan (Memory Leak) selama VM berjalan.
*   **Solusi:** Gunakan `Weak` reference atau implementasikan Garbage Collector (GC) sederhana (Mark-and-Sweep).

## 2. Fitur yang Belum Ada (Missing Features)

### A. Cross-Frame Exception Unwinding
Implementasi `THROW` saat ini hanya mencari handler (`try_stack`) di frame lokal dan menelusuri stack frame pemanggil (Unwinding). Namun, perlu pengujian lebih lanjut untuk kasus kompleks seperti exception yang melewati batas modul/native boundaries.

### B. Standard Library yang Terfragmentasi
Saat ini ada `stdlib/core.fox` (stub lama), `sys/syscalls.fox` (interface baru), dan `bridge_fox.fox` (handler baru).
*   **Rencana:** Migrasikan semua kode lama (`berkas.fox`) untuk menggunakan `bridge_fox.fox`. Hapus stub yang tidak terpakai di `core.fox`.

## 3. Toolchain

### A. Bootstrap Compiler Compatibility
Host VM (Python) menggunakan parser lama (`transisi/crusher.py`) yang tidak mendukung sintaks baru.
*   **Solusi:** Percepat transisi ke **Full Self-Hosting** (jalankan compiler Morph di atas Rust VM).

---
**Status Penyelesaian Patch 14:**
- [x] **No Panic I/O:** Opcode IO dan Network kini mengembalikan `Nil`/`False` alih-alih panic.
- [x] **Exception Handling:** Rust VM kini mendukung `PUSH_TRY`, `POP_TRY`, dan `THROW` dengan stack unwinding.
- [x] **Lexical Scoping:** `BUILD_FUNCTION` diperbaiki untuk menangkap globals (sebagai `Function`), bukan hanya `Code`.
- [x] **Bridge Fox:** Menggunakan `lemparkan` untuk mengubah return value `nil` menjadi Exception Morph.
