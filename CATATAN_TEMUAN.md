# Catatan Temuan & Hutang Teknis Morph

Dokumen ini berisi daftar hutang teknis (technical debt), potensi bug (bug triggers), dan fitur yang belum terimplementasi (TODO) yang ditemukan selama pengembangan.

Tujuannya adalah untuk transparansi dan panduan bagi pengembangan selanjutnya agar tidak "tersandung batu yang sama".

## 1. Hutang Teknis (Technical Debt)

### A. Dualitas Parser (The Split-Brain Problem)
*   **Masalah:** Kita memiliki dua parser aktif (`transisi` dan `greenfield`).
*   **Status:** **Terkendali (Mitigated)**.
*   **Mitigasi:** `tests/test_parser_parity.py` kini berjalan di CI untuk memastikan kedua parser memiliki perilaku yang sama (konsisten menerima/menolak sintaks).
*   **Solusi Jangka Panjang:** Parser Python harus dihapus total setelah self-hosting stabil 100% dan VM native tersedia.

## 2. Pemicu Bug (Known Bug Triggers)

### A. Sensitivitas Newline
*   **Pemicu:** Blok `jika`, `kelas`, `fungsi` sangat sensitif terhadap keberadaan baris baru (`\n`) setelah keyword pembuka (`maka`).
*   **Gejala:** `Parser Error: Dibutuhkan baris baru...` (Kini parser akan Panic/Fail Fast di sini, sehingga lebih mudah dideteksi).
*   **Mitigasi:** Selalu gunakan format multi-line yang ketat.

### B. Konflik Keyword di Identifier
*   **Pemicu:** Menggunakan kata seperti `jenis`, `tipe`, `ambil` sebagai nama variabel lokal.
*   **Status:** Parser telah dipatch untuk mengizinkan keyword ini sebagai **Nama Properti** (`obj.tipe`) dan **Nama Fungsi**. Namun penggunaannya sebagai variabel lokal (`biar tipe = 1`) masih berisiko ambigu.

### C. Circular Import
*   **Pemicu:** Modul A import Modul B, Modul B import Modul A.
*   **Gejala:** `ImportError` atau variabel global bernilai `nil` saat diakses.
*   **Mitigasi:** Hindari dependensi melingkar. Gunakan injeksi dependensi jika perlu.

## 3. Daftar TODO & Fitur Belum Terimplementasi

### Prioritas Tinggi
- [x] **Sinkronisasi Parser Otomatis:** Script tes (`tests/test_parser_parity.py`) telah dibuat dan berjalan sukses.
- [ ] **Dokumentasi API `cotc`:** Generate docs dari komentar kode (docstrings).

### Jangka Menengah (Arsitektur)
- [ ] **Native VM:** Porting `StandardVM` (Python) ke bahasa sistem (Rust/C++) untuk performa dan snapshotting memori yang akurat.
- [ ] **Source Maps:** Mapping bytecode kembali ke baris kode sumber `.fox` untuk stack trace yang lebih akurat saat debugging binary.
- [ ] **Manajemen Memori Heap:** Implementasi alokator memori di level Morph (untuk `cotc` tingkat lanjut).

### Fitur Bahasa
- [ ] **Closure Penuh:** Dukungan `nonlocal` atau *captured variables* yang lebih robust di VM.
- [ ] **Destructuring Assignment:** `biar [a, b] = list` (saat ini baru di `jodohkan`).
- [ ] **String Interpolation:** Sintaks `"Halo {nama}"`.

---
*Dibuat oleh Jules, [Tanggal Hari Ini]*
