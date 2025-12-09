# Status Compiler Morph (Self-Hosting)

Dokumen ini melacak progres transisi dari compiler berbasis Python (`ivm`) menuju compiler mandiri (`greenfield`).

**Status Keseluruhan:** 🚀 **Full Compiler Self-Hosting**
*   **Self-Hosted Compiler (`greenfield/kompiler/`) SUKSES** mengkompilasi dirinya sendiri dan kode sumber lain. Ini diverifikasi oleh workflow CI/CD (`morph_ci.yml`) yang menggunakan `greenfield/morph.fox` untuk membangun artefak.
*   **Runtime Dependency:** Compiler saat ini masih dijalankan di atas Host VM (`StandardVM` Python), namun logika kompilasi sepenuhnya berada di kode Morph.

## 1. Fitur Bahasa & Dukungan Compiler

| Fitur | Host Compiler (Python) | Self-Hosted Compiler (Morph) | Catatan Audit |
| :--- | :---: | :---: | :--- |
| Variable Declaration | ✅ | ✅ | |
| Assignment | ✅ | ✅ | Fixed Global Scope Issue. |
| Arithmetic Ops | ✅ | ✅ | |
| Logical Ops | ✅ | ✅ | |
| Control Flow | ✅ | ✅ | |
| Functions | ✅ | ✅ | |
| Classes | ✅ | ✅ | |
| Inheritance | ✅ | ✅ | |
| Modules (Import) | ✅ | ✅ | |
| FFI (Native) | ✅ | ✅ | |
| List/Dict Literals | ✅ | ✅ | |
| **Closures** | ✅ | ✅ | Fully supported & verified. |
| **Destructuring** | ✅ | ✅ | |
| **Interpolation** | ✅ | ✅ | |
| **Pattern Matching** | ✅ | ✅ | Local scope verified. |
| Error Handling | ✅ | ✅ | Local scope verified. |
| Ternary Operator | ✅ | ✅ | |
| **Native Intrinsics** | ✅ | ✅ | Didukung penuh. |
| **Parser Updates** | ✅ | ✅ | `ambil_semua`, `ambil_sebagian`, `warnai` (Self-Hosted Parser updated). |

## 2. Milestone Pencapaian

### ✅ Tahap 1: Fondasi (Selesai)
*   VM Python (`ivm/vms/standard_vm.py`) stabil dan bisa menjalankan bytecode kompleks.
*   Format Binary (`.mvm`) terstandarisasi ("VZOEL FOXS").
*   FFI (`pinjam`) berfungsi untuk interop Python.

### ✅ Tahap 2: Bootstrap & Self-Hosting (Selesai)
*   **Compiler Self-Hosting Tercapai:** `greenfield/morph.fox build` sukses menghasilkan `.mvm` valid.
*   **Serialization Pure Morph:** Modul `struktur.fox` telah dibersihkan dari FFI, menjamin determinisme.
*   Modularisasi Compiler (`greenfield/kompiler/` paket) stabil.

### 🟡 Tahap 3: Runtime Independence (Sedang Berjalan)
*   **Pure Morph Stdlib:** `teks`, `matematika`, `himpunan`, `struktur` sudah Pure Morph. `railwush` (ex-netbase) baru saja dimigrasikan ke Pure Morph (Cryptex).
*   **Native VM:** Sudah stabil untuk operasi dasar dan struktur data, namun eksekusi kode kompleks (seperti Compiler itu sendiri) di atas Native VM masih dalam tahap stabilisasi.

## 3. Matriks Pengujian

| Komponen | Status Tes | Alat Verifikasi |
| :--- | :---: | :--- |
| **Lexer** | ✅ Stabil | `greenfield/lx_morph.fox` |
| **Parser** | ✅ Stabil | `tests/test_parser_parity.py` & `greenfield/verifikasi.fox` |
| **Compiler (Self)** | ✅ **SUKSES** | CI/CD Workflow (`morph_ci.yml`) |
| **Scope Logic** | ✅ **FIXED** | `repro_global_scope.fox` (Deleted after fix) |
| **VM Runtime** | 🟡 Beta | Heisenbugs (Globals/Type) fixed. Lexer execution in progress. |
| **Railwush/Crypto** | ✅ Stabil | `test_railwush.fox` |
| **Runner/CI** | ✅ Stabil | `run_ivm_tests.py` now correctly reports exit code 1 on failure. |

---
*Diperbarui terakhir: Perbaikan Bug Scope Compiler & Migrasi Railwush.*
