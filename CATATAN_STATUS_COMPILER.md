# Status Compiler Morph (Self-Hosting)

Dokumen ini melacak progres transisi dari compiler berbasis Python (`ivm`) menuju compiler mandiri (`greenfield`).

**Status Keseluruhan:** 🟢 **Partial Self-Hosting (Stable Frontend)**
*   Host Compiler (`ivm/compiler.py`) memiliki fitur lengkap dan stabil.
*   Self-Hosted Compiler (`greenfield/kompiler/`) setara secara fungsional (logika), namun belum bisa berjalan penuh di atas Native VM karena isu runtime VM.
*   Standard Library (`cotc`) stabil di level logika, modular, namun memiliki campuran implementasi Native dan Wrapper.

## 1. Fitur Bahasa & Dukungan Compiler

| Fitur | Host Compiler (Python) | Self-Hosted Compiler (Morph) | Catatan Audit |
| :--- | :---: | :---: | :--- |
| Variable Declaration | ✅ | ✅ | |
| Assignment | ✅ | ✅ | |
| Arithmetic Ops | ✅ | ✅ | |
| Logical Ops | ✅ | ✅ | |
| Control Flow | ✅ | ✅ | |
| Functions | ✅ | ✅ | |
| Classes | ✅ | ✅ | |
| Inheritance | ✅ | ✅ | |
| Modules (Import) | ✅ | ✅ | |
| FFI (Native) | ✅ | ✅ | |
| List/Dict Literals | ✅ | ✅ | |
| **Closures** | ✅ | ✅ | |
| **Destructuring** | ✅ | ✅ | |
| **Interpolation** | ✅ | ✅ | |
| **Pattern Matching** | ✅ | ✅ | |
| Error Handling | ✅ | ✅ | |
| Ternary Operator | ✅ | ✅ | |
| **Native Intrinsics** | ✅ | ✅ | Menggunakan `Op.STR_*`, `Op.SYS_*` yang dipetakan ke fungsi Host Python oleh VM. |

## 2. Milestone Pencapaian

### ✅ Tahap 1: Fondasi (Selesai)
*   VM Python (`ivm/vms/standard_vm.py`) stabil dan bisa menjalankan bytecode kompleks.
*   Format Binary (`.mvm`) terstandarisasi ("VZOEL FOXS").
*   FFI (`pinjam`) berfungsi untuk interop Python.

### ✅ Tahap 2: Bootstrap (Selesai)
*   Parser Greenfield (`greenfield/crusher.fox`) paritas dengan parser Python.
*   Modularisasi Compiler (`greenfield/kompiler/` paket).
*   CLI `morph` bisa build dan run file `.fox`.

### 🟡 Tahap 3: Fitur Lanjutan (Sedang Berjalan & Audit)
*   **Closure:** Host Compiler ✅, Self-Hosted ✅.
*   **Struktur Data Native:** `Tumpukan` & `Antrian` ✅ (Pure Morph).
*   **Native System/IO:** Opcode `SYS_*`, `NET_*`, `IO_*` terimplementasi. Status: **Intrinsik VM** (Valid).
*   **Stdlib Purity:** Audit menunjukkan `base64` dan `netbase` masih mengandung wrapper/FFI.

## 3. Matriks Pengujian

| Komponen | Status Tes | Alat Verifikasi |
| :--- | :---: | :--- |
| **Lexer** | ✅ Stabil | `greenfield/lx_morph.fox` |
| **Parser** | ✅ Stabil | `tests/test_parser_parity.py` |
| **Compiler (Host)** | ✅ Stabil | `run_ivm_tests.py` |
| **Compiler (Self)** | 🟡 WIP | `hello_world.fox` (Compile Only), Run via Host VM. |
| **VM Runtime** | ⚠️ **Regresi** | Gagal menjalankan Lexer Self-Hosted (`test_vm_lexer_wip.fox`). |
| **Closure Support** | ✅ Stabil | `test_closure.fox` (Host & Self) |
| **Native Lib (IO/Sys)** | ✅ Stabil | `test_foxys_io.fox`, `test_pure_teks.fox` |

---
*Diperbarui terakhir: Audit Kejujuran Sistem.*
