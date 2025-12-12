# Catatan Perjalanan Self-Hosting (FoxVM Ascension)
**Founder:** Vzoel Fox's (Lutpan)
**Engineer:** Jules AI

Dokumen ini melacak kemajuan spesifik menuju "Self-Hosting", yaitu kemampuan FoxVM (Rust/Python) untuk menjalankan Compiler Morph (yang ditulis dalam Morph) secara mandiri tanpa bantuan Python `builtins`.

## Status Saat Ini: Fase 1 - Infrastruktur Dasar (Patch 16)

### Pencapaian
*   **[SELESAI] Portabilitas Bytes:** Modul kritis `greenfield/cotc/bytes.fox` tidak lagi bergantung pada `pinjam "builtins"`.
*   **[SELESAI] Native Bytes Support:** Rust VM kini memiliki tipe native `Constant::Bytes` (sebelumnya hanya String/List).
*   **[SELESAI] Bitwise Opcodes:** Memperbaiki bug kritis di mana opcode bitwise (AND, OR, XOR, SHIFT) hilang atau salah dipetakan di Rust VM.

### Tantangan Tersisa (To-Do)
1.  **Full Compiler Execution:** Mencoba menjalankan `greenfield/morph.fox` (Compiler) sepenuhnya di atas Rust VM untuk mengkompilasi file sederhana.
2.  **File I/O Completeness:** Memastikan semua operasi file yang dibutuhkan compiler didukung oleh Rust VM.
3.  **Performance Tuning:** Optimasi operasi byte dan string di Rust VM.

---

## Log Perubahan Kritis

### Patch 16 (Bytes & Opcode Fix)
*   **Masalah:** `bytes.fox` menggunakan `builtins` Python untuk packing/unpacking binary. Rust VM panik karena tidak punya `builtins`.
*   **Solusi:**
    1.  Menambahkan syscall `sys_bytes_dari_list`, `sys_bytes_ke_list` di `_backend`.
    2.  Implementasi `Constant::Bytes` di Rust VM.
    3.  Implementasi Opcode Bitwise (69-74) yang hilang di Rust VM.
*   **Hasil:** `pack_int`, `pack_string` kini berjalan murni menggunakan logika Morph dan Syscall VM-agnostic.

---
*Dokumen ini akan terus diperbarui seiring perjalanan menuju Self-Hosting.*
