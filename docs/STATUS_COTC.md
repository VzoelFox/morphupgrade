# Status Pustaka Standar (COTC)

Dokumen ini mengklasifikasikan modul-modul dalam `greenfield/cotc` berdasarkan tingkat kemandirian (Self-Hosting) dan kemurnian logika Morph.

## Klasifikasi Status

*   🟢 **Murni (Pure):** Logika ditulis 100% dalam Morph. Ketergantungan pada Python (`pinjam`) hanya diperbolehkan untuk alokasi memori dasar (seperti membuat objek Bytes/List/Dict) atau syscall yang terisolasi di `foxys`.
*   🟡 **Hibrida (Hybrid):** Logika utama dalam Morph, tetapi masih ada fungsi helper yang meminjam fungsi built-in Python (misal `str.find`, `slice`) yang belum ada opcode-nya.
*   🔴 **Wrapper:** Hanya pembungkus tipis di atas library Python. Jika backend diganti, modul ini mati total.
*   ⚠️ **Legacy:** Kode lama yang belum diaudit atau masih menggunakan pola lama.

## Tabel Audit

| Modul | Status | Commit Terakhir | Keterangan |
| :--- | :---: | :--- | :--- |
| **Data & Struktur** | | | |
| `cotc/data/json.fox` | 🟢 | `bec6d61` | Parser Recursive Descent murni. Terverifikasi via `audit_cotc.fox`. |
| `cotc/data/base64.fox` | 🟢 | `bec6d61` | Logika Bitwise murni. Telah diperbaiki (init Map, UTF-8 handler). Terverifikasi. |
| `cotc/struktur/tumpukan.fox` | 🟢 | - | Wrapper List Morph. |
| `cotc/struktur/antrian.fox` | 🟢 | - | Wrapper List Morph. |
| `cotc/bytes.fox` | 🟢 | - | Implementasi `pack/unpack` murni bitwise. |
| **Logika & Matematika** | | | |
| `cotc/logika/*.fox` | 🟢 | - | Semua logika formal, unifikasi, dan ZFC adalah murni. |
| `cotc/matematika/*.fox` | 🟢 | - | Algoritma matematika murni. |
| `cotc/waktu/dtime.fox` | 🟢 | - | Logika kalender dan waktu murni (Epoch converter). |
| **Protokol & Jaringan** | | | |
| `cotc/protokol/url.fox` | 🟢 | - | Parser URL murni string manipulation. |
| `cotc/protokol/http.fox` | 🟢 | - | Serializer/Parser HTTP 1.1 murni string/bytes. |
| `cotc/netbase/*.fox` | 🔴⚠️ | - | **HUTANG TEKNIS.** Banyak wrapper library Python (`hashlib`, `cryptography`, `aiohttp`). |
| **Sistem & IO** | | | |
| `cotc/sistem/foxys.fox` | 🟡 | - | Interface Syscall standar. Saat ini wrap Python `time`, `os`, `socket`. |
| `cotc/io/berkas.fox` | 🔴 | `125046e` | Wrapper intrinsik VM `_io_*`. Menggunakan tipe `Hasil` (Sukses/Gagal). Terverifikasi. |
| `cotc/stdlib/teks.fox` | 🟢 | `061e95e` | **Murni.** Implementasi manual untuk `kecil`, `besar`, `mengandung`, `ganti` tanpa FFI Python. Terverifikasi. |

## Rekomendasi Perbaikan

1.  **Tulis Ulang `netbase`:** Modul `netbase` harus dibersihkan. Fitur kriptografi dan database harus ditulis ulang menggunakan algoritma native Morph jika memungkinkan, atau dibuatkan interface standar via `foxys` jika butuh performa native (C/Rust).
2.  **Optimasi String:** Implementasi murni `teks.fox` saat ini O(N) atau O(N*M). Jika performa menjadi isu, pertimbangkan menambahkan Opcode VM khusus di masa depan.
3.  **Standarisasi Error IO:** Pastikan semua modul IO menggunakan pola `Hasil` (Sukses/Gagal) secara konsisten.

---
*Terakhir diperbarui: Migrasi Teks Murni - Commit `061e95e`*
