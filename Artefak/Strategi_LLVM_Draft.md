# Draf Strategi: FoxVM ke LLVM IR
**Status:** Draf Awal
**Tanggal:** 12/12/2025

Dokumen ini mencatat perubahan arah strategis dari pengembangan VM kustom berbasis Rust (`morph_vm`) menuju penggunaan infrastruktur LLVM.

## 1. Latar Belakang
Pengembangan `morph_vm` (Rust) menemui jalan buntu pada integrasi Lexer dan kompleksitas manajemen memori (Borrow Checker) yang menghambat iterasi cepat. Untuk mencapai performa tinggi tanpa terjebak dalam detail implementasi VM tingkat rendah, diputuskan untuk beralih ke LLVM.

## 2. Tujuan
*   **Jangka Pendek:** Membersihkan codebase dari artefak Rust VM yang tidak terpakai (Archived).
*   **Jangka Menengah:** Mengembangkan backend baru di Kompiler Self-Hosted (`greenfield/kompiler`) yang dapat memancarkan (emit) **LLVM IR** (.ll) alih-alih Bytecode stack machine (.mvm).
*   **Jangka Panjang:** Menggunakan `llc` atau binding LLVM untuk mengompilasi kode Morph menjadi *native machine code*.

## 3. Rencana Tahapan (Tentatif)
1.  **Studi Struktur LLVM IR:** Memahami bagaimana memetakan konsep Morph (Dynamic Typing, Garbage Collection) ke LLVM IR. Mungkin memerlukan *Runtime Library* kecil (C/C++ atau Rust) untuk menangani GC dan Tipe Data.
2.  **Prototype Backend:** Membuat `generator_llvm.fox` di folder kompiler.
3.  **Runtime Support:** Memutuskan apakah akan menggunakan *Shadow Stack* untuk GC atau ref counting sederhana.

## 4. Referensi
*   Arsip Rust VM: `archived_morph/rust_vm_patch16_deprecated/`
