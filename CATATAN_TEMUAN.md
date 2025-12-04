# Catatan Temuan & Hutang Teknis Morph

Dokumen ini berisi daftar hutang teknis (technical debt), potensi bug (bug triggers), dan fitur yang belum terimplementasi (TODO) yang ditemukan selama pengembangan.

Tujuannya adalah untuk transparansi dan panduan bagi pengembangan selanjutnya agar tidak "tersandung batu yang sama".

## 1. Hutang Teknis (Technical Debt)

### A. Dualitas Parser (The Split-Brain Problem)
*   **Masalah:** Kita memiliki dua parser aktif (`transisi` dan `greenfield`).
*   **Status:** **Terkendali (Mitigated)**.
*   **Mitigasi:** `tests/test_parser_parity.py` kini berjalan di CI untuk memastikan kedua parser memiliki perilaku yang sama (konsisten menerima/menolak sintaks).
*   **Solusi Jangka Panjang:** Parser Python harus dihapus total setelah self-hosting stabil 100% dan VM native tersedia.

### B. Kompiler Self-Hosted Belum Mendukung Closure Penuh
*   **Masalah:** Host Compiler (`ivm/compiler.py`) sudah mendukung analisis scope (Closure), tapi Self-Hosted Compiler (`greenfield/kompiler/`) belum. Kode Morph yang dikompilasi oleh `morph` CLI belum bisa menggunakan Closure.
*   **Solusi:** Porting logika `ScopeAnalyzer` dari Python ke Morph.

## 2. Pemicu Bug (Known Bug Triggers)

### A. Sensitivitas Newline (RESOLVED)
*   **Masalah:** Sebelumnya blok `jika`, `kelas`, `fungsi` mewajibkan baris baru setelah keyword `maka`.
*   **Status:** **Teratasi**. Parser Bootstrap dan Self-Hosted kini mendukung penulisan blok satu baris (newline opsional setelah `maka`).
*   **Contoh:** `jika benar maka tulis("ok") akhir` kini valid.

### B. Konflik Keyword di Identifier (RESOLVED)
*   **Masalah:** Kata kunci seperti `jenis`, `tipe`, `ambil` sebelumnya menyebabkan error jika digunakan sebagai variabel lokal.
*   **Status:** **Teratasi**. Parser kini mengizinkan keyword tersebut sebagai nama variabel lokal (`biar tipe = 1`) dan nama properti (`obj.tipe`).

### C. Circular Import
*   **Pemicu:** Modul A import Modul B, Modul B import Modul A.
*   **Gejala:** `ImportError` atau variabel global bernilai `nil` saat diakses.
*   **Mitigasi:** Hindari dependensi melingkar. Gunakan injeksi dependensi jika perlu.

## 3. Daftar TODO & Fitur Belum Terimplementasi

### Prioritas Tinggi
- [x] **Sinkronisasi Parser Otomatis:** Script tes (`tests/test_parser_parity.py`) telah dibuat dan berjalan sukses.
- [x] **Dokumentasi API `cotc`:** Tools `tools/docgen.fox` telah dibuat untuk generate docs otomatis dari komentar kode.
- [x] **Closure Penuh (Host Compiler):** Dukungan `nonlocal` atau *captured variables* yang lebih robust di VM dan Host Compiler.
- [ ] **Closure Penuh (Self-Hosted):** Porting analisis scope ke `greenfield/kompiler/`.

### Jangka Menengah (Arsitektur)
- [ ] **Native VM:** Porting `StandardVM` (Python) ke bahasa sistem (Rust/C++) untuk performa dan snapshotting memori yang akurat. ATAU implementasi VM native dalam Morph (Self-Hosted Micro-VM).
- [ ] **Source Maps:** Mapping bytecode kembali ke baris kode sumber `.fox` untuk stack trace yang lebih akurat saat debugging binary.
- [ ] **Manajemen Memori Heap:** Implementasi alokator memori di level Morph (untuk `cotc` tingkat lanjut).

### Fitur Bahasa
- [x] **Destructuring Assignment:** `biar [a, b] = list` (didukung di Parser & Compiler).
- [x] **String Interpolation:** Sintaks `"Halo {nama}"` didukung dengan `Op.STR` (Intrinsic 64).

---
*Dibuat oleh Jules, [Tanggal Hari Ini]*
