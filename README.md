# Morph: Bahasa Pemrograman Self-Hosting

Morph adalah bahasa pemrograman dinamis yang sedang dalam tahap pengembangan aktif dengan tujuan utama mencapai kemampuan **self-hosting** penuh (bahasa yang ditulis dengan bahasa itu sendiri).

## Status Proyek
Saat ini proyek berada dalam fase **Bootstrap / Self-Hosting**. Kompiler utama (`greenfield`) sudah ditulis dalam Morph dan dijalankan di atas mesin virtual Python (`ivm`).

*   **Status**: *In Progress* (Pengembangan Aktif)
*   **Target**: Memindahkan seluruh logika *toolchain* dari Python ke Morph murni.

## Arsitektur

Proyek ini terbagi menjadi tiga komponen utama:

1.  **`greenfield/` (The New World)**
    *   Berisi kode sumber Morph yang *self-hosted*.
    *   Termasuk kompiler (`kompiler.fox`), lexer, parser, dan standar library (`cotc` - *Core of the Core*).
    *   Ini adalah masa depan dari bahasa Morph.

2.  **`ivm/` (The Runtime)**
    *   *Implementation Virtual Machine*: Runtime berbasis Python yang menjalankan *bytecode* Morph.
    *   Bertanggung jawab untuk menjembatani kode Morph dengan sistem operasi (via FFI) selama fase bootstrap.

3.  **`transisi/` (The Bridge)**
    *   Komponen *legacy* berbasis Python (Parser & Lexer) yang digunakan untuk mem-bootstrap sistem awal sebelum parser Morph stabil sepenuhnya.

## Fitur Bahasa Terbaru

-   **Interpolasi String:**
    ```morph
    biar nama = "Dunia"
    tulis("Halo {nama}") # Output: Halo Dunia
    ```

-   **Destructuring Assignment:**
    ```morph
    biar [x, y] = [10, 20]
    tulis(x) # 10
    tulis(y) # 20
    ```

-   **Blok Satu Baris:**
    ```morph
    jika benar maka tulis("Ya") akhir
    ```

## Cara Penggunaan

Untuk menjalankan skrip Morph, Anda dapat menggunakan *wrapper script* `morph` atau memanggil modul `ivm` secara langsung.

### Prasyarat
Pastikan dependensi Python terpenuhi:
```bash
pip install -r requirements.txt
```

### Menjalankan Skrip
Jalankan file `.fox` menggunakan perintah:

```bash
# Menggunakan wrapper script (Linux/Mac)
./morph run greenfield/examples/hello_world.fox

# Atau menggunakan Python langsung
python3 -m ivm.main greenfield/examples/hello_world.fox
```

### Verifikasi Sistem
Untuk memverifikasi skrip (sintaks & dependensi), gunakan perintah berikut:

```bash
# Contoh memverifikasi file compiler
python3 -m ivm.main greenfield/verifikasi.fox greenfield/kompiler.fox
```

## Kontribusi
Fokus pengembangan saat ini adalah menstabilkan `greenfield/kompiler.fox` dan memperluas cakupan tes di `greenfield/cotc`.

---
*Dokumentasi ini diperbarui secara otomatis oleh Agen AI (Jules).*
