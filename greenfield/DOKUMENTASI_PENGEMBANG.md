# Dokumentasi Pengembang Greenfield

Selamat datang di **Greenfield**, implementasi *self-hosted* dari bahasa pemrograman Morph. Direktori ini berisi kode sumber Morph yang ditulis menggunakan bahasa Morph itu sendiri.

## Struktur Proyek

*   **`morph.fox`**: Titik masuk utama (Entry Point) compiler. Menggabungkan Lexer dan Parser.
*   **`lx_morph.fox`**: Lexer (Analisis Leksikal). Mengubah kode sumber menjadi daftar Token.
*   **`crusher.fox`**: Parser (Analisis Sintaksis). Mengubah Token menjadi Abstract Syntax Tree (AST).
*   **`absolute_syntax_morph.fox`**: Definisi node-node AST.
*   **`morph_t.fox`**: Definisi tipe token dan konstanta bahasa.
*   **`error_utils.fox`**: Utilitas untuk pelaporan kesalahan yang visual (dengan panah penunjuk).
*   **`handler.fox`**: Pengelola kesalahan terpusat.
*   **`cotc/`**: (Core of the Core) Standar library dasar untuk bootstrap.

## Standar Verifikasi 4 Langkah

Setiap perubahan kode di Greenfield harus lulus **Verifikasi 4 Langkah** untuk memastikan kestabilan bootstrap. Gunakan script `verify_greenfield.py` di root repository untuk menjalankan verifikasi ini.

1.  **Verifikasi Per-line (Sintaks)**:
    Memastikan setiap file `.fox` valid secara sintaksis menggunakan parser bootstrap (`ivm` Python).

2.  **Verifikasi Ketergantungan**:
    Memastikan semua file yang diimpor (via `ambil_semua` atau `ambil_sebagian`) benar-benar ada di sistem file.

3.  **Verifikasi Kompatibilitas (Simbol)**:
    Memastikan simbol (fungsi/variabel) yang diimpor spesifik benar-benar diekspor oleh modul target.

4.  **Verifikasi Eksekusi (Runtime)**:
    Mencoba memuat dan menginisialisasi modul menggunakan Bootstrap VM (`StandardVM`) untuk mendeteksi *runtime error* seperti referensi variabel global yang hilang.

### Cara Menjalankan Verifikasi
```bash
python3 verify_greenfield.py
```

## Fitur & Sintaks Baru

### Import
Sintaks import telah diperbarui agar lebih terstruktur:
```morph
# Import seluruh modul
ambil_semua "path/ke/file.fox" sebagai Alias

# Import sebagian simbol
dari "path/ke/file.fox" ambil_sebagian Simbol1, Simbol2
```

### Error Reporting
Greenfield dilengkapi dengan pelaporan kesalahan visual. Jika terjadi error parsing, output akan menunjukkan baris kode dan posisi kolom:

```
Kesalahan di baris 10, kolom 5:
  Dibutuhkan 'maka'
10 | jika benar tulis("x")
     ^--- Di sini
```

## Bootstrap Shim (Standard Library)
Untuk menghubungkan kode Morph dengan kemampuan VM Python, file `greenfield/cotc/stdlib/core.fox` bertindak sebagai *shim*. File ini mengekspos fungsi built-in VM (seperti `panjang`, `tambah`) agar bisa diimpor secara eksplisit oleh modul lain.

## Catatan Teknis VM (IVM)
*   **Path Resolution**: VM telah dipatch untuk memetakan path `cotc(stdlib)` ke `greenfield/cotc/stdlib` secara otomatis selama fase bootstrap ini.
*   **Class Closure**: VM mendukung penangkapan `globals` modul ke dalam definisi Kelas, sehingga metode kelas dapat mengakses variabel modul asalnya dengan benar.
*   **Dictionary**: VM mendukung metode `.punya(kunci)` pada tipe Dictionary.
