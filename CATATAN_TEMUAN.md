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

*   **Isu:** Banyak modul inti `cotc` (seperti `netbase`) masih wrapper tipis.
*   **Status:** **BERJALAN (In Progress)**.
*   **Rencana Perbaikan:** Migrasi bertahap ke `foxys` (Intrinsik). Modul `netbase` lama telah diarsipkan ke `archived_morph/`.

## 7. Masalah Identitas Tipe (The Real "Heisenbug")

*   **Isu:** Serialisasi bytecode (`struktur.fox`) menggunakan `pinjam "builtins"` dan `py.type(val)` untuk deteksi tipe. Ini menyebabkan ketidakcocokan identitas tipe saat dijalankan di Native VM (di mana `tipe_objek(val)` mengembalikan string "angka", "teks", dll, bukan kelas Python).
*   **Status:** **LUNAS (Resolved)**.
*   **Solusi:** `struktur.fox` direfaktor total menjadi **Pure Morph**. Menggunakan `tipe_objek()` native dan deteksi nilai manual (misal: `val == int(val)` untuk integer vs float).

## 8. Konflik Nama Metode `punya`

*   **Isu:** Mendefinisikan metode instance bernama `punya(x)` pada kelas Morph (contoh: `Himpunan`) menyebabkan perilaku tidak terduga di `StandardVM`. Metode tersebut seolah-olah tidak dipanggil atau dibayangi oleh implementasi internal VM.
*   **Status:** **DIKETAHUI**.
*   **Solusi:** Gunakan nama lain seperti `memuat(x)` atau `memiliki(x)` untuk pengecekan keberadaan anggota dalam struktur data kustom.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
