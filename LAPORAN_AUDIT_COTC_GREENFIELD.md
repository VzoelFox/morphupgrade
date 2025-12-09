# Laporan Audit Arsitektur: COTC & Greenfield

**Penulis:** Jules (AI Assistant)
**Tanggal:** 25 Oktober 2023 (Simulasi)
**Lingkup:** `greenfield/cotc` (Standard Library) dan `greenfield/fox_vm` (Native VM).

---

## 1. Ringkasan Eksekutif

Ekosistem `greenfield` menunjukkan struktur proyek yang ambisius dengan pemisahan tanggung jawab yang jelas antara Compiler, VM, dan Standard Library (`cotc`).

*   **Standard Library (`cotc`)**: Berada pada tahap "Hybrid", di mana logika tingkat tinggi ditulis dalam Morph, tetapi fungsi inti (kriptografi, I/O, waktu) masih sangat bergantung pada `pinjam` (FFI ke Python). Ini strategi bootstrap yang valid namun menciptakan hutang teknis "kemandirian".
*   **Native VM (`fox_vm`)**: Mengejutkan, implementasi VM cukup matang. Interpreter loop (`prosesor.fox`) menangani puluhan opcode, stack operations, dan bahkan exception handling. Namun, ia berjalan di atas abstraksi data host (menggunakan List/Dict Python via FFI), bukan raw memory management.
*   **Compiler**: Seperti temuan sebelumnya, merupakan mata rantai terlemah (missing implementation).

---

## 2. Analisa Mendalam: `cotc` (Core of the Core)

Direktori ini adalah calon pustaka standar Morph.

### 2.1. Ketergantungan FFI (`pinjam`)
Penggunaan `pinjam` masih sangat masif.
*   **Railwush (`railwush/`):** Modul jaringan dan profil ini hampir sepenuhnya wrapper Python.
    *   `cryptex.fox`: Menggunakan `hashlib`, `os`, `datetime` dari Python. Algoritma enkripsi "XOR Cipher" diimplementasikan manual (bagus), tapi key generation masih pakai Python.
    *   `profil.fox`: Menggunakan `json` Python untuk serialisasi.
*   **Core (`stdlib/core.fox`):** Berfungsi sebagai *bridge* ke fungsi intrinsik VM. Ini pola yang bagus; memisahkan deklarasi fungsi standar dari implementasi internal VM.

### 2.2. Kualitas Kode
*   **Abstraksi IO (`io/berkas.fox`)**: Desain kelas `Berkas` cukup rapi dan *Pythonic* (ada `buka`, `tutup`, `baca`). Wrapper `baca_bytes` memudahkan penggunaan umum.
*   **Konsistensi**: Penamaan fungsi konsisten menggunakan Snake Case (`baca_bytes`, `tulis_file`).

---

## 3. Analisa Mendalam: `fox_vm` (Native VM)

Ini adalah implementasi VM Morph yang ditulis *dalam bahasa Morph sendiri*.

### 3.1. Prosesor (`prosesor.fox`)
Jantung dari VM.
*   **Interpreter Loop**: Menggunakan `selama` loop sederhana dengan limit langkah (1.000.000) untuk mencegah infinite loop saat dev.
*   **Opcode Dispatch**: Menggunakan rangkaian `jika ... lain jika ...` raksasa. Ini tidak efisien dibandingkan *jump table* (yang sulit diimplementasikan tanpa pointer function) atau *match/case* yang teroptimasi, tapi fungsional.
*   **Error Handling**: Sudah mendukung instruksi `PUSH_TRY`, `POP_TRY`, dan `THROW`. Logika stack unwinding di `_tangani_error` terlihat benar.

### 3.2. Integrasi Host
VM ini "curang" dengan cerdas. Alih-alih mengelola heap memori byte-per-byte:
*   **Objek**: Menggunakan Dictionary Python (via Morph Dict) untuk merepresentasikan Instance Kelas dan Modul.
*   **ProxyHostGlobals**: Kelas pintar yang menjembatani akses global Morph ke dictionary Python Host. Ini memungkinkan VM Morph mengakses fungsi native Python tanpa wrapper manual satu per satu.

---

## 4. Evaluasi Struktural

| Komponen | Status | Kualitas Desain | Kemandirian (Non-Python) |
| :--- | :--- | :--- | :--- |
| **COTC (Stdlib)** | Berfungsi (Hybrid) | Tinggi (API bersih) | Rendah (Banyak `pinjam`) |
| **Fox VM** | Fungsional | Sedang (Opcode dispatch lambat) | Sedang (Logika Morph, Data Python) |
| **Compiler** | **RUSAK** | Tinggi (Visitor Pattern) | Tinggi (Tidak pakai `ast` Python) |

---

## 5. Kesimpulan Akhir

Struktur `greenfield` membuktikan bahwa visi "Self-Hosting" Morph *bukan omong kosong*, tetapi status saat ini lebih mirip **prototype arsitektur** daripada produk jadi.

1.  **Fundamental VM Kuat**: Logika eksekusi bytecode di `fox_vm` sudah siap.
2.  **Stdlib Siap Pakai**: API `cotc` sudah cukup untuk menulis program CLI sederhana.
3.  **Compiler Bolong**: Satu-satunya penghalang self-hosting adalah kosongnya `pernyataan.fox`. Jika file ini diisi, sistem ini *bisa* hidup.

**Rekomendasi:** Perbaiki `compiler/pernyataan.fox` adalah satu-satunya jalan maju. Jangan sentuh `cotc` atau `fox_vm` dulu karena mereka sudah cukup baik untuk menopang compiler saat ini.
