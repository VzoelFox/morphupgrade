# AGENTS.md - Micro Driver Zone

**Scope:** `greenfield/micro_llvm_driver/`

## Instruksi Khusus Agen
Direktori ini berisi kode C++ untuk Driver Micro LLVM.

### Aturan Utama:
1.  **Keep it Thin:** Driver ini tidak boleh berisi logika bisnis bahasa Morph. Tugasnya hanya **Bootstrapping** dan **Hardware Interface**. Logika bahasa harus tetap di `greenfield/kompiler` (Morph).
2.  **Compiler:** Gunakan `g++` (GCC) sebagai standar kompilasi utama karena stabilitasnya di lingkungan ini. Hindari `clang++` jika menyebabkan segfault pada parser.
3.  **Dependency Free:** Usahakan tidak menggunakan library C++ berat (seperti Boost). Gunakan Standard Library (STL) saja.

### Struktur CLI:
*   Parser argumen ada di `main.cpp`.
*   Jika Anda mengubah sintaks `run morph make` atau `star spawn`, pastikan update parser di sini.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
