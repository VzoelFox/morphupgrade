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
*   **Status:** **LUNAS (Resolved)** (Sebagian Besar).
*   **Analisa & Solusi:**
    *   **Akses Globals:** `cpu.globals` sering terdeteksi sebagai "Host Object" (bukan Native Dict) di dalam VM, menyebabkan kegagalan method `.ambil()`.
    *   **Fix:** `greenfield/fox_vm/prosesor.fox` diperbarui dengan logika `coba-tangkap` di `_ops_variabel`. Ia mencoba akses indeks (`[]`) terlebih dahulu (standar untuk Dict/Host Dict), lalu fallback ke `.ambil()` (untuk Proxy).
    *   **Lexer Execution:** Memerlukan injeksi globals manual (seperti di `test_vm_lexer_wip.fox`) atau pembungkusan `ObjekKode` dalam struktur `Fungsi` agar VM tahu konteks globals-nya.

## 5. Konflik Keyword di Argumen Parser Bootstrap

*   **Isu:** Parser Bootstrap (`transisi/crusher.py`) gagal memparsing pemanggilan fungsi jika argumennya menggunakan nama yang sama dengan keyword tertentu.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Parser diperbarui untuk mengizinkan token keyword tertentu sebagai identifier.

## 6. Ketergantungan Berat pada FFI (`pinjam`) di Standard Library

*   **Isu:** Banyak modul inti `cotc` (seperti `netbase`) masih wrapper tipis dan bergantung pada library Python berat (`cryptography`).
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:**
    *   **Migrasi ke `railwush`:** Modul `netbase` direstrukturisasi menjadi `greenfield/cotc/railwush`.
    *   **Native Crypto (`cryptex.fox`):** Implementasi `cryptography` Python diganti dengan algoritma XOR Cipher + Base64 yang ditulis dalam Pure Morph dan wrapper `hashlib` stdlib. Dependensi eksternal dihilangkan.

## 7. Masalah Identitas Tipe (The Real "Heisenbug")

*   **Isu:** Serialisasi bytecode (`struktur.fox`) menggunakan `pinjam "builtins"` dan `py.type(val)` untuk deteksi tipe. Ini menyebabkan ketidakcocokan identitas tipe saat dijalankan di Native VM.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** `struktur.fox` direfaktor total menjadi **Pure Morph**.

## 8. Bug Imutabilitas Scope Global (Compiler Logic Error)

*   **Isu:** Variabel global modul tidak bisa diubah nilainya menggunakan `ubah` di dalam fungsi. Nilai selalu kembali ke nilai awal setelah fungsi selesai.
*   **Status:** **LUNAS (Resolved)**.
*   **Analisa:** `ScopeAnalyzer` di `ivm/compiler.py` memiliki bug logika di mana ia secara agresif menganggap semua target `Assignment` (`ubah`) sebagai deklarasi variabel lokal. Ini menyebabkan `STORE_LOCAL` di-emit alih-alih `STORE_GLOBAL`.
*   **Solusi:**
    1.  Menghapus `visit_Assignment` dari `ScopeAnalyzer`. Assignment tidak lagi menciptakan variabel lokal baru.
    2.  Menambahkan visitor eksplisit `visit_CobaTangkap` dan `visit_Jodohkan` untuk memastikan variabel yang diperkenalkan oleh blok `tangkap` dan pola `jodohkan` tetap terdaftar sebagai lokal.

## 9. Metode String Primitif Hilang

*   **Isu:** String literal (tipe primitif `str`) gagal memanggil metode standar Morph (`.kecil()`, `.besar()`) karena VM tidak memiliki mapping atribut untuk tipe primitif, mengharuskan pembungkusan manual dengan kelas `Teks`.
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** Memperbarui `StandardVM` (`ivm/vms/standard_vm.py`) pada instruksi `LOAD_ATTR` untuk mendeteksi objek string dan memetakan nama metode Indonesia ke metode Python native secara otomatis.

## 10. Kekurangan Cakupan Tes Legacy

*   **Isu:** Skrip tes lama (`run_ivm_tests.py` dan tes di folder `tests/`) banyak yang usang atau gagal dijalankan karena perubahan arsitektur VM (Native vs Bootstrap).
*   **Status:** ⚠️ **WIP (Work In Progress)**.
*   **Mitigasi:** Fokus verifikasi saat ini beralih ke tes mandiri (`greenfield/examples/test_*.fox`). Tes legacy perlu diaudit ulang atau dihapus jika tidak lagi relevan.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM & Migrasi Railwush.*
