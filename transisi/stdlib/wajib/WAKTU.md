# Modul Waktu - Date and Time Operations

Modul `waktu` menyediakan fungsi-fungsi untuk manipulasi objek `datetime`.

## Import

Untuk menggunakan modul ini, impor semua fungsinya dengan cara berikut:
```morph
ambil_semua "transisi/stdlib/wajib/waktu.fox"
```

## Fungsi

### `tambah_hari(dt_obj: ObjekPython, jumlah_hari: angka) -> ObjekPython`
Menambahkan `jumlah_hari` ke objek `datetime` `dt_obj` dan mengembalikan objek `datetime` baru.

### `selisih_hari(dt_obj1: ObjekPython, dt_obj2: ObjekPython) -> angka`
Menghitung selisih hari antara dua objek `datetime`, `dt_obj1` dan `dt_obj2`.
