# Catatan Temuan Teknis

Dokumen ini mencatat hambatan teknis (technical debt), bug aneh, dan limitasi yang ditemukan selama pengembangan, untuk referensi perbaikan di masa depan.

## 1. Keterbatasan Parser Bootstrap (`transisi/crusher.py`)

*   **Isu:** Parser lama (Python-based) mengalami kegagalan (`PenguraiKesalahan: Ekspresi tidak terduga`) saat memparsing file `.fox` yang memiliki struktur kontrol (`jika`/`selama`) yang dalam atau kompleks di dalam metode.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Refactoring kode self-hosted menjadi fungsi modular dan perbaikan logika parser. Toolchain Greenfield kini dapat dikompilasi dengan stabil.

## 2. Inkonsistensi Runner (`ivm/main.py`) pada Skrip Top-Level

*   **Isu:** Saat menjalankan file `.fox` yang didesain sebagai skrip prosedural (tanpa fungsi `utama`), runner memaksa injeksi pemanggilan `utama()`, menyebabkan error `RuntimeError: Global 'utama' not found` di akhir eksekusi.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Logika runner diperbarui untuk melakukan pengecekan dinamis (`if "utama" in vm.globals`) setelah eksekusi modul selesai.

## 3. Interop Native VM dengan Host Object

*   **Isu:** Native VM (Greenfield) yang berjalan di atas Host VM (StandardVM) memerlukan mekanisme khusus untuk berinteraksi dengan Objek Host (Python objects).
    *   **Globals:** Kode Host (seperti Lexer) mengakses variabel global modulnya. Native VM menggunakan `ini.globals` (Prosesor) secara default. Solusinya adalah menggunakan `ProxyHostGlobals`.
    *   **Instantiation:** Native VM tidak bisa langsung memanggil Class Host (`MorphClass`). Solusinya adalah bridge `_buat_instance` dan `_is_callable`.

## 4. Warning "Lokal tidak ditemukan" & "Variabel tidak ditemukan"

*   **Isu:** Saat menjalankan Parser di Native VM, muncul banyak peringatan `Error: Lokal tidak ditemukan: tX` (variabel temporer) dan `Error: Variabel tidak ditemukan`.
*   **Analisa:** Kemungkinan compiler `ivm` menghasilkan kode `LOAD_LOCAL` sebelum `STORE_LOCAL` pada path tertentu. Untuk `Variabel tidak ditemukan`, dicurigai masalah pada `LOAD_GLOBAL` di Native VM saat mengakses `cpu.globals` yang merupakan dictionary Host.

## 5. Konflik Keyword di Argumen Parser Bootstrap

*   **Isu:** Parser Bootstrap (`transisi/crusher.py`) gagal memparsing pemanggilan fungsi jika argumennya menggunakan nama yang sama dengan keyword tertentu.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Parser diperbarui untuk mengizinkan token keyword tertentu sebagai identifier.

## 6. Ketergantungan Berat pada FFI (`pinjam`) di Standard Library

*   **Isu:** Banyak modul inti `cotc` (seperti `netbase`) masih wrapper tipis.
*   **Status:** **BERJALAN (In Progress)**.
*   **Rencana Perbaikan:** Migrasi bertahap ke `foxys` (Intrinsik).

## 7. Limitasi Parser terhadap Blok Satu Baris (`jodohkan`)

*   **Isu:** Parser Host (`transisi/crusher.py`) memaksa adanya baris baru setelah `maka` dalam blok `jodohkan`, melarang penulisan `| pola maka pernyataan` dalam satu baris.
*   **Status:** **DIKETAHUI (Workaround)**.
*   **Solusi:** Gunakan blok multi-baris untuk kompatibilitas.

## 8. Masalah File System di Lingkungan Pengembangan

*   **Isu:** Operasi `overwrite_file_with_block` terkadang gagal memperbarui file secara persisten dalam sesi agen, memerlukan strategi `delete` lalu `create`.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
