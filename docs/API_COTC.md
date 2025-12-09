# Referensi API `greenfield/cotc` (Core of the Core)

Pustaka standar (Standard Library) untuk bahasa pemrograman Morph, diimplementasikan dalam **Pure Morph**.

## Daftar Modul Utama

### 1. Struktur Data (`greenfield/cotc/struktur/`)
*   **`tumpukan.fox`**: Implementasi Stack (LIFO) menggunakan native List.
    *   `dorong(item)`, `angkat()`, `intip()`, `kosong()`.
*   **`antrian.fox`**: Implementasi Queue (FIFO) menggunakan native List.
    *   `masuk(item)`, `copot()`, `intip()`, `kosong()`.
*   **`himpunan.fox`**: Implementasi Set menggunakan native Dictionary.
    *   `tambah(item)`, `hapus(item)`, `memuat(item)`, `gabung(lain)`, `iris(lain)`, `beda(lain)`.

### 2. Matematika (`greenfield/cotc/matematika/`)
*   **`dasar.fox`**: Fungsi matematika dasar dan konstanta.
    *   `absolut(x)`, `min(a,b)`, `max(a,b)`, `pangkat(base, exp)`, `akar(x)`, `faktorial(n)`.
    *   `lantai(x)`, `atap(x)`.
    *   Konstanta: `PI`, `E`.
*   **`trigonometri.fox`**: Fungsi trigonometri (Taylor Series).
    *   `sin(x)`, `cos(x)`, `tan(x)`, `radian(deg)`, `derajat(rad)`.

### 3. Teks & String (`greenfield/cotc/stdlib/teks.fox`)
*   **`teks.fox`**: Manipulasi string tanpa dependensi FFI.
    *   `format(template, args)`: Interpolasi string `{}`.
    *   `temukan(haystack, needle)`, `ganti(s, old, new)`, `pisah(s, delim)`, `bersihkan(s)`.
    *   **Metode Primitif:** String literal (`"..."`) kini mendukung metode native seperti `.kecil()`, `.besar()`, `.ganti()`, dll secara langsung.

### 4. Bytecode & VM (`greenfield/cotc/bytecode/`)
*   **`struktur.fox`**: Serialisasi/Deserialisasi format binary `.mvm` ("VZOEL FOXS").
*   **`opkode.fox`**: Definisi konstanta Opcode VM.

### 5. Sistem & I/O
*   **`io/berkas.fox`**: Wrapper I/O File.
*   **`sistem/foxys.fox`**: Antarmuka sistem operasi (waktu, sleep).

## Status Implementasi
Semua modul di atas telah diaudit dan dipastikan **Pure Morph** (bebas dari `pinjam "builtins"` yang tidak perlu), menjamin portabilitas ke Native VM.
