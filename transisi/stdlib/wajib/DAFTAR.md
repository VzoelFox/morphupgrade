# Modul Daftar - List Operations

Modul `daftar` menyediakan fungsi-fungsi untuk manipulasi `daftar` (list).

## Import

Untuk menggunakan modul ini, impor semua fungsinya dengan cara berikut:
```morph
ambil_semua "transisi/stdlib/wajib/daftar.fox"
```

## Fungsi

### `panjang(daftar: daftar) -> angka`
Mengembalikan jumlah elemen dalam `daftar`.

### `tambah(daftar: daftar, item: apapun) -> daftar`
Menambahkan `item` ke akhir `daftar` dan mengembalikan daftar yang telah diubah.

### `hapus(daftar: daftar, indeks: angka) -> daftar`
Menghapus item pada `indeks` dari `daftar` dan mengembalikan daftar yang telah diubah.

### `urut(daftar: daftar) -> daftar`
Mengembalikan `daftar` baru yang telah diurutkan.

### `balik(daftar: daftar) -> daftar`
Mengembalikan `daftar` baru dengan urutan elemen yang terbalik.

### `cari(daftar: daftar, item: apapun) -> angka`
Mencari `item` dalam `daftar` dan mengembalikan `indeks` dari kemunculan pertama. Mengembalikan `-1` jika `item` tidak ditemukan.
