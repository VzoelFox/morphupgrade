# Catatan Temuan Teknis

Dokumen ini mencatat hambatan teknis (technical debt), bug aneh, dan limitasi yang ditemukan selama pengembangan, untuk referensi perbaikan di masa depan.

## 1. Keterbatasan Parser Bootstrap (`transisi/crusher.py`)

*   **Isu:** Parser lama (Python-based) mengalami kegagalan (`PenguraiKesalahan: Ekspresi tidak terduga`) saat memparsing file `.fox` yang memiliki struktur kontrol (`jika`/`selama`) yang dalam atau kompleks di dalam metode, terutama jika melibatkan impor modul lain (`ambil_semua`).
*   **Dampak:** Pengembangan Native VM (`greenfield/fox_vm/prosesor.fox`) terhambat.
*   **Status:** **Teratasi (Mitigasi)**.
*   **Solusi:** Refactoring kode self-hosted menjadi fungsi-fungsi modular yang lebih kecil (mengurangi kedalaman indentasi) terbukti memungkinkan parser lama untuk memproses file kompleks seperti `greenfield/kompiler/pernyataan.fox`. Selain itu, Toolchain Greenfield (`morph.mvm`) yang dikompilasi dengan metode ini siap digunakan sebagai parser yang lebih kuat.

## 2. Limitasi Native Function Bridge

*   **Isu:** Native VM belum memiliki mekanisme `unpacking` argumen yang sempurna untuk memanggil fungsi host (Python/COTC) yang variadic.
*   **Workaround:** `greenfield/fox_vm/fungsi_native.fox` menggunakan pengecekan manual jumlah argumen (0 sampai 3) dan memanggil handler secara eksplisit.

---
*Dibuat oleh Jules saat Fase Implementasi Native VM.*
