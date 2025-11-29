# Dokumentasi Standard Library (Self-Hosted)

Direktori ini (`greenfield/cotc/stdlib/`) berisi implementasi Pustaka Standar Morph yang ditulis dalam bahasa Morph murni (Pure Morph) atau antarmuka intrinsik ke VM.

## Modul Tersedia

### 1. `teks.fox`
Modul untuk manipulasi string (teks).

**Fungsi Utama:**
- `iris(objek, start, stop)`
  - **Deskripsi:** Mengambil bagian (substring/slice) dari teks atau daftar.
  - **Efisiensi:** Menggunakan Opcode VM Native (`Op.SLICE`) sehingga berjalan dalam waktu O(k), jauh lebih cepat daripada loop manual.
  - **Parameter:**
    - `objek`: String atau List.
    - `start`: Indeks awal (inklusif).
    - `stop`: Indeks akhir (eksklusif). Jika `nil`, akan mengambil sampai akhir.
  - **Contoh:**
    ```morph
    dari "cotc(stdlib)/teks.fox" ambil_sebagian iris
    biar s = "Halo Dunia"
    tulis(iris(s, 0, 4)) # Output: "Halo"
    ```

### 2. `warna.fox`
Modul definisi konstanta warna ANSI untuk terminal.
Harus diimpor dari `cotc/warna.fox` (level parent) jika belum dipindahkan, atau sesuaikan path.
*Catatan: Saat ini file fisik ada di `greenfield/cotc/warna.fox`.*

**Konstanta:**
- `MERAH`, `HIJAU`, `KUNING`, `BIRU`
- `RESET`, `TEBAL`

**Penggunaan:**
Digunakan bersama blok `warnai`:
```morph
warnai MERAH maka
    tulis("Ini Error!")
akhir
```
