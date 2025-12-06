# Catatan Temuan Teknis

Dokumen ini mencatat hambatan teknis (technical debt), bug aneh, dan limitasi yang ditemukan selama pengembangan, untuk referensi perbaikan di masa depan.

## 1. Keterbatasan Parser Bootstrap (`transisi/crusher.py`)

*   **Isu:** Parser lama (Python-based) mengalami kegagalan (`PenguraiKesalahan: Ekspresi tidak terduga`) saat memparsing file `.fox` yang memiliki struktur kontrol (`jika`/`selama`) yang dalam atau kompleks di dalam metode.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Refactoring kode self-hosted menjadi fungsi modular dan perbaikan logika parser. Toolchain Greenfield kini dapat dikompilasi dengan stabil.

## 2. Inkonsistensi Runner (`ivm/main.py`) pada Skrip Top-Level

*   **Isu:** Saat menjalankan file `.fox` yang didesain sebagai skrip prosedural (tanpa fungsi `utama`), runner memaksa injeksi pemanggilan `utama()`, menyebabkan error `RuntimeError: Global 'utama' not found` di akhir eksekusi.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Logika runner diperbarui untuk melakukan pengecekan dinamis (`if "utama" in vm.globals`) setelah eksekusi modul selesai, alih-alih memaksa kompilasi instruksi `CALL utama` secara statis.

## 3. Interop Native VM dengan Host Object

*   **Isu:** Native VM (Greenfield) yang berjalan di atas Host VM (StandardVM) memerlukan mekanisme khusus untuk berinteraksi dengan Objek Host (Python objects).
    *   **Globals:** Kode Host (seperti Lexer) mengakses variabel global modulnya. Native VM menggunakan `ini.globals` (Prosesor) secara default. Solusinya adalah menggunakan `ProxyHostGlobals` yang membungkus `__globals__` fungsi Host dan mengeksposnya ke Native VM via bridge `_host_contains` dan `_getitem`.
        *   *Catatan:* Saat menjalankan Host Method yang dikonversi ke Native Code (bukan dipanggil via bridge), Native VM menggunakan Global Processor (dict). Kita harus menyuntikkan dependensi (seperti `AST` atau `T`) ke dalam `cpu.globals` agar kode Native dapat menemukannya.
    *   **Bytecode:** CodeObject Host menggunakan Tuple untuk instruksi, sedangkan Native VM mengharapkan List. Native VM harus melakukan konversi on-the-fly saat memuat kode Host.
    *   **Instantiation:** Native VM tidak bisa langsung memanggil Class Host (`MorphClass`) karena `tipe_objek` mengembalikan "objek". Solusinya adalah menggunakan bridge `_is_callable` dan `_call_host` untuk mendelegasikan pemanggilan ke Host VM.

## 4. Warning "Lokal tidak ditemukan"

*   **Isu:** Saat menjalankan Parser di Native VM, muncul banyak peringatan `Error: Lokal tidak ditemukan: tX` (variabel temporer). Namun, eksekusi tetap berhasil.
*   **Analisa:** Kemungkinan compiler `ivm` menghasilkan kode `LOAD_LOCAL` untuk variabel temporer pada jalur eksekusi tertentu sebelum `STORE_LOCAL` dieksekusi (atau VM Native menanganinya berbeda dari StandardVM). Native VM mendorong `nil` saat variabel tidak ditemukan, yang tampaknya ditangani dengan aman oleh logika program.

## 5. Konflik Keyword di Argumen Parser Bootstrap

*   **Isu:** Parser Bootstrap (`transisi/crusher.py`) gagal memparsing pemanggilan fungsi jika argumennya menggunakan nama yang sama dengan keyword tertentu (contoh: `setitem(..., tulis)` dimana `tulis` adalah keyword). Error yang muncul adalah `PenguraiKesalahan: Ekspresi tidak terduga`.
*   **Status:** **Workaround Aktif**.
*   **Solusi:** Hindari penggunaan keyword sebagai identifier langsung dalam argumen. Gunakan akses kamus pada objek modul (misal: `CoreLib["tulis"]`) atau bungkus dalam fungsi helper.

## 6. Ketergantungan Berat pada FFI (`pinjam`) di Standard Library

*   **Isu:** Banyak modul inti `cotc` (seperti `bytes`, `netbase`, `json`) yang hanya berupa wrapper tipis di atas pustaka Python (`struct`, `os`, `json`). Ini menghalangi kemandirian (self-hosting) penuh VM dan Compiler.
*   **Status:** **Hutang Teknis (High)**.
*   **Rencana Perbaikan:**
    1.  **`bytes.fox` (Priority):** Implementasi Native Packing/Unpacking (Little Endian) menggunakan bitwise ops.
    2.  **`struktur/*.fox`:** Implementasi `Set` (Himpunan) native.
    3.  **`json` (Medium):** Implementasi JSON Parser native di Morph.
    4.  **`netbase` (Low):** Tetap menggunakan FFI sampai ada OS Layer.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
