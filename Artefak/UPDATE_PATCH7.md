# Update Patch 7: Arithmetic & Logic in Rust VM

**Status:** COMPLETE
**Date:** 11/12/2025

## 1. Perubahan Utama
Patch ini fokus pada implementasi kemampuan komputasi dasar (Aritmatika & Logika) pada Greenfield Native VM (Rust).

### A. Rust VM (`greenfield/morph_vm`)
- **Aritmatika:** Implementasi opcode `ADD` (4), `SUB` (5), `MUL` (6), `DIV` (7), `MOD` (8). Mendukung Integer dan Float.
- **Logika:** Implementasi opcode `EQ`, `NEQ`, `GT`, `LT`, `GTE`, `LTE`, `NOT`, `AND`, `OR`.
- **Stack:** Implementasi opcode `POP` (2), `DUP` (3).
- **IO:** Implementasi opcode `PRINT` (53).

### B. Self-Hosted Compiler (Hotfixes)
- **Ekspresi:** Menambahkan dukungan emisi opcode `MOD` untuk operator `%` di `greenfield/kompiler/ekspresi.fox`.
- **Lexer:** Patch pada `greenfield/lx_morph.fox` untuk memastikan keyword `tulis` dikenali sebagai Token Tipe `TULIS` (mengatasi masalah deteksi identifier).
- **Opcode:** Update `greenfield/cotc/bytecode/opkode.fox` untuk menyertakan `PRINT = 53`.

## 2. Hasil Pengujian
- **Aritmatika:** `greenfield/examples/uji_aritmatika.fox` -> **PASS**.
- **Logika:** `greenfield/examples/uji_logika.fox` -> **PASS**.

## 3. Langkah Selanjutnya (Patch 8)
- Implementasi Control Flow (JMP, JMP_IF) di Rust.
- Implementasi Function Calls (CALL, RET dengan Frame) di Rust.
