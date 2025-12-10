# Referensi Sintaks Morph (SYNTX)
Dokumen ini menjelaskan kata kunci dan struktur sintaks yang didukung oleh bahasa pemrograman Morph (Greenfield Edition).

## Kata Kunci (Keywords)

### Deklarasi & Variabel
- `biar`: Mendeklarasikan variabel baru (mutable).
- `tetap`: Mendeklarasikan konstanta (immutable).
- `ubah`: Mengubah nilai variabel yang sudah ada (wajib untuk mutasi).
- `tipe`: Mendefinisikan tipe data kustom (Algebraic Data Types).
    ```morph
    tipe Hasil = Sukses(data) | Gagal(pesan)
    ```

### Kontrol Alur
- `jika` ... `maka` ... `akhir`: Percabangan kondisional.
- `lain_jika` ... `maka`: Cabang kondisional alternatif.
- `lain`: Blok default jika kondisi tidak terpenuhi.
- `selama` ... `maka` ... `akhir`: Perulangan (loop).
- `berhenti`: Menghentikan perulangan.
- `lanjutkan`: Melanjutkan ke iterasi berikutnya.
- `pilih` ... `kasus` ... `akhir`: Percabangan multi-kondisi (Switch).
- `jodohkan` ... `dengan` ... `| Pola maka ...`: Pattern Matching (Match).
    ```morph
    jodohkan nilai dengan
    | 10 maka ...
    | Sukses(x) maka ...
    | _ maka ...
    akhir
    ```

### Fungsi & Kelas
- `fungsi`: Mendefinisikan fungsi.
- `kembali` / `kembalikan`: Mengembalikan nilai dari fungsi.
- `kelas` ... `maka` ... `akhir`: Mendefinisikan kelas (OOP).
- `warisi`: Menentukan pewarisan kelas (inheritance).
- `ini`: Referensi ke instance objek saat ini (self/this).
- `induk`: Referensi ke kelas induk (super).

### Modul & Import
- `ambil_semua`: Mengimpor seluruh isi modul.
    ```morph
    ambil_semua "path/modul" sebagai Mod
    ```
- `ambil_sebagian`: Mengimpor simbol spesifik dari modul.
    ```morph
    dari "path/modul" ambil_sebagian A, B
    ```
- `dari`: Menentukan asal modul.
- `sebagai`: Memberikan alias pada impor.
- `pinjam`: Interface ke modul Host (Python).
    ```morph
    pinjam "builtins" sebagai py
    ```

### Penanganan Error
- `coba` ... `maka`: Blok percobaan (try).
- `tangkap e` ... `maka`: Menangkap error (catch).
- `akhirnya`: Blok yang selalu dijalankan (finally).
- `lemparkan`: Memicu error manual (throw/raise).

### Lain-lain
- `tulis`: Mencetak output ke konsol.
- `nil`: Nilai kosong/null.
- `benar` / `salah`: Nilai boolean.
- `warnai` ... `maka`: Blok pewarnaan teks terminal otomatis.
- `asink` / `tunggu`: Dukungan pemrograman asinkron (Coroutines).

## Operator

- **Aritmatika**: `+`, `-`, `*`, `/`, `%`
- **Bitwise**: `&`, `|`, `^` (XOR), `~`, `<<`, `>>`
- **Logika**: `dan`, `atau`, `tidak`
- **Perbandingan**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Assignment**: `=`

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.4 (Greenfield Patch 4)
tanggal  : 10/12/2025
