# Vzoel ft Jules: Log Sesi & Visi Masa Depan
**Tanggal:** 12 Desember 2025
**Engineer:** Jules AI
**Founder:** Vzoel Fox's (Lutpan)

Dokumen ini merekam jejak diskusi strategis dan visi arsitektur yang dikembangkan bersama dalam sesi ini, khususnya mengenai Transisi Rust VM dan Evolusi FoxVM.

---

## 1. Pencapaian: Stabilisasi Rust VM (Patch 14)

Dalam sesi ini, kita berhasil mengubah Rust VM (`morph_vm`) dari sekadar "Prototipe yang Suka Panic" menjadi "Runtime yang Stabil".

*   **No Panic Policy:** Mengubah semua Opcode I/O dan Networking agar mengembalikan `Nil` atau `False` saat error sistem, bukan mematikan proses (Crash).
*   **Exception Handling:** Mengimplementasikan Opcodes `PUSH_TRY`, `POP_TRY`, dan `THROW` dengan logika *Stack Unwinding*. Ini memungkinkan kode Morph menangkap error dari Rust VM.
*   **Lexical Scoping:** Memperbaiki bug kritis dimana fungsi kehilangan akses ke variabel global modulnya. Solusinya adalah mengubah `BUILD_FUNCTION` agar menangkap `globals` saat definisi.
*   **Bridge Fox:** Memperbarui layer jembatan (`bridge_fox.fox`) untuk menerjemahkan nilai return aman dari Rust VM menjadi Exception Morph yang deskriptif.

---

## 2. Visi Besar: FoxVM Ascension

Kita sepakat untuk mengubah paradigma:
*   **Lama:** Rust/Python adalah "Otak" yang mengatur memori dan string. Morph hanya "Penumpang".
*   **Baru:** **FoxVM (Kode Morph)** adalah "Kernel/OS" yang mengatur memori, alokasi, dan logika. Rust/Python turun pangkat menjadi "Hardware" (penyedia Raw Byte Array & CPU).

Tujuannya adalah portabilitas total (ke WASM/JS) di masa depan.

---

## 3. Visi Alokator: "Lemari Allocator" (The Cupboard)

Kita merancang sistem manajemen memori manual di dalam Morph dengan analogi **Warung Kopi**:

### A. Terminologi & Konsep
1.  **Lemari (Memory Pool):** Total ruang memori yang tersedia.
2.  **Laci (Memory Arena):** Bagian dari lemari. Bersifat **Lazy Loading** (tidak dibuka jika tidak ada pesanan/data).
3.  **Nampan (Double Buffer):** Setiap laci punya 2 nampan (A dan B).
    *   Satu untuk *Write* (sedang diisi).
    *   Satu untuk *Read* (hasil proses sebelumnya).
4.  **Gelas (Object/Data):** Data aktual.
5.  **Tiket Gelas (Pointer):** Penunjuk lokasi data `{id_lemari, id_nampan, offset}`.

### B. Aturan Main (Konstitusi)
1.  **Cuci Nampan (Reset):** Saat pemilik (proses) pergi, Nampan A (bekas pakai) langsung dicuci bersih (Reset Offset). Data di Nampan B bertahan sampai pembeli selesai.
2.  **Owner Tanpa Kepemilikan:** Objek Morph memegang "Tiket Gelas", tapi tidak memiliki gelasnya. Gelas dimiliki oleh Laci. Tidak ada *free()* manual per objek.
3.  **Konstitusi Hybrid:** Jika Laci Rust penuh atau Panic, atau sedang di mode REPL, Rust **diizinkan** membuka "Lemari Python" (Malloc Host OS) sebagai *fallback*. Jangan biarkan sistem mati konyol.

### C. Implementasi Awal
File struktur telah dibuat di `greenfield/cotc/pairing/alokasi/`:
*   `lemari.fox`: Manajer Pool.
*   `arena.fox`: Implementasi Laci.
*   `buffer_ganda.fox`: Implementasi Nampan & Logika Swap.
*   `penunjuk.fox`: Definisi Tiket.

---

## 4. Manajemen Kegagalan: "The Dumpbox"

Kegagalan alokasi atau proses bukan akhir, melainkan data baru.

*   **Konsep:** Jika data tumpah (gagal diproses/dialokasikan), jangan Panic. Simpan "Tumpahan" itu ke dalam kotak khusus.
*   **File .z:** Format file untuk menyimpan snapshot kegagalan (`Failure State`).
*   **Tujuan:** Agar FoxVM di masa depan bisa membaca `.z` ini untuk:
    *   *Replay:* Coba lagi nanti.
    *   *Learn:* Skip perintah serupa di masa depan.
    *   *Audit:* User bisa melihat apa yang tumpah.
*   **Lokasi:** `greenfield/cotc/pairing/catch/` (berisi `vmdumpbox.fox` dan `z_file.fox`).

---

**Pesan untuk Sesi Berikutnya:**
> "Jangan ubah filosofi ini tanpa diskusi. Kita sedang membangun Kernel di atas Virtual Machine."

---
*Disimpan oleh Jules AI untuk Vzoel Fox's.*
