# Update Patch 17: Lexer Fix & VM Stability

**Tanggal:** 13 Desember 2025
**Engineer:** Jules AI
**Founder:** Vzoel Fox's (Lutpan)

Patch ini mengatasi hambatan utama pada Lexer saat dijalankan di atas Rust VM, serta memperbaiki stabilitas eksekusi fungsi.

## 1. Fix: String Comparison (Lexer Unblock)
Lexer Morph (`lx_morph.fox`) bergantung pada perbandingan string seperti `char >= "a"` untuk mendeteksi identifier.
*   **Masalah:** Rust VM sebelumnya tidak mengimplementasikan `PartialOrd` untuk `Constant::String`, sehingga semua perbandingan string (GT, LT, GTE, LTE) mengembalikan `false`. Akibatnya, `_is_alpha` selalu gagal, dan Lexer melaporkan "Karakter tidak dikenal".
*   **Solusi:** Implementasi `PartialOrd` untuk `Constant::String` dan `Constant::Bytes` di `greenfield/morph_vm/src/main.rs`.
*   **Hasil:** Lexer kini berfungsi normal dan dapat memproses input.

## 2. Fix: Call Arguments (Parser Stability)
Parser (`crusher.fox`) menggunakan fungsi dengan argumen opsional (misal: `_cocok(t1, t2, t3, t4)` dipanggil dengan 2 argumen).
*   **Masalah:** Implementasi `CALL` opcode di Rust VM menggunakan `zip` iterator yang berhenti pada jumlah argumen terkecil. Argumen yang hilang tidak dimasukkan ke `locals`, menyebabkan panic "Local not found" saat fungsi mencoba mengaksesnya.
*   **Solusi:** Memperbarui logika `CALL` (baik untuk Fungsi maupun Inisiasi Kelas) untuk mengisi argumen yang hilang dengan `Constant::Nil`.
*   **Hasil:** Parser dapat berjalan lebih jauh tanpa crash pada pemanggilan fungsi.

## 3. Fix: Dictionary `punya`
*   **Masalah:** Parser menggunakan `dict.punya(key)` untuk pengecekan keyword. Rust VM tidak mendukung metode native pada Dictionary.
*   **Solusi:** Menambahkan dukungan `LOAD_ATTR` dan `CALL` untuk metode `punya` pada `Constant::Dict`.

## 4. Tantangan Berikutnya (Parser Runtime)
Saat ini kompilasi `hello_world.fox` terhenti pada tahap Parsing/AST Construction dengan error:
`CALL target invalid: Instance(...)`
Terindikasi bahwa kelas AST `Konstanta` entah bagaimana teresolusi menjadi sebuah `Instance` saat hendak dipanggil sebagai konstruktor. Ini memerlukan investigasi lebih lanjut pada resolusi variabel modul.

---
*Status Self-Hosting: Lexer Berfungsi, Parser Berjalan (Crash di AST).*
