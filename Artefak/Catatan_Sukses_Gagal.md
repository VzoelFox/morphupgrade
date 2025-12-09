# Catatan Sukses dan Gagal (Test Report)

Dokumen ini mencatat hasil eksekusi tes otomatis menggunakan `run_ivm_tests.py` dan upaya build self-hosted compiler.

## Ringkasan Eksekusi
- **Total Tes IVM**: 37
- **Lulus**: 29
- **Gagal**: 8
- **Build Self-Hosted**: GAGAL (RuntimeError)

## Detail Kegagalan (Failures)

### Kategori 1: Missing Globals & System Errors
Beberapa tes gagal karena fungsi global tidak ditemukan atau error sistem internal VM.

1. **Test Loader (`greenfield/examples/test_loader.fox`)**
   - **Status**: GAGAL
   - **Error**: `Global 'utama' not found.`
   - **Analisis**: Modul tidak mengekspos fungsi `utama` yang diharapkan oleh runner, atau proses pemuatan bytecode gagal mendaftarkan simbol global dengan benar.

2. **Parser Wrapper (`greenfield/examples/test_vm_parser_wip.fox`)**
   - **Status**: LULUS (Dengan Error Log)
   - **Catatan**: Mencetak banyak error `Lokal tidak ditemukan: tX` namun status akhir LULUS. Ini mungkin indikasi *false positive* atau tes yang mentoleransi error parsial.

3. **Lexer Wrapper (`greenfield/examples/test_vm_lexer_wip.fox`)**
   - **Status**: LULUS (Dengan Error Log)
   - **Catatan**: Mencetak `Error: CALL unknown type None`. Perlu investigasi lebih lanjut pada FFI Lexer.

### Kategori 2: Build Self-Hosted Compiler
Proses kompilasi compiler itu sendiri (bootstrapping) mengalami kegagalan kritis.

- **Target**: `greenfield/morph.fox`
- **Error**: `Instance '<Instance Pengurai>' has no attribute '_pernyataan_ambil_semua'`
- **Lokasi**: `_deklarasi at PC 33` -> `urai at PC 19`
- **Analisis**: Terdapat ketidakcocokan antara definisi kelas `Pengurai` di `parser.fox` dengan pemanggilannya. Metode `_pernyataan_ambil_semua` kemungkinan belum diimplementasikan atau salah nama.

## Detail Kesuksesan (Successes)

Tes berikut berjalan dengan sempurna dan memvalidasi fitur inti bahasa Morph:

- **Operasi Bitwise**: (`greenfield/examples/test_bitwise.fox`) - Shift, AND, OR, XOR, NOT berfungsi benar.
- **Protokol Dasar**: (`greenfield/examples/test_foxprotocol.fox`) - Parsing URL dan struktur HTTP Request/Response valid.
- **Base64 Encoding**: (`greenfield/examples/test_data_base64.fox`) - Encode/Decode string dan bytes roundtrip berhasil.
- **Manipulasi Teks**: (`greenfield/examples/test_pure_teks.fox`) - Operasi string murni (tanpa FFI berat) berjalan normal.
- **FoxVM Basic**: (`greenfield/examples/test_fox_vm_basic.fox`) - VM self-hosted mampu menjalankan kalkulasi aritmatika sederhana.
- **HTTP Client (Socket)**: (`greenfield/examples/test_http_client.fox`) - FFI Socket berfungsi (validasi koneksi ditolak).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.0.69 pre release
tanggal  : 10/12/2025
