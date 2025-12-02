# Catatan Status Compiler Morph - Update Sesi Ini

## Ringkasan Sesi (Verifikasi Aktual & Migrasi Tooling)

Pada sesi ini, dilakukan verifikasi mendalam terhadap status aktual pengembangan compiler self-hosted (`greenfield/`) dan pembersihan alat verifikasi (tooling).

### 1. Status Aktual: Self-Hosting Berjalan
-   **Kompiler (`greenfield/kompiler.fox`):**
    -   ✅ **Fungsional Dasar:** Mampu mengompilasi dan menjalankan skrip sederhana seperti `hello_world.fox` secara *on-the-fly*.
    -   ✅ **Fitur Terimplementasi:** Deklarasi fungsi, kelas, struktur kontrol (`jika`, `selama`), dan operasi dasar.
    -   ⚠️ **Fitur Belum Lengkap:** Assignment target kompleks, Closure penuh, dan operator bitwise.

-   **Toolchain (`greenfield/morph.fox`):**
    -   ✅ **Build:** Berhasil menghasilkan file biner `.mvm`.
    -   ✅ **Run (Source):** Berhasil menjalankan file `.fox` langsung.
    -   ❌ **Run (Binary):** Gagal menjalankan file `.mvm` karena bug decoding encoding.

### 2. Migrasi Tooling Verifikasi
-   **Alat Utama:** `greenfield/verifikasi.fox` (Self-Hosted).
    -   Telah diperbaiki untuk mendukung resolusi path `cotc(stdlib)` dan fallback path `greenfield/`.
    -   Sekarang menjadi standar verifikasi (Sintaks & Dependensi).
-   **Alat Arsip:** `verify_greenfield.py` (Python).
    -   Dipindahkan ke `tests/legacy_disabled/` untuk mencegah kebingungan.

### 3. Hutang Teknis Teridentifikasi

#### A. VM Runtime (`standard_vm.py`)
-   **Masalah:** VM melempar `RuntimeError: Global 'utama' not found` jika skrip top-level tidak mendefinisikan `utama()`.
-   **Status:** 🐛 **Bug**. Perlu penanganan gracefull exit.

#### B. CLI Runner (`morph.fox`)
-   **Masalah:** Perintah `morph run file.mvm` crash dengan error decoding `utf-8`.
-   **Status:** 🐛 **Bug**.

### 4. Rekomendasi Prioritas Berikutnya
1.  **Fix Runner Biner:** Agar siklus *compile-then-run* benar-benar terbukti berjalan.
2.  **Lengkapi Tes Compiler:** Menggunakan `run_ivm_tests.py` dengan cakupan lebih luas.

---
*Catatan Lama (Arsip)*

### Ringkasan Sesi (Robustness & Safety) [Sebelumnya]
... (Isi lama tetap relevan sebagai sejarah)
