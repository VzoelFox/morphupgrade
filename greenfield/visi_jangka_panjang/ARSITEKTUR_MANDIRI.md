# Visi Arsitektur Mandiri: Menuju Morph Native

Dokumen ini merangkum rencana jangka panjang untuk melepaskan ekosistem Morph dari ketergantungan terhadap Python (Host VM) dan mencapai kemandirian total melalui implementasi sistem memori tingkat rendah dan ekosistem driver mandiri.

## 1. Sistem Manajemen Memori (Morph-in-Morph)

Setelah **FoxVM Native** (yang ditulis dalam Morph) stabil, langkah selanjutnya adalah mengimplementasikan manajemen memori manual. Ini bertujuan untuk menghapus ketergantungan pada *Garbage Collector* (GC) Python dan membuka jalan menuju "Deep Logic" serta kompilasi ke WebAssembly (WASM).

### Prinsip Utama
*   **Linear Memory Model:** Memori fisik akan disimulasikan sebagai satu blok array raksasa (misalnya bytearray dari host). Pointer hanyalah *integer index* ke dalam array ini.
*   **Immutable Data Model:** Secara *default*, data bersifat *immutable*.
*   **Ownership Tanpa Borrowing:**
    *   Sistem kepemilikan tunggal (*Single Ownership*).
    *   Tidak ada *Borrowing* (peminjaman referensi yang kompleks).
    *   **Semantik:** Menggunakan pendekatan *Functional / Copy-on-Write*. Passing data antar fungsi hanya menyalin "pointer/index" (murah) karena data aslinya tidak bisa berubah.
    *   **Mutasi:** Jika ingin mengubah data, wajib melakukan **Manual Clone** (menyalin data ke lokasi memori baru).
*   **Manajemen Otomatis vs Manual:** Fokus pada pembebasan memori deterministik (via Region/Scope) dengan opsi *Basic GC* (Non-default) jika benar-benar dibutuhkan.

### Komponen Alokator
Sistem ini akan dibangun di atas beberapa strategi alokasi:
1.  **Region-Based Allocator (RB):** Untuk manajemen memori berbasis *scope*. Mendukung *Manual Free* per region.
2.  **Stack Allocator:** Alokasi super cepat (LIFO).
3.  **Frame Stack untuk VM:** Manajemen memori khusus untuk *Call Frames* VM.
4.  **Pool Allocator:** Untuk penggunaan ulang objek yang sering dibuat/dihapus.
5.  **Small Object Pool:** Optimasi khusus untuk objek kecil guna mengurangi fragmentasi.
6.  **Scoped Arena untuk Compiler:** Khusus untuk Compiler, memudahkan pembersihan memori massal setelah proses kompilasi selesai.
7.  **Symbol Table Immutable & String Interning:** Optimasi penyimpanan teks dan identifier agar hemat memori dan cepat dibandingkan.
8.  **Basic GC Optional (Non-default):** Kolektor sampah sederhana yang opsional, bukan mekanisme utama.

### Tujuan Implementasi
*   **Deep Logic & Time Travel:** Model *immutable* dan *linear memory* memungkinkan fitur **`bekukan` / `ingat` / `undur`** (snapshot & rollback) dilakukan dengan sangat efisien (menyalin state hanya butuh menyalin index/pointer atau blok memori mentah, bukan *deep copy* objek Python yang berat).
*   **WASM Backend:** Model linear ini memetakan secara langsung ke model memori WebAssembly.

---

## 2. Ekosistem Driver & Distribusi ("Star Spawn")

Visi kemandirian ini akan diwujudkan melalui seperangkat alat baru yang menggantikan peran Python sebagai *launcher* dan *package manager*.

### `star spawn` (Installer & Distribusi)
Perintah ini bertindak sebagai manajer paket dan installer sistem, mirip dengan `pip install`.

*   **Perintah:** `star spawn <nama_paket>.fall`
*   **Format `.fall`:** Format paket distribusi Morph. Berisi *binary* VM, *bytecode* library standar, dan aset yang siap "dilahirkan" ke dalam sistem.
*   **Fungsi:** Menginstal dependensi atau menyiapkan lingkungan runtime Morph di mesin host.

### `morph to` (Native Runner)
Ini adalah "Driver" utama yang akan menggantikan perintah `python3 -m ivm ...`.

*   **Perintah:** `morph to <file>.fox`
*   **Fungsi:** Menjalankan kode Morph menggunakan FoxVM Native yang telah terinstal.
*   **Tujuan:** Menjadi satu-satunya *entry point* yang dibutuhkan pengguna, sehingga Python tidak lagi terlihat oleh pengguna akhir.

---

## Roadmap Singkat

1.  **Fase 1 (Sekarang):** Stabilisasi FoxVM (Interpreter) di atas Host Python.
2.  **Fase 2:** Implementasi "Driver" (`morph to`) dan format distribusi (`.fall`).
3.  **Fase 3:** Implementasi Sistem Memori Manual (Allocator) di dalam FoxVM.
4.  **Fase 4:** Migrasi total ke backend Native/WASM dan pelepasan Python.
