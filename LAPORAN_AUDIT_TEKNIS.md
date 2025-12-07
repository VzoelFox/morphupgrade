# Laporan Audit Teknis: Kejujuran & Realita
**Tanggal:** 23 Oktober 2024
**Auditor:** Jules (AI Agent)
**Status:** DRAFT / UNFILTERED

## 1. Audit Arsitektur Parser (`greenfield/crusher.fox`)

Parser ini menganut filosofi "Fail Fast" yang bagus, namun strukturnya memiliki beberapa "Retakan Struktural" yang membuatnya rapuh terhadap pengembangan masa depan.

### A. "Bom Waktu" Interpolasi String (`_parse_interpolasi_teks`)
Ini adalah bagian paling berbahaya di parser saat ini.
- **Logika:** Fungsi ini melakukan *scanning* manual karakter-per-karakter di dalam Parser (seharusnya tugas Lexer).
- **Rekursi Mahal:** Ia memanggil `Lexer` dan `Pengurai` baru secara rekursif untuk setiap interpolasi.
- **Ketergantungan Melingkar:** Fungsi ini melakukan `dari "cotc(stdlib)/teks.fox" ambil_sebagian iris`. Ini berarti **Parser Inti bergantung pada Standard Library**. Jika `stdlib` rusak, Parser tidak bisa berjalan. Jika Parser tidak jalan, kita tidak bisa compile `stdlib`. *Circular Dependency Hell*.

### B. Daftar Putih Identifier yang Kaku (`_apakah_identifier`)
Fungsi ini berisi daftar hardcoded (`T.NAMA`, `T.TIPE`, `T.JENIS`, dll).
- **Masalah:** Setiap kali kita menambah keyword baru di bahasa, kita HARUS ingat untuk menambahkannya ke sini jika keyword tersebut boleh dipakai sebagai nama variabel. Jika lupa, parser akan menolak kode valid dengan error membingungkan.
- **Solusi:** Seharusnya Lexer memberikan flag `is_keyword` atau Parser mengecek range token, bukan whitelist manual.

### C. Duplikasi Logika Fungsi
`_deklarasi_fungsi` dan `_deklarasi_fungsi_asink` memiliki 90% kode yang sama (parsing parameter, parsing body). Ini pelanggaran prinsip DRY (Don't Repeat Yourself) yang membuat refactoring sulit (harus ubah di dua tempat).

---

## 2. Audit "Ilusi Native" pada FoxVM (`greenfield/fox_vm/prosesor.fox`)

Saat ini, FoxVM bukanlah "Mesin Virtual" dalam arti tradisional (yang mengatur memori dan register hardware), melainkan sebuah **Meta-Interpreter** yang sangat bergantung pada Host (IVM/Python).

### A. Ketergantungan Python (FFI)
Kita masih "meminjam" otak Python untuk hal-hal sepele:
- **Slicing (`_ops_slice`):** Menggunakan `py.slice(start, stop)`. Kita belum punya logika slicing sendiri.
- **Iterasi Dictionary (`_keys_builtin`):** Menggunakan `py.list(obj)` untuk mengambil kunci dictionary. Tanpa Python, FoxVM tidak bisa melakukan loop pada dictionary atau menginstansiasi Kelas (yang butuh iterasi metode).
- **Intrinsik Dasar:** `panjang`, `tambah` (list append), `tipe_objek` semuanya adalah *pass-through* ke fungsi built-in IVM. FoxVM tidak tahu cara menghitung panjang list, ia hanya bertanya pada Host.

### B. Jembatan Rapuh (`ProxyHostGlobals`)
VM sangat bergantung pada `_getitem`, `_setitem`, `_getattr`, `_call_host` yang disuntikkan ke global scope.
- **Risiko:** Jika interface bridge ini berubah di IVM, FoxVM langsung lumpuh total. Tidak ada lapisan abstraksi yang kuat di sisi Morph.

### C. Status I/O
I/O (`greenfield/cotc/io/berkas.fox`) 100% adalah wrapper FFI. Ini wajar untuk fase bootstrap, tapi perlu dicatat bahwa Morph saat ini "buta dan tuli" tanpa Python.

---

## 3. Kesimpulan & Rekomendasi

### Status Sebenarnya: "Hybrid-Meta Interpreter"
Kita belum berada di tahap "Self-Hosting" murni. Kita berada di tahap di mana logika alur program (Control Flow) sudah milik Morph, tapi logika data (Data Manipulation) dan Sistem (Syscall) masih milik Python.

### Rekomendasi Prioritas (Urutan Kritikalitas):

1.  **Refactor Interpolasi String:** Pindahkan logika scanning string ke **Lexer**. Hilangkan ketergantungan Parser pada `stdlib`. Parser harus mandiri.
2.  **Hapus Hardcoded Identifier:** Ubah logika `_apakah_identifier` menjadi lebih dinamis berbasis Tipe Token.
3.  **Implementasi Slicing Native:** Tulis ulang logika slicing di Morph (kalkulasi indeks start/end/step) alih-alih meminjam `py.slice`.
4.  **Unifikasi Parsing Fungsi:** Gabungkan `_deklarasi_fungsi` dan `asink` menjadi satu fungsi builder yang fleksibel.

---
*Laporan ini dibuat otomatis oleh Jules untuk tujuan audit transparansi.*
