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

## 3. Limitasi Native Function Bridge

*   **Isu:** Native VM belum memiliki mekanisme `unpacking` argumen yang sempurna untuk memanggil fungsi host (Python/COTC) yang variadic secara dinamis tanpa mengetahui arity sebelumnya.
*   **Workaround:** `greenfield/fox_vm/fungsi_native.fox` menggunakan pengecekan manual jumlah argumen (0 sampai 3) dan memanggil handler secara eksplisit.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
