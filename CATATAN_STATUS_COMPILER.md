# Catatan Status Compiler Morph - Update Sesi Ini

## Ringkasan Sesi (Advanced Features & Deep Analysis)

Sesi ini difokuskan pada verifikasi mendalam terhadap kapabilitas *Advanced Control Flow* dan *Error Handling* pada kompiler self-hosted. Analisis menunjukkan bahwa kompiler telah mendukung fitur-fitur modern seperti Pattern Matching dan FFI, meskipun masih ada beberapa catatan teknis terkait runtime.

### 1. Status Aktual: Self-Hosting Berjalan
-   **Kompiler (`greenfield/kompiler.fox`):**
    -   ✅ **Flow Control Lengkap:** Mendukung `jika` (dengan `lain_jika` bertingkat), `selama` (dengan `berhenti` dan `lanjutkan`).
    -   ✅ **Pattern Matching (`jodohkan`):** Terimplementasi penuh. Mendukung pola literal, wildcard (`_`), dan varian (`Sukses(x)`). **Catatan:** Menggunakan sintaks blok `| pola maka ...`.
    -   ✅ **Error Handling:** Mendukung `coba`, `tangkap e`, `akhirnya`, dan `lemparkan`. Kompilasi menghasilkan opcode `PUSH_TRY`, `POP_TRY`, `THROW`.
    -   ✅ **FFI (`pinjam`):** Mendukung impor modul host (Python) melalui `pinjam "modul" sebagai alias`.
    -   ✅ **Ternary Operator:** Mendukung ekspresi `kondisi ? benar : salah`.
    -   ✅ **Generator:** Mendukung `bekukan` (yield) dan `lanjut` (resume).
    -   ⚠️ **Fitur Belum Lengkap:**
        -   **Closure Penuh:** Variabel dari scope luar belum tertangkap otomatis (perlu passing manual).
        -   **Operator Bitwise:** Belum ditemukan implementasi untuk `&`, `|`, `^`, `<<`, `>>` di parser/kompiler.

-   **Parser (`crusher.fox`):**
    -   ✅ **Syntactic Sugar:** Mendukung inline `jika`, inisialisasi properti (`biar ini.x`), dan ternary operator.
    -   ⚠️ **Strictness:** Parser sangat ketat terhadap *newline* setelah keyword blok (`maka`, `akhir`), yang bisa membingungkan pengguna baru.

-   **Toolchain (`morph.fox`):**
    -   ✅ **Build & Run:** Mampu mengompilasi fitur kompleks di atas menjadi biner `.mvm` yang valid.
    -   ❌ **Run (Binary Bug):** Eksekusi file `.mvm` via `morph run` masih mengalami kendala deteksi format (dianggap source text).

### 2. Analisis & Temuan Teknis (Technical Debt)
-   **Runtime String Concatenation:** Objek error yang ditangkap blok `tangkap e` adalah dictionary. Melakukan `tulis("Error: " + e)` menyebabkan *panic* di VM. **Solusi:** Wajib menggunakan `teks(e)` atau implementasi `__str__` otomatis di level VM.
-   **Loop Stack Workaround:** Di `kompiler.fox`, manajemen `tumpukan_loop` menggunakan workaround slice (`iris`) untuk "pop", karena `list.pop()` standar belum tersedia/stabil di `cotc`. Ini berpotensi *memory leak* kecil saat kompilasi file sangat besar.
-   **Jodohkan Syntax:** Implementasi saat ini mewajibkan `maka` setelah pola (`| 1 maka`), berbeda dengan gaya fungsional umum (`| 1 =>`). Perlu konsistensi dokumentasi.

### 3. Eksperimen Logika (Paused)
-   **Deep Logic (Vzoel/ZFC):** Pengembangan fitur logika tingkat lanjut (Backtracking otomatis, Snapshot/Rollback VM) ditunda.

### 4. Roadmap & Prioritas Berikutnya
1.  **Standard Library (`cotc`):**
    -   Implementasi `list.pop()` yang efisien di `cotc` untuk menghapus workaround di kompiler.
    -   Implementasi `teks()` yang lebih robust untuk konversi objek error.
2.  **Fix Runner Biner:** Prioritas tinggi agar distribusi biner memungkinkan.
3.  **Dokumentasi Sintaks:** Memperbarui panduan sintaks terutama untuk `jodohkan` dan `try-catch` agar pengguna tidak bingung dengan aturan *newline*.
