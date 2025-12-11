# Roadmap Pengembangan Morph (FoxLLVM)

Dokumen ini merangkum status terkini dari pengembangan kompiler Morph dan menguraikan langkah-langkah selanjutnya menuju visi "FoxLLVM".

## 1. Status Terkini (Stabilisasi & Integrasi)

**Versi:** Morph v1 (Bootstrap Python)
**Status:** Stabil & Robust

### ✅ Pencapaian Terbaru (Integrasi Fox Engine)
1.  **Interpreter Stabil (`transisi/`):**
    -   Masalah *timeout* pada tes interpreter lama telah diatasi dengan mekanisme **Loop Protection**.
    -   Tes unit inti (`lx`, `crusher`, `translator`) lulus sepenuhnya.
2.  **Integrasi Keamanan Runtime:**
    -   Interpreter (`Penerjemah`) kini terhubung langsung dengan **Circuit Breaker** (`PemutusSirkuit`) dari `ManajerFox`.
    -   Sistem secara otomatis menghentikan eksekusi jika beban sistem berlebih, mencegah crash server/runtime.
3.  **Pustaka Standar Robust (File I/O):**
    -   Modul `berkas` telah direfaktor total.
    -   Tidak lagi melempar Exception Python mentah yang membuat crash.
    -   Menggunakan pola `Result` (Varian `Sukses | Gagal`) untuk penanganan error yang aman dan idiomatic.

---

## 2. Rencana Jangka Pendek (Minggu Depan)

Fokus: Menyelesaikan fondasi agar siap untuk menulis Compiler Self-Hosted.

### 2.1. Verifikasi FFI & Interop Python
-   **Masalah:** Fungsionalitas FFI masih dilaporkan memiliki banyak kegagalan tes (terutama tipe data kompleks).
-   **Tindakan:**
    -   Audit modul `transisi/ffi.py`.
    -   Perbaiki konversi tipe data antara Morph <-> Python (List, Dict).
    -   Pastikan `try-catch` Python di level FFI tidak membocorkan exception ke Morph.

### 2.2. Tuning JIT/AOT untuk I/O Baru
-   **Masalah:** Implementasi I/O baru menggunakan Dictionary wrapper. Perlu dipastikan JIT compiler (`tfox`) bisa mengoptimalkan ini.
-   **Tindakan:**
    -   Pastikan `RuntimeMORPHFox` menangani objek `JitModuleProxy` dengan benar saat mengakses fungsi yang mengembalikan Dictionary.
    -   Benchmark sederhana operasi file via JIT.

---

## 3. Rencana Jangka Menengah (Self-Hosting Phase 1)

Fokus: Memulai penulisan Compiler Morph menggunakan Bahasa Morph.

### 3.1. Struktur Proyek Morph
-   Membuat direktori `morph_src/` (atau `morph/`).
-   Mendefinisikan struktur modul standar: `compiler/lexer.fox`, `compiler/parser.fox`.

### 3.2. Implementasi Lexer di Morph
-   Menerjemahkan logika `transisi/lx.py` ke `morph_src/compiler/lexer.fox`.
-   Menggunakan fitur `jodohkan` dan `pilih` yang sudah stabil.
-   Memanfaatkan pustaka `berkas` robust untuk membaca file sumber.

### 3.3. Bootstrapping Loop
-   Menjalankan `lexer.fox` menggunakan interpreter Python (`transisi`).
-   Memverifikasi output token.

---

## 4. Visi Jangka Panjang (FoxLLVM)

Menuju ekosistem compiler adaptif.

### 4.1. FoxIR (Intermediate Representation)
-   Setelah parser self-hosted selesai, desain format IR (FoxIR) yang agnostik target.
-   FoxIR akan menjadi jembatan antara Morph frontend dan backend LLVM/Cranelift.

### 4.2. Adaptive Optimization
-   Mengembangkan strategi `ManajerFox` yang lebih cerdas (ML-based) untuk memilih kapan menggunakan JIT (WaterFox) vs AOT (ThunderFox) berdasarkan profil eksekusi runtime FoxIR.

### 4.3. Native Backend
-   Menggunakan LLVM (via binding) untuk menghasilkan native code dari FoxIR.
-   Tujuan akhir: `morph build main.fox` menghasilkan binary executable tanpa ketergantungan Python.

---

**Catatan Pengembang:**
-   Gunakan `git log` untuk melacak perubahan granular.
-   Selalu jalankan `pytest tests/unit` dan `tes_berkas_manual.fox` setelah melakukan perubahan pada core.
-   Dokumen ini menggantikan roadmap lama yang telah usang.

---

## 5. Greenfield Progress (2025)

Era Self-Hosting & Native VM.

### 5.1. Rust VM (`morph_vm`)
- [x] Inisialisasi Proyek Cargo (Patch 5).
- [x] Deserializer `.mvm` Lengkap (Patch 6).
- [x] Runtime Stack Machine Dasar (Patch 6).
- [x] Eksekusi Hello World (Patch 6).
- [ ] Implementasi Opcode Aritmatika & Logika.
- [ ] Integrasi Syscalls Native.

### 5.2. Compiler Hardening
- [x] Fix: Scope Analysis untuk Pattern Matching `jodohkan` (Patch 5).
- [x] Fix: Native VM Processor Safety (Patch 5).
- [x] CI/CD Automation (Patch 5).
