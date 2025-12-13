# AGENTS.md - Morph Kernel Zone

**Scope:** `greenfield/kompiler/`

## Instruksi Khusus Agen
Direktori ini adalah **Jantung** dari Morph ("The Kernel").

### Aturan Utama:
1.  **Self-Hosted:** Semua kode di sini ditulis dalam Morph (`.fox`).
2.  **Compatibility:** Saat ini kode harus bisa berjalan di atas IVM (Python Host) DAN dipersiapkan untuk berjalan di atas Micro Driver (LLVM) nantinya.
3.  **No Python Dependencies:** Jangan gunakan `pinjam "builtins"` di sini kecuali benar-benar terpaksa untuk debugging sementara. Kernel harus murni.

### Fokus Pengembangan Patch 18:
*   Pastikan AST dan bytecode generation stabil.
*   Persiapan antarmuka untuk komunikasi dengan Driver C++ (nanti akan ada syscall khusus).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
