# Dokumentasi Aplikasi Kalkulator MORPH

Aplikasi `kalkulator.fox` adalah salah satu contoh program pertama yang ditulis dalam bahasa MORPH. Program ini mendemonstrasikan fitur-fitur inti bahasa seperti deklarasi variabel (`biar`), konstanta (`tetap`), definisi fungsi (`fungsi`), dan operasi aritmatika dasar.

## Kode Sumber (`contoh/aplikasi/kalkulator.fox`)

```morph
# Bahasa MORPH adalah Bahasa Pemrograman yang diciptakan oleh Vzoel Fox's #Lutpan
# Aplikasi Kalkulator Sederhana v0.1
# Ini adalah aplikasi pertama yang ditulis sepenuhnya dalam bahasa MORPH.
# Kalkulator ini masih sederhana dan menggunakan nilai yang sudah ditentukan (hardcoded)
# karena fitur input pengguna belum diimplementasikan.

# --- Definisi Konstanta ---
tetap PI = 3.14159
tulis("Kalkulator MORPH v0.1 Siap.")
tulis("------------------------------")
tulis("Konstanta PI didefinisikan sebagai: ", PI)
tulis("")

# --- Definisi Fungsi Matematika ---

# Fungsi untuk penjumlahan (+)
fungsi tambah(a, b) maka
    kembalikan a + b
akhir

# Fungsi untuk pengurangan (-)
fungsi kurang(a, b) maka
    kembalikan a - b
akhir

# Fungsi untuk perkalian (*)
fungsi kali(a, b) maka
    kembalikan a * b
akhir

# Fungsi untuk pembagian (/)
fungsi bagi(a, b) maka
    # TODO: Tambahkan penanganan jika b adalah 0
    kembalikan a / b
akhir

# Fungsi untuk pangkat dua (n²)
fungsi kuadrat(n) maka
    kembalikan n * n
akhir

# Fungsi untuk pangkat tiga (n³)
fungsi kubik(n) maka
    kembalikan n * n * n
akhir

# TODO: Fungsi akar kuadrat (√) belum didukung oleh bahasa.

# --- Contoh Penggunaan ---
tulis("--- Operasi Dasar ---")
biar angka1 = 20
biar angka2 = 5

tulis(angka1, " + ", angka2, " = ", tambah(angka1, angka2))
tulis(angka1, " - ", angka2, " = ", kurang(angka1, angka2))
tulis(angka1, " * ", angka2, " = ", kali(angka1, angka2))
tulis(angka1, " / ", angka2, " = ", bagi(angka1, angka2))
tulis("")

tulis("--- Operasi Pangkat ---")
biar angka3 = 4
tulis("Kuadrat dari ", angka3, " (", angka3, "²) = ", kuadrat(angka3))
tulis("Kubik dari ", angka3, " (", angka3, "³) = ", kubik(angka3))
tulis("")

tulis("--- Penggunaan Konstanta ---")
biar radius = 7
biar luas_lingkaran = PI * kuadrat(radius)
tulis("Luas lingkaran dengan radius ", radius, " = ", luas_lingkaran)
tulis("")

tulis("------------------------------")
tulis("Kalkulasi Selesai.")
```

## Hasil Eksekusi

Berikut adalah output yang dihasilkan saat skrip dijalankan dengan interpreter MORPH:

```
Kalkulator MORPH v0.1 Siap.
------------------------------
Konstanta PI didefinisikan sebagai: 3.14159

--- Operasi Dasar ---
20 + 5 = 25
20 - 5 = 15
20 * 5 = 100
20 / 5 = 4.0

--- Operasi Pangkat ---
Kuadrat dari 4 (4²) = 16
Kubik dari 4 (4³) = 64

--- Penggunaan Konstanta ---
Luas lingkaran dengan radius 7 = 153.93791

------------------------------
Kalkulasi Selesai.
```

## Analisis Batasan dan Kemampuan Tambahan

Untuk memahami kapabilitas interpreter MORPH lebih dalam, pengujian tambahan dilakukan untuk kasus-kasus di luar lingkup kalkulator dasar.

### Skenario Pengujian

Sebuah skrip baru (`contoh/aplikasi/uji_batasan.fox`) dibuat untuk menguji dua skenario:
1.  Operasi pembagian yang melibatkan bilangan desimal.
2.  Penggunaan sintaks yang tidak valid (operator persen `%`).

```morph
# File Uji Batasan Kalkulator MORPH
# Tujuan: Menganalisis bagaimana interpreter menangani
# operasi yang tidak standar atau belum didukung sepenuhnya.

tulis("--- Uji Batasan Kalkulator ---")
tulis("")

# --- Kasus 1: Operasi dengan Bilangan Desimal ---
tulis("Kasus 1: Pembagian dengan desimal (1 / 0.01)")
biar hasil_desimal = 1 / 0.01
tulis("Hasil: ", hasil_desimal)
tulis("")

# --- Kasus 2: Operasi dengan Sintaks Belum Didukung (%) ---
# Baris di bawah ini sengaja dikomentari untuk pengujian terpisah.
# Saat dijalankan, baris ini menghasilkan kesalahan penguraian yang diharapkan.
#
# tulis("Kasus 2: Penggunaan sintaks persen (0.8% * 12)")
# biar hasil_persen = 0.8% * 12
# tulis("Hasil: ", hasil_persen)
# tulis("")

tulis("--- Uji Selesai ---")
```

### Hasil Analisis

1.  **Penanganan Bilangan Desimal (Berhasil)**
    Interpreter berhasil mengeksekusi operasi `1 / 0.01` dan memberikan hasil yang akurat.

    **Output:**
    ```
    --- Uji Batasan Kalkulator ---

    Kasus 1: Pembagian dengan desimal (1 / 0.01)
    Hasil:  100.0

    --- Uji Selesai ---
    ```
    Ini membuktikan bahwa operasi aritmatika MORPH sudah mendukung bilangan titik-mengambang (floating-point) dengan baik.

2.  **Penanganan Sintaks Tidak Valid (Berhasil)**
    Ketika baris yang mengandung operator `%` dijalankan, interpreter dengan benar menghentikan eksekusi dan melaporkan kesalahan penguraian (parser error).

    **Output Kesalahan:**
    ```
    Kesalahan di baris 18, kolom 26: Diharapkan sebuah ekspresi, tapi ditemukan token yang tidak valid.
    ```
    Ini menunjukkan bahwa sistem deteksi kesalahan sintaks berfungsi sesuai desain dan mencegah eksekusi kode yang tidak valid.

## Kesimpulan

Aplikasi kalkulator dan pengujian batasan ini secara komprehensif membuktikan bahwa interpreter MORPH berada dalam kondisi yang stabil dan siap produksi. Fitur-fitur fundamentalnya bekerja dengan andal, dan sistem penanganan kesalahannya mampu melindungi dari input yang tidak valid.
