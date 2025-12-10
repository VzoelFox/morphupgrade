# Core of the Core (COTC)
COTC adalah pustaka standar (Standard Library) untuk bahasa pemrograman Morph yang diimplementasikan dengan pendekatan hibrida: logika tingkat tinggi dalam Morph (Pure Morph) dan operasi tingkat rendah melalui FFI ke Python (Host VM) jika diperlukan.

## Struktur Direktori

### `/greenfield/cotc/`
Direktori ini berisi modul-modul inti dan definisi tipe dasar.

- **bytes.fox**: Utilitas manipulasi data biner (byte array).
- **unit.fox**: Definisi tipe data unit dasar dan asersi tes.
- **warna.fox**: Konstanta dan fungsi untuk pewarnaan teks terminal (ANSI escape codes).

### `/greenfield/cotc/stdlib/`
Implementasi standar library utama yang sering digunakan.

- **core.fox**: Fungsi built-in inti (`panjang`, `tambah`, `teks`) dan shim VM.
- **teks.fox**: Manipulasi string (`iris`, `gabung`, `cari`).
- **loader.fox**: Logika pemuat binary `.mvm`.

### `/greenfield/cotc/struktur/`
Implementasi struktur data klasik.

- **tumpukan.fox**: Stack (LIFO).
- **antrian.fox**: Queue (FIFO).
- **himpunan.fox**: Set (Unik).

### `/greenfield/cotc/matematika/`
Algoritma matematika.

- **dasar.fox**: Aritmatika dasar.
- **trigonometri.fox**: Fungsi sin, cos, tan (Pure Morph).

### `/greenfield/cotc/io/`
Input/Output sistem.

- **berkas.fox**: Manipulasi file (baca, tulis, bytes, teks).

### `/greenfield/cotc/logika/`
Logika Lanjutan & AI Simbolik.

- **unifikasi.fox**: Algoritma unifikasi Robinson.
- **prop.fox**: Logika Proposisional.
- **zfc.fox**: Himpunan tak hingga (Generator).

### `/greenfield/cotc/protokol/`
Implementasi protokol komunikasi.

- **http.fox**: Klien dan server HTTP sederhana.
- **json.fox**: Parser dan serializer JSON.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.3 (Greenfield Patch 3)
tanggal  : 10/12/2025
