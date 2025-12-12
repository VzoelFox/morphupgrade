# Catatan Hutang Teknis (Technical Debt) & Fokus Masa Depan
# Diperbarui: Patch 15 (LoneWolf Update)

## 1. Kestabilan Rust VM (Critical)

### A. [SELESAI] Panic pada Operasi Matematika
Implementasi opcode `ADD`, `SUB`, `MUL`, `DIV`, `MOD` kini menggunakan `throw_exception` untuk menangani ketidakcocokan tipe.
*   **Status:** Teratasi di Patch 15.

### B. [SELESAI] Reference Cycles (Memory Leak)
Struktur `Function` kini menyimpan `globals` sebagai `Weak` reference.
*   **Status:** Teratasi di Patch 15. Siklus referensi Parent-Child diputus.

### C. [SELESAI] Opcode Perbandingan yang Hilang
Opcode dasar (`LT`, `GT`, `NEQ`, dll) sebelumnya hilang di Rust VM, menyebabkan infinite loop.
*   **Status:** Teratasi di Patch 15.

### D. [SELESAI] Dukungan OOP (Kelas & Metode)
Rust VM kini mendukung `BUILD_CLASS`, `STORE_ATTR`, dan binding `MetodeTerikat`. Compiler juga diperbaiki untuk mengkompilasi metode ke dalam kelas.
*   **Status:** Teratasi di Patch 15.

### E. [SELESAI] Dukungan Pattern Matching (Jodohkan)
Rust VM kini mendukung opcode `SNAPSHOT`, `RESTORE`, `IS_VARIANT`, dan tipe data `Variant`. Ini memungkinkan modul `json` dan sistem `LoneWolf` berjalan.
*   **Status:** Teratasi di Patch 15.

## 2. Fitur yang Belum Ada (Missing Features)

### C. Portabilitas Bytes (Blocker Self-Hosting)
Modul `greenfield/cotc/bytes.fox` masih bergantung pada `pinjam "builtins"` (Python) untuk tipe `bytes` dan `bytearray`. Rust VM belum memiliki tipe `Bytes` native, menyebabkan kegagalan saat compiler mencoba melakukan serialisasi bytecode.
*   **Solusi:** Implementasi `Constant::Bytes` di Rust VM dan porting `bytes.fox`.

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
- [x] **No Panic Math:** Opcode Aritmatika (4-8) kini melempar Exception `TipeError` atau `ZeroDivisionError` alih-alih panic.
- [x] **Memory Leak Fix:** Reference Cycle `Function <-> Globals` diputus menggunakan `Weak` references.
- [x] **Missing Opcodes:** Mengimplementasikan Opcode Comparison (10-14) yang sebelumnya hilang.
- [x] **OOP Support:** Mengimplementasikan Opcode OOP dan memperbaiki Compiler Stub untuk metode kelas.
- [x] **Pattern Matching:** Implementasi Opcode `SNAPSHOT`, `RESTORE`, `VARIANT` untuk mendukung `jodohkan` dan `LoneWolf`.
