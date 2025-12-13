# Catatan Perjalanan Self-Hosting (FoxVM Ascension)
**Founder:** Vzoel Fox's (Lutpan)
**Engineer:** Jules AI

Dokumen ini melacak kemajuan spesifik menuju "Self-Hosting", yaitu kemampuan FoxVM (Rust/Python) untuk menjalankan Compiler Morph (yang ditulis dalam Morph) secara mandiri tanpa bantuan Python `builtins`.

## Status Saat Ini: Fase 2 - Eksekusi Kompiler (Patch 16)

### Pencapaian
*   **[SELESAI] Portabilitas Bytes:** Modul kritis `greenfield/cotc/bytes.fox` tidak lagi bergantung pada `pinjam "builtins"`.
*   **[SELESAI] Native Bytes Support:** Rust VM kini memiliki tipe native `Constant::Bytes`.
*   **[SELESAI] Bitwise Opcodes:** Memperbaiki bug kritis di mana opcode bitwise (69-74) hilang di Rust VM.
*   **[SELESAI] Backend Syscalls:** Implementasi `_backend` (sys_bytes, sys_list, sys_str) di kedua VM.
*   **[SELESAI] Eksekusi Kompiler:** `greenfield/morph.fox` (Compiler) **BERHASIL** dijalankan di atas Rust VM! Ia memuat semua modul dependensi dan memulai proses kompilasi.

### Tantangan Tersisa (To-Do Patch 17)
1.  **Lexer/Parser Debugging:** Kompiler melaporkan "Gagal Lexing" pada file sederhana. Perlu investigasi apakah ini bug logika di `lx_morph.fox` atau bug VM (misal: perbandingan karakter).
2.  **Missing String Methods:** Rust VM belum mendukung metode `.split` (pisah) secara native pada string (AttributeError), menyebabkan crash saat pelaporan error. Solusi: Gunakan `teks.pisah` atau implementasikan syscall.
3.  **Full Compilation:** Mencapai titik di mana `build hello.fox` menghasilkan output `.mvm` yang valid dari Rust VM.

---

## Log Perubahan Kritis

### Patch 16 (Bytes & Opcode Fix)
*   **Masalah:** `bytes.fox` menggunakan `builtins` Python. Rust VM panik.
*   **Solusi:**
    1.  Menambahkan syscall `sys_bytes_*` dan `sys_list_*` di `_backend`.
    2.  Implementasi Opcode Bitwise (69-74) dan Logika (15-17) di Rust VM.
    3.  Implementasi `is_init` logic untuk pemanggilan konstruktor kelas di Rust VM.
    4.  Refactor `bytes.fox`, `core.fox`, `loader.fox`, `analisis.fox` untuk menghapus dependensi `builtins`.
*   **Hasil:** Kompiler berjalan di Rust VM sampai tahap Lexing.

---
*Dokumen ini akan terus diperbarui seiring perjalanan menuju Self-Hosting.*
