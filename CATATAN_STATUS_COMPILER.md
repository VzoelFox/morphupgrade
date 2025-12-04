# Status Compiler Morph (Self-Hosting)

Dokumen ini melacak progres transisi dari compiler berbasis Python (`ivm`) menuju compiler mandiri (`greenfield`).

**Status Keseluruhan:** 🟡 **Partial Self-Hosting (Hybrid)**
*   Host Compiler (`ivm/compiler.py`) memiliki fitur lengkap (termasuk Closure).
*   Self-Hosted Compiler (`greenfield/kompiler/`) bisa mengkompilasi dirinya sendiri tapi belum mendukung fitur lanjutan (Closure).
*   Standard Library (`cotc`) stabil dan modular.

## 1. Fitur Bahasa & Dukungan Compiler

| Fitur | Host Compiler (Python) | Self-Hosted Compiler (Morph) | Catatan |
| :--- | :---: | :---: | :--- |
| Variable Declaration | ✅ | ✅ | `biar x = 1` |
| Assignment | ✅ | ✅ | `ubah x = 2` |
| Arithmetic Ops | ✅ | ✅ | `+, -, *, /, %` |
| Logical Ops | ✅ | ✅ | `dan, atau, tidak` |
| Control Flow | ✅ | ✅ | `jika, selama, pilih` |
| Functions | ✅ | ✅ | `fungsi nama(a) ... akhir` |
| Classes | ✅ | ✅ | `kelas Nama ... akhir` |
| Inheritance | ✅ | ✅ | `kelas Anak dari Induk` |
| Modules (Import) | ✅ | ✅ | `dari "..." ambil ...` |
| FFI (Native) | ✅ | ✅ | `pinjam "..."` |
| List/Dict Literals | ✅ | ✅ | `[1, 2], {"a": 1}` |
| **Closures** | ✅ | ❌ | Captured vars (`cell_vars`) |
| **Destructuring** | ✅ | ✅ | `biar [a, b] = data` |
| **Interpolation** | ✅ | ✅ | `"Nilai: {x}"` |
| **Pattern Matching** | ✅ | ✅ | `jodohkan x dengan ...` |
| Error Handling | ✅ | ✅ | `coba ... tangkap ...` |
| Ternary Operator | ✅ | ✅ | `kondisi ? benar : salah` |

## 2. Milestone Pencapaian

### ✅ Tahap 1: Fondasi (Selesai)
*   VM Python (`ivm/vms/standard_vm.py`) stabil dan bisa menjalankan bytecode kompleks.
*   Format Binary (`.mvm`) terstandarisasi ("VZOEL FOXS").
*   FFI (`pinjam`) berfungsi untuk interop Python.

### ✅ Tahap 2: Bootstrap (Selesai)
*   Parser Greenfield (`greenfield/crusher.fox`) paritas dengan parser Python.
*   Modularisasi Compiler (`greenfield/kompiler/` paket).
*   CLI `morph` bisa build dan run file `.fox`.

### 🟡 Tahap 3: Fitur Lanjutan (Sedang Berjalan)
*   **Closure:** Host Compiler ✅, Self-Hosted ❌.
*   **Optimasi:** Constant Folding (Belum).
*   **Linter:** Deteksi blok kosong (Basic).

## 3. Matriks Pengujian

| Komponen | Status Tes | Alat Verifikasi |
| :--- | :---: | :--- |
| **Lexer** | ✅ Stabil | `greenfield/lx_morph.fox` |
| **Parser** | ✅ Stabil | `tests/test_parser_parity.py` |
| **Compiler (Host)** | ✅ Stabil | `run_ivm_tests.py` |
| **Compiler (Self)** | 🟡 Parsial | `hello_world.fox`, `test_logika_unit.fox` |
| **VM Runtime** | ✅ Stabil | Unit tests internal VM |
| **Closure Support** | ✅ Stabil | `test_closure.fox` (Host Only) |

---
*Diperbarui terakhir: Setelah implementasi Closure di Host Compiler.*
