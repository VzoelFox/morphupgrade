# Catatan Hutang Teknis (Technical Debt) & Fokus Masa Depan
# Diperbarui: Patch 16 (Bytes Fix)

## 1. Kestabilan Rust VM (Critical)

### A. [SELESAI] Panic pada Operasi Matematika
*   **Status:** Teratasi di Patch 15.

### B. [SELESAI] Reference Cycles (Memory Leak)
*   **Status:** Teratasi di Patch 15.

### C. [SELESAI] Opcode Perbandingan yang Hilang
*   **Status:** Teratasi di Patch 15.

### D. [SELESAI] Dukungan OOP (Kelas & Metode)
*   **Status:** Teratasi di Patch 15. Dukungan inisialisasi otomatis (`is_init`) ditambahkan di Patch 16.

### E. [SELESAI] Dukungan Pattern Matching (Jodohkan)
*   **Status:** Teratasi di Patch 15.

### F. [SELESAI] Portabilitas Bytes (Blocker Self-Hosting)
Modul `bytes.fox` telah di-refactor menggunakan syscall `_backend`. Rust VM telah mendukung `Constant::Bytes` dan opcode terkait.
*   **Status:** Teratasi di Patch 16.

### G. [BARU] Paritas Metode String (String Method Parity)
Rust VM masih kurang dalam mendukung metode string native yang diharapkan oleh kode Morph (misalnya `.split()` atau `.pisah()`). Saat ini `LOAD_ATTR` untuk string di Rust VM sangat minimal.
*   **Dampak:** Compiler panic saat melaporkan error (`AttributeError: 'teks' tidak punya 'split'`).
*   **Solusi:** Implementasi `sys_str_split` di `_backend` atau update `LOAD_ATTR` untuk delegasi ke syscall.

## 2. Fitur yang Belum Ada (Missing Features)

### A. Cross-Frame Exception Unwinding
Implementasi `THROW` saat ini hanya mencari handler (`try_stack`) di frame lokal dan menelusuri stack frame pemanggil. Perlu pengujian batas modul.

### B. Standard Library yang Terfragmentasi
Saat ini ada `stdlib/core.fox` (stub lama yang kini menggunakan `_backend`), `sys/syscalls.fox` (interface baru), dan `bridge_fox.fox`.
*   **Status Patch 16:** `core.fox` telah diperbarui untuk menggunakan `_backend`, mengurangi fragmentasi builtins.

## 3. Toolchain & Self-Hosting

### A. [ONGOING] Self-Hosted Compiler Execution
Kompiler Morph kini bisa berjalan di atas Rust VM (Hybrid Self-Hosting). Namun, masih mengalami *runtime error* pada logika Lexer/Parser tertentu.
*   **Status:** Berjalan (Patch 16), tapi belum stabil (Crash pada Lexing).
*   **Tugas:** Debugging logika `lx_morph.fox` saat berjalan di Rust VM (mungkin perbedaan representasi Char/String).

---
**Status Penyelesaian Patch 16:**
- [x] **Native Bytes:** Implementasi `Constant::Bytes` dan syscall terkait di Rust VM.
- [x] **Opcode Bitwise:** Memperbaiki bug kritis Opcode 69-74 yang hilang/salah mapping.
- [x] **Opcode Logika:** Memisahkan Opcode 15-17 (Logical) dari Bitwise.
- [x] **Class Init:** Rust VM kini otomatis memanggil `inisiasi` saat instansiasi kelas.
- [x] **Core Refactor:** `stdlib/core.fox` tidak lagi menggunakan `builtins` Python lama.
- [x] **Self-Hosting Run:** Kompiler berhasil dimuat dan dijalankan di Rust VM (meski masih ada bug runtime).
