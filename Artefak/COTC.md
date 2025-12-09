# Core of the Core (COTC)
COTC adalah pustaka standar (Standard Library) untuk bahasa pemrograman Morph yang diimplementasikan dengan pendekatan hibrida: logika tingkat tinggi dalam Morph dan operasi tingkat rendah melalui FFI ke Python (Host VM).

## Struktur Direktori

### `/greenfield/cotc/`
Direktori ini berisi modul-modul inti.

- **bytes.fox**: Utilitas manipulasi data biner (byte array).
- **unit.fox**: Definisi tipe data unit dasar.
- **warna.fox**: Konstanta dan fungsi untuk pewarnaan teks terminal (ANSI escape codes).

### `/greenfield/cotc/stdlib/`
Implementasi standar library utama.

- **teks.fox**: Manipulasi string (iris, gabung, cari).
- **matematika.fox**: Operasi matematika dasar dan lanjutan.
- **waktu.fox**: Fungsi terkait waktu dan penundaan (tidur).
- **sistem.fox**: Interaksi dengan sistem operasi (argumen, env).

### `/greenfield/cotc/protokol/`
Implementasi protokol komunikasi.

- **http.fox**: Klien dan server HTTP sederhana.
- **json.fox**: Parser dan serializer JSON.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.0.69 pre release
tanggal  : 10/12/2025
