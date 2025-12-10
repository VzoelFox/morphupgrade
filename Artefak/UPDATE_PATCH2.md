# Update Patch 2: Refactor, Fixes, and Universal Scope

**Tanggal:** 10/12/2025
**Engineer:** Jules AI Agent

## 1. Ringkasan Perubahan

Patch ini mencakup refactoring besar-besaran pada arsitektur compiler, perbaikan bug kritis pada analisis scope dan akses dictionary, serta penambahan fitur arsitektur "Universal Scope" untuk mendukung optimasi masa depan.

### A. Refactoring: Dispatcher Hell (`utama.fox`)
*   **Masalah:** Compiler sebelumnya menggunakan rantai `jika-lain-jika` (if-else) raksasa untuk mendispatch visitor AST, yang lambat dan sulit dirawat.
*   **Solusi:** Mengganti logika tersebut dengan `dispatch_map` (Hash Map) yang memetakan nama tipe AST ke fungsi visitor yang relevan.
*   **Dampak:** Kinerja kompilasi lebih efisien dan kode lebih bersih.

### B. Bug Fix: Analisis Scope (`analisis.fox`)
*   **Masalah:** Logika `_is_really_global` memiliki kesalahan off-by-one yang menyebabkan variabel closure teridentifikasi sebagai Global, menyebabkan VM crash saat mengaksesnya.
*   **Solusi:** Memperbaiki batas iterasi stack scope.
*   **Verifikasi:** Lulus tes regresi `repro_scope_bug.fox` dan `test_analisa_scope.fox`.

### C. Bug Fix: Akses Dictionary (`pernyataan.fox`)
*   **Masalah:** Compiler mengabaikan assignment ke indeks dictionary (`map["key"] = val`).
*   **Solusi:** Menambahkan dukungan node `Akses` pada visitor `Assignment`, yang sekarang mengemisikan opcode `STORE_INDEX`.
*   **Verifikasi:** Lulus tes `debug_kamus.fox`.

### D. Fitur Baru: Universal Scope (`analisis.fox`)
*   **Deskripsi:** Mengimplementasikan hierarki scope 3-lapis: `Universal -> Global -> Local`.
*   **Tujuan:** Memisahkan "Builtins" (seperti `tulis`, `panjang`) dari "User Globals". Ini penting untuk optimasi JIT/AOT di masa depan agar builtins bisa di-inline atau diproteksi.
*   **Implementasi:**
    *   Scope stack diinisialisasi dengan Universal Scope (Index 0) berisi whitelist builtins.
    *   Global Scope (User) berada di Index 1.
    *   Analisis scope mendeteksi akses ke builtins sebagai "Global Load" yang valid tanpa perlu deklarasi eksplisit.
    *   Mendukung shadowing (variabel lokal/global menimpa builtin).

## 2. Area yang Perlu Diperhatikan

### A. Railwush Side Effects
*   Modul `Railwush` (profiling/auth) secara inheren menulis ke disk (`checksum.dat`, `.mnet`).
*   **Penting:** Jangan menganggap file-file ini sebagai sampah. Mereka adalah bagian dari state aplikasi yang valid. CI telah dikonfigurasi untuk mengabaikan status git yang "kotor" akibat file ini.

### B. Native VM Variable Storage
*   Di Native VM (`fox_vm`), variabel global disimpan di `lokal` dari Frame Utama, bukan di `globals` dictionary (yang berisi builtins).
*   Namun, opcode `LOAD_VAR` memeriksa `lokal` lalu `globals`, sehingga akses tetap berjalan lancar.
*   **Potensi Isu:** Jika di masa depan kita membutuhkan akses langsung ke variabel global user dari fungsi lain tanpa passing frame, model ini mungkin perlu ditinjau ulang.

## 3. Saran Pengembangan Selanjutnya

1.  **Strict Mode Opsional:** Menambahkan mode kompilasi yang mengharuskan deklarasi variabel (`biar x`) sebelum penggunaan, untuk mencegah typo menjadi implicit global.
2.  **Optimasi Opcode:** Mengganti `LOAD_VAR` dengan `LOAD_FAST` (Local) dan `LOAD_GLOBAL` (Global/Universal) secara eksplisit di level generator untuk mengurangi overhead runtime lookup.
3.  **VM Hardening:** Menambahkan boundary check yang lebih ketat pada `fox_vm` untuk mencegah panic saat stack underflow/overflow.

## 4. Status Bug

*   [Fixed] Closure variable crash.
*   [Fixed] Dictionary assignment ignored.
*   [Fixed] Dispatcher performance bottleneck.
*   [Fixed] Error handling di Native VM (Traceback added).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.2 (Greenfield Patch 2)
tanggal  : 10/12/2025
