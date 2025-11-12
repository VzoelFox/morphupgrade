# Modul Berkas - File System Operations

Modul `berkas` menyediakan fungsi-fungsi untuk berinteraksi dengan file system, seperti membaca, menulis, menghapus, dan mengelola file serta direktori.

## Import

Untuk menggunakan modul ini, impor semua fungsinya dengan cara berikut:
```morph
ambil_semua "transisi/stdlib/wajib/berkas.fox"
```

## Fungsi

### `baca_file(path: teks) -> teks`
Membaca seluruh konten dari file yang ditentukan oleh `path` dan mengembalikannya sebagai sebuah string (teks). Jika file tidak ditemukan atau terjadi error lain, sebuah `KesalahanRuntime` akan dilemparkan.

### `tulis_file(path: teks, konten: teks) -> benar`
Menulis string `konten` ke dalam file yang ditentukan oleh `path`. Jika direktori induk dari `path` belum ada, maka akan dibuat secara otomatis. Mengembalikan `benar` jika berhasil.

### `ada_file(path: teks) -> boolean`
Mengecek apakah sebuah file atau direktori ada pada `path` yang diberikan. Mengembalikan `benar` jika ada, dan `salah` jika tidak.

### `hapus_file(path: teks) -> benar`
Menghapus file atau direktori (beserta isinya secara rekursif) pada `path` yang diberikan. Mengembalikan `benar` jika berhasil.

### `buat_direktori(path: teks) -> benar`
Membuat sebuah direktori pada `path` yang diberikan. Fungsi ini bersifat rekursif, artinya jika ada direktori induk yang belum ada, maka akan dibuat juga. Mengembalikan `benar` jika berhasil.

### `daftar_file(path: teks) -> daftar`
Mengembalikan sebuah daftar (list) berisi nama-nama file dan direktori yang ada di dalam `path`. `path` harus menunjuk ke sebuah direktori.

### `info_file(path: teks) -> kamus`
Mengembalikan sebuah kamus (dictionary) yang berisi informasi detail tentang file atau direktori, termasuk:
- `ukuran`: Ukuran file dalam bytes.
- `dibuat`: Timestamp kapan file dibuat.
- `diubah`: Timestamp kapan file terakhir diubah.
- `adalah_file`: `benar` jika path adalah file.
- `adalah_direktori`: `benar` jika path adalah direktori.
- `path_absolut`: Path absolut dari file/direktori.

### `salin_file(sumber: teks, tujuan: teks) -> benar`
Menyalin file atau direktori dari `sumber` ke `tujuan`. Jika `sumber` adalah direktori, seluruh isinya akan disalin secara rekursif. Mengembalikan `benar` jika berhasil.

### `pindah_file(sumber: teks, tujuan: teks) -> benar`
Memindahkan (atau mengubah nama) file atau direktori dari `sumber` ke `tujuan`. Mengembalikan `benar` jika berhasil.

### `path_absolut(path: teks) -> teks`
Mengembalikan path absolut dari `path` yang relatif.

### `gabung_path(bagian1: teks, bagian2: teks) -> teks`
Menggabungkan dua bagian path menjadi satu path tunggal dengan menggunakan pemisah direktori yang sesuai dengan sistem operasi.
