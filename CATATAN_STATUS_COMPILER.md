# Catatan Status Compiler Morph - Update Sesi Ini

## Ringkasan Sesi (Verifikasi Aktual & Hutang Teknis)

Pada sesi ini, dilakukan verifikasi mendalam terhadap status aktual pengembangan compiler self-hosted (`greenfield/`) dibandingkan dengan dokumentasi yang ada. Ditemukan bahwa proyek telah resmi memasuki **Fase Self-Hosting**, namun terdapat beberapa hutang teknis pada alat bantu (tooling) dan VM.

### 1. Status Aktual: Self-Hosting Berjalan
-   **Kompiler (`greenfield/kompiler.fox`):**
    -   ✅ **Fungsional Dasar:** Mampu mengompilasi dan menjalankan skrip sederhana seperti `hello_world.fox` secara *on-the-fly*.
    -   ✅ **Fitur Terimplementasi:** Deklarasi fungsi, kelas, struktur kontrol (`jika`, `selama`), dan operasi dasar.
    -   ⚠️ **Fitur Belum Lengkap:** Assignment target kompleks (misal `a[0] = 1`), Closure penuh, dan operator bitwise.

-   **Toolchain (`greenfield/morph.fox`):**
    -   ✅ **Build:** Berhasil menghasilkan file biner `.mvm`.
    -   ✅ **Run (Source):** Berhasil menjalankan file `.fox` langsung.
    -   ❌ **Run (Binary):** Gagal menjalankan file `.mvm` karena mencoba membacanya sebagai teks UTF-8 (Bug Encoding).

### 2. Hutang Teknis & Bug Teridentifikasi

#### A. Tooling Verifikasi (`verify_greenfield.py`)
-   **Masalah:** Skript verifikasi gagal di Langkah 2 (Dependency Check) dengan laporan *false negative*. Ia tidak dapat menemukan file yang sebenarnya ada (misal `greenfield/cotc/stdlib/core.fox`).
-   **Dampak:** Menghambat validasi otomatis CI/CD.
-   **Status:** 🐛 **Broken**. Perlu perbaikan pada logika resolusi path impor.

#### B. VM Runtime (`standard_vm.py`)
-   **Masalah:** VM melempar `RuntimeError: Global 'utama' not found` di akhir eksekusi jika skrip tidak mendefinisikan fungsi `utama()`, meskipun skrip berjalan sukses.
-   **Dampak:** Membingungkan pengguna dengan pesan error "Unhandled Panic" setelah output yang sukses.
-   **Status:** 🐛 **Bug**. Perlu penanganan gracefull exit untuk skrip tanpa `utama`.

#### C. CLI Runner (`morph.fox`)
-   **Masalah:** Perintah `morph run file.mvm` crash dengan error decoding `utf-8`.
-   **Penyebab:** Runner mencoba membaca file biner menggunakan `baca()` (teks) alih-alih `baca_bytes()`.
-   **Status:** 🐛 **Bug**.

### 3. Rekomendasi Prioritas Berikutnya
1.  **Perbaiki `verify_greenfield.py`:** Agar kita bisa memvalidasi kemajuan secara otomatis.
2.  **Fix Runner Biner:** Agar siklus *compile-then-run* benar-benar terbukti berjalan (bukan hanya *compile-on-the-fly*).
3.  **Lengkapi Tes Compiler:** `run_ivm_tests.py` saat ini hanya menjalankan tes aritmatika dan logika dasar, belum menyentuh fitur compiler yang kompleks.

---
*Catatan Lama (Arsip)*

### Ringkasan Sesi (Robustness & Safety) [Sebelumnya]
... (Isi lama tetap relevan sebagai sejarah)
