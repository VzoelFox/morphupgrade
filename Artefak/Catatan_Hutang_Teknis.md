# Catatan Hutang Teknis (Technical Debt) & Fokus Masa Depan
# Dibuat: Patch 13 (Hybrid Infrastructure)

## 1. Kestabilan Rust VM (Critical)

### A. Panic pada Opcode I/O
Saat ini, implementasi Opcode Networking (`NET_CONNECT`, dll) dan File I/O di `greenfield/morph_vm/src/main.rs` menggunakan `panic!` jika terjadi error sistem (misal koneksi ditolak).
*   **Dampak:** VM crash seketika. Blok `coba/tangkap` di kode Morph tidak berfungsi.
*   **Solusi:** Ubah semua `panic!` menjadi pengembalian nilai `Constant::Nil` atau `Constant::Error` agar bisa ditangkap oleh `bridge_fox.fox`. (Sebagian Networking sudah diperbaiki di Patch 13, tapi File IO masih perlu audit).

### B. Reference Cycles (Memory Leak)
Struktur `Function` menyimpan `globals` (Rc), dan `globals` menyimpan `Function` (Rc).
*   **Dampak:** Memori tidak pernah dibebaskan (Memory Leak) selama VM berjalan.
*   **Solusi:** Gunakan `Weak` reference atau implementasikan Garbage Collector (GC) sederhana (Mark-and-Sweep).

## 2. Fitur yang Belum Ada (Missing Features)

### A. Protokol Tingkat Tinggi
Rust VM saat ini hanya mendukung TCP Socket mentah.
*   **Kebutuhan:** HTTP/HTTPS Client, SSH Client.
*   **Rencana:** Implementasikan di level Morph (`greenfield/cotc/protokol/http.fox`) menggunakan `Socket` class, atau tambahkan crate Rust (`reqwest`) jika performa native dibutuhkan.

### B. Standard Library yang Terfragmentasi
Saat ini ada `stdlib/core.fox` (stub lama), `sys/syscalls.fox` (interface baru), dan `bridge_fox.fox` (handler baru).
*   **Rencana:** Migrasikan semua kode lama (`berkas.fox`) untuk menggunakan `bridge_fox.fox`. Hapus stub yang tidak terpakai di `core.fox`.

## 3. Toolchain

### A. Bootstrap Compiler Compatibility
Host VM (Python) menggunakan parser lama (`transisi/crusher.py`) yang tidak mendukung sintaks baru (misal blok `maka { ... }`).
*   **Solusi:** Percepat transisi ke **Full Self-Hosting** (jalankan compiler Morph di atas Rust VM) agar kita bisa membuang parser Python lama.

---
**Prioritas Berikutnya:**
1.  Stabilisasi Error Handling di Rust VM (No Panic Policy).
2.  Implementasi HTTP Client sederhana di atas `jaringan.fox`.
