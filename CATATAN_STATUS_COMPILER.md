# Catatan Status Compiler Morph - Update Sesi Ini

## Ringkasan Sesi (Fitur Bahasa Baru)

Fokus utama sesi ini adalah implementasi fitur **Interpolasi String**, yang meningkatkan kenyamanan penulisan kode dengan mengurangi kebutuhan akan konkatenasi manual. Implementasi ini mencakup pembaruan pada seluruh toolchain (VM, Compiler, dan Parser).

### 1. Status Aktual: Feature Expansion
-   **Fitur Baru: Interpolasi String**
    -   ✅ **Sintaks:** Mendukung `"Halo {nama}"` atau `"Hasil: {a + b}"`.
    -   ✅ **Implementasi VM:** Menambahkan `Op.STR` (Opcode 64) untuk konversi intrinsik ke string.
    -   ✅ **Implementasi Parser:** Parser secara otomatis mendeteksi `{...}` dalam string literal, memecahnya, dan menyusun ulang sebagai rantai operasi penjumlahan string.
    -   ✅ **Parity:** Didukung baik di Bootstrap Parser (Python) maupun Self-Hosted Parser (Morph).

-   **Stabilitas & Keamanan:**
    -   ✅ **Escaping:** Mendukung escaping `\{` untuk menulis karakter kurawal literal di dalam string.
    -   ✅ **Robustness:** Telah diuji dengan berbagai kasus (ekspresi matematika, nested string sederhana, tipe data campuran) dan lulus `tests/test_parser_parity.py`.

### 2. Analisis & Temuan Teknis
-   **Tantangan Self-Hosting:** Implementasi parser di Morph (`greenfield/crusher.fox`) memerlukan teknik rekursif dimana parser memanggil lexer dan parser baru untuk bagian interpolasi. Ini berhasil diimplementasikan dengan mengimpor modul secara dinamis/lokal.
-   **Keterbatasan:** Interpolasi bersarang (nested interpolation) seperti `"{ "{a}" }"` didukung secara teori oleh parser rekursif, namun string literal di dalam interpolasi harus memperhatikan escaping karakter `{` jika diperlukan.

### 3. Roadmap & Prioritas Berikutnya
1.  **Dokumentasi API:** Membuat dokumentasi referensi untuk `greenfield/cotc`.
2.  **Destructuring Assignment:** Fitur `biar [a, b] = list`.
3.  **Optimasi VM:** Mempertimbangkan implementasi native untuk performa jangka panjang.
