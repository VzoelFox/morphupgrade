# Catatan Perjalanan Self-Hosting (FoxVM Ascension)
**Founder:** Vzoel Fox's (Lutpan)
**Engineer:** Jules AI

Dokumen ini melacak kemajuan spesifik menuju "Self-Hosting".

## UPDATE STRATEGIS (PATCH 18 - MICRO LLVM PIVOT)
**Status:** Rust VM (FoxVM) telah **DIHENTIKAN** dan diarsipkan ke `archived_morph/`.

**Arah Baru:**
Kita beralih dari memelihara 3 VM (Bootstrap, Rust, Morph) menjadi strategi "Morph as Kernel":
1.  **Orchestrator Utama:** Morph Compiler (Self-Hosted).
2.  **Driver:** Micro LLVM / C++ Driver tipis untuk bootstrapping hardware.
3.  **Foundation:** Mematangkan Self-Hosted Compiler di atas Python VM (IVM) sebelum transisi ke Micro LLVM.

---

## Status Saat Ini: Fase Konsolidasi IVM

Kita kembali fokus memastikan `greenfield/kompiler` berjalan sempurna di atas Python VM (IVM).

### Tantangan Tersisa
1.  **Full Compilation di IVM:** Memastikan `greenfield/morph.fox` bisa melakukan `build` kode yang kompleks tanpa error.
2.  **Generasi LLVM:** Membangun ulang generator LLVM yang lebih robust (setelah eksperimen awal gagal karena isu parser bootstrap).

---

## Riwayat Arsip (Deprecated)

### [DEPRECATED] Rust VM Status (Patch 17)
*   *Catatan: Rust VM telah diarsipkan per Patch 18.*
*   Pencapaian terakhir: Lexer berjalan, Parser crash di konstruksi AST.
*   Alasan penghentian: Beban maintenance ganda dan keputusan strategis untuk menggunakan LLVM sebagai backend universal.

---
*Dokumen ini akan terus diperbarui seiring perjalanan menuju Self-Hosting.*
