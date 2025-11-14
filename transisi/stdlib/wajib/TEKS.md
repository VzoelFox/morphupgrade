# Modul Teks - String Operations

Modul `teks` menyediakan fungsi-fungsi untuk manipulasi string (teks).

## Import

Untuk menggunakan modul ini, impor semua fungsinya dengan cara berikut:
```morph
ambil_semua "transisi/stdlib/wajib/teks.fox"
```

## Fungsi

### `pisah(teks: teks, pembatas: teks) -> daftar`
Memisahkan `teks` menjadi sebuah `daftar` (list) string, menggunakan `pembatas` sebagai delimeter.

### `gabung(daftar: daftar, penghubung: teks) -> teks`
Menggabungkan elemen-elemen dalam sebuah `daftar` menjadi satu string, dengan `penghubung` di antara setiap elemen.

### `potong_spasi(teks: teks) -> teks`
Menghapus spasi di awal dan akhir dari `teks`.

### `huruf_besar(teks: teks) -> teks`
Mengubah semua karakter dalam `teks` menjadi huruf besar.

### `huruf_kecil(teks: teks) -> teks`
Mengubah semua karakter dalam `teks` menjadi huruf kecil.

### `ganti(teks: teks, cari: teks, ganti_dengan: teks) -> teks`
Mengganti semua kemunculan `cari` dalam `teks` dengan `ganti_dengan`.

### `mulai_dengan(teks: teks, awalan: teks) -> boolean`
Mengembalikan `benar` jika `teks` dimulai dengan `awalan`, jika tidak `salah`.

### `berakhir_dengan(teks: teks, akhiran: teks) -> boolean`
Mengembalikan `benar` jika `teks` diakhiri dengan `akhiran`, jika tidak `salah`.
