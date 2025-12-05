# Catatan Temuan Teknis

Dokumen ini mencatat hambatan teknis (technical debt), bug aneh, dan limitasi yang ditemukan selama pengembangan, untuk referensi perbaikan di masa depan.

## 1. Keterbatasan Parser Bootstrap (`transisi/crusher.py`)

*   **Isu:** Parser lama (Python-based) mengalami kegagalan (`PenguraiKesalahan: Ekspresi tidak terduga`) saat memparsing file `.fox` yang memiliki struktur kontrol (`jika`/`selama`) yang dalam atau kompleks di dalam metode, terutama jika melibatkan impor modul lain (`ambil_semua`).
*   **Dampak:** Pengembangan Native VM (`greenfield/fox_vm/prosesor.fox`) terhambat. Kita tidak bisa menaruh logika dispatch opcode lengkap (switch/if-else chain panjang) di satu file karena parser akan menolaknya.
*   **Status:** **Bypass**. Kode `prosesor.fox` disederhanakan (logika dievakuasi/dikomentari) agar bisa dimuat (loaded).
*   **Solusi Jangka Panjang:** Segera beralih menggunakan Parser Self-Hosted (`greenfield/crusher.fox`) untuk menjalankan toolchain, karena parser baru ini didesain lebih robust.

## 2. Limitasi Native Function Bridge

*   **Isu:** Native VM belum memiliki mekanisme `unpacking` argumen yang sempurna untuk memanggil fungsi host (Python/COTC) yang variadic.
*   **Workaround:** `greenfield/fox_vm/fungsi_native.fox` menggunakan pengecekan manual jumlah argumen (0 sampai 3) dan memanggil handler secara eksplisit.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
