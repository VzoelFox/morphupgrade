# Catatan Status Compiler Morph - Update Sesi Ini

## Ringkasan Sesi (Standard Library Expansion)

Sesi ini berfokus pada pengayaan **Standard Library (`cotc`)** dengan struktur data fundamental. Fondasi VM dan Kompiler telah diperkuat untuk mendukung operasi `pop` secara efisien, membuka jalan bagi algoritma yang lebih kompleks.

### 1. Status Aktual: Kaya Fitur Dasar
-   **Standard Library (`cotc`):**
    -   ✅ **Struktur Data:** `Tumpukan` (Stack) dan `Antrian` (Queue) kini tersedia di `greenfield/cotc/struktur/`.
    -   ✅ **Utilitas List:** Fungsi `pop(list, index)` telah diimplementasikan secara native di VM dan diekspos ke Morph.
    -   ✅ **Naming Strategy:** Menggunakan `angkat` dan `copot` untuk metode penghapusan data guna menghindari konflik keyword parser.

-   **Infrastruktur VM & Opcodes:**
    -   ✅ **Intrinsic Support:** Penambahan Opcode `LEN` (62) dan `TYPE` (63) menyelesaikan crash pada optimasi compiler untuk fungsi `panjang()` dan `tipe_objek()`.
    -   ✅ **Native Pop:** Builtin `_pop_builtin` di VM kini mendukung argumen indeks opsional untuk efisiensi Queue.

### 2. Analisis & Temuan Teknis
-   **Parser Limitation:** Keyword seperti `ambil` tidak bisa digunakan sebagai nama properti (`obj.ambil`). Ini memaksa penggunaan nama alternatif (`angkat`).
    -   *Rekomendasi:* Di masa depan, parser perlu dilonggarkan agar menerima keyword sebagai identifier di posisi properti akses (`T.TITIK` -> `KEYWORD`).

### 3. Roadmap & Prioritas Berikutnya
1.  **Binary Runner (`morph run`):**
    -   Memungkinkan eksekusi langsung file `.mvm` via CLI self-hosted untuk distribusi aplikasi yang lebih cepat.
2.  **Pelonggaran Parser:**
    -   Memperbaiki parser agar properti objek bisa menggunakan nama keyword umum.
3.  **Dokumentasi API:**
    -   Membuat referensi API otomatis untuk `cotc`.
