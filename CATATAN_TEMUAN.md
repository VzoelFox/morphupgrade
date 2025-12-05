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
    *   **Bytecode:** CodeObject Host menggunakan Tuple untuk instruksi, sedangkan Native VM mengharapkan List. Native VM harus melakukan konversi on-the-fly saat memuat kode Host.
    *   **Instantiation:** Native VM tidak bisa langsung memanggil Class Host (`MorphClass`) karena `tipe_objek` mengembalikan "objek" dan mereka bukan `FungsiNative`. Solusinya adalah menggunakan bridge `_is_callable` dan `_call_host` untuk mendelegasikan pemanggilan ke Host VM, yang menangani instansiasi dan inisialisasi.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
