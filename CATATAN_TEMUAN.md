# Catatan Temuan & Hutang Teknis Morph

Dokumen ini berisi daftar hutang teknis (technical debt), potensi bug (bug triggers), dan fitur yang belum terimplementasi (TODO) yang ditemukan selama pengembangan, khususnya fase refactoring kompiler dan ekspansi standard library.

Tujuannya adalah untuk transparansi dan panduan bagi pengembangan selanjutnya agar tidak "tersandung batu yang sama".

## 1. Hutang Teknis (Technical Debt)

### A. Dualitas Parser (The Split-Brain Problem)
*   **Masalah:** Kita memiliki dua parser aktif:
    1.  `transisi/crusher.py` (Python): Digunakan untuk bootstrap awal dan fallback jika binary `.mvm` tidak ada.
    2.  `greenfield/crusher.fox` (Morph): Parser utama self-hosted yang dikompilasi menjadi binary.
*   **Dampak:** Perubahan sintaks (seperti mengizinkan keyword sebagai nama fungsi) harus diterapkan manual di **KEDUA** parser. Jika lupa satu, kode akan jalan di satu mode tapi crash di mode lain.
*   **Solusi:** Jangka panjang, parser Python harus dihapus total setelah self-hosting stabil 100%, atau dibuat mekanisme tes otomatis yang membandingkan output AST kedua parser.

## 2. Pemicu Bug (Known Bug Triggers)

### A. Sensitivitas Newline
*   **Pemicu:** Blok `jika`, `kelas`, `fungsi` sangat sensitif terhadap keberadaan baris baru (`\n`) setelah keyword pembuka (`maka`).
*   **Gejala:** `Parser Error: Dibutuhkan baris baru...` atau parsing berhenti tiba-tiba.
*   **Mitigasi:** Selalu gunakan format multi-line yang ketat.

### B. Konflik Keyword di Identifier
*   **Pemicu:** Menggunakan kata seperti `jenis`, `tipe`, `ambil` sebagai nama variabel lokal.
*   **Gejala:** Parser error membingungkan ("Dibutuhkan nama variabel...").
*   **Status:** Sudah di-patch untuk properti (`obj.tipe`), tapi untuk variabel lokal (`biar tipe = 1`) masih berisiko.

### C. Circular Import
*   **Pemicu:** Modul A import Modul B, Modul B import Modul A.
*   **Gejala:** `ImportError` atau variabel global bernilai `nil` saat diakses.
*   **Mitigasi:** Hindari dependensi melingkar. Gunakan injeksi dependensi jika perlu.

## 3. Daftar TODO & Fitur Belum Terimplementasi

### Prioritas Tinggi
- [ ] **Sinkronisasi Parser Otomatis:** Script tes untuk memvalidasi paritas parser Python vs Morph.
- [ ] **Dokumentasi API `cotc`:** Generate docs dari komentar kode (docstrings).

### Jangka Menengah (Arsitektur)
- [ ] **Native VM:** Porting `StandardVM` (Python) ke bahasa sistem (Rust/C++) untuk performa dan snapshotting memori yang akurat.
- [ ] **Source Maps:** Mapping bytecode kembali ke baris kode sumber `.fox` untuk stack trace yang lebih akurat saat debugging binary.
- [ ] **Manajemen Memori Heap:** Implementasi alokator memori di level Morph (untuk `cotc` tingkat lanjut) daripada bergantung 100% pada Python list/dict.

### Fitur Bahasa
- [ ] **Closure Penuh:** Dukungan `nonlocal` atau *captured variables* yang lebih robust di VM.
- [ ] **Destructuring Assignment:** `biar [a, b] = list` (saat ini baru di `jodohkan`).
- [ ] **String Interpolation:** Sintaks `"Halo {nama}"` (saat ini manual `"Halo " + nama`).

---
*Dibuat oleh Jules, [Tanggal Hari Ini]*
