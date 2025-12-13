# Catatan Perjalanan Self-Hosting (FoxVM Ascension)
**Founder:** Vzoel Fox's (Lutpan)
**Engineer:** Jules AI

Dokumen ini melacak kemajuan spesifik menuju "Self-Hosting", yaitu kemampuan FoxVM untuk menjalankan Compiler Morph (yang ditulis dalam Morph) secara mandiri.

## Status Saat Ini: Fase 3 - Pivot Strategi (LLVM)

### Keputusan Strategis (Patch 16/17)
*   **Masalah:** Pengembangan `morph_vm` (Rust) mengalami stagnasi ("Jalan Buntu") pada integrasi Lexer dan kompleksitas arsitektur.
*   **Keputusan:** Menghentikan sementara dan mengarsipkan pengembangan Rust VM (`morph_vm`).
*   **Arah Baru:** Fokus dialihkan untuk mengembangkan kemampuan **FoxVM memancarkan LLVM IR**. Tujuannya adalah kompilasi ke *Native Code* via LLVM, bukan lagi interpretasi bytecode via Custom VM.

### Riwayat Fase 2 - Eksekusi Kompiler (Diarsipkan)
*   **[SELESAI] Portabilitas Bytes:** Modul kritis `greenfield/cotc/bytes.fox` tidak lagi bergantung pada `pinjam "builtins"`.
*   **[SELESAI] Native Bytes Support:** Rust VM memiliki tipe native `Constant::Bytes`.
*   **[SELESAI] Bitwise Opcodes:** Memperbaiki bug kritis opcode bitwise (69-74).
*   **[SELESAI] Eksekusi Kompiler:** `greenfield/morph.fox` (Compiler) berhasil dijalankan di atas Rust VM sampai tahap inisialisasi.
*   **[TERTUNDA]** Debugging Lexer dan String Method di Rust VM dihentikan. Kode dipindahkan ke `archived_morph/rust_vm_patch16_deprecated/`.

---

## Log Perubahan Kritis

### Patch 17 (The Great Pivot)
*   **Tindakan:** Mengarsipkan `greenfield/morph_vm` ke `archived_morph/`.
*   **Pembersihan:** Menghapus referensi Rust VM dari dokumentasi utama.
*   **Persiapan:** Membuat draf awal untuk strategi backend LLVM.

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
