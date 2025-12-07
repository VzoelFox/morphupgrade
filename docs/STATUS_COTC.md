# Status Pustaka Standar (COTC)

Dokumen ini mengklasifikasikan modul-modul dalam `greenfield/cotc` berdasarkan tingkat kemandirian (Self-Hosting) dan kemurnian logika Morph.

## Klasifikasi Status

*   🟢 **Murni (Pure):** Logika ditulis 100% dalam Morph. Ketergantungan pada Python (`pinjam`) hanya diperbolehkan untuk alokasi memori dasar (seperti membuat objek Bytes/List/Dict) atau syscall yang terisolasi di `foxys`.
*   🟡 **Hibrida (Hybrid):** Logika utama dalam Morph, tetapi masih ada fungsi helper yang meminjam fungsi built-in Python (misal `str.find`, `slice`) yang belum ada opcode-nya.
*   🔴 **Wrapper:** Hanya pembungkus tipis di atas library Python. Jika backend diganti, modul ini mati total.
*   ⚠️ **Legacy:** Kode lama yang belum diaudit atau masih menggunakan pola lama.

## Tabel Audit

| Modul | Status | Keterangan |
| :--- | :---: | :--- |
| **Data & Struktur** | | |
| `cotc/data/json.fox` | 🟢 | Parser Recursive Descent murni. Menggunakan `kunci()` native. |
| `cotc/data/base64.fox` | 🟡 | Logika Bitwise murni. Menggunakan `utf-8 encode` Python. |
| `cotc/struktur/tumpukan.fox` | 🟢 | Wrapper List Morph. |
| `cotc/struktur/antrian.fox` | 🟢 | Wrapper List Morph. |
| `cotc/bytes.fox` | 🟢 | Implementasi `pack/unpack` murni bitwise. |
| **Logika & Matematika** | | |
| `cotc/logika/*.fox` | 🟢 | Semua logika formal, unifikasi, dan ZFC adalah murni. |
| `cotc/matematika/*.fox` | 🟢 | Algoritma matematika murni. |
| `cotc/waktu/dtime.fox` | 🟢 | Logika kalender dan waktu murni (Epoch converter). |
| **Protokol & Jaringan** | | |
| `cotc/protokol/url.fox` | 🟢 | Parser URL murni string manipulation. |
| `cotc/protokol/http.fox` | 🟢 | Serializer/Parser HTTP 1.1 murni string/bytes. |
| `cotc/netbase/*.fox` | 🔴⚠️ | **HUTANG TEKNIS.** Banyak wrapper library Python (`hashlib`, `cryptography`, `aiohttp`). |
| **Sistem & IO** | | |
| `cotc/sistem/foxys.fox` | 🟡 | Interface Syscall standar. Saat ini wrap Python `time`, `os`, `socket`. |
| `cotc/io/berkas.fox` | 🔴 | Wrapper intrinsik VM `_io_*`. |
| `cotc/stdlib/teks.fox` | 🟡 | Menggunakan `py.slice`. Perlu migrasi ke Opcode `SLICE`. |

## Rekomendasi Perbaikan

1.  **Migrasi `teks.fox`:** Ganti `py.slice` dengan Opcode `SLICE` (59) yang sudah diimplementasikan di VM.
2.  **Tulis Ulang `netbase`:** Modul `netbase` harus dibersihkan. Fitur kriptografi dan database harus ditulis ulang menggunakan algoritma native Morph jika memungkinkan, atau dibuatkan interface standar via `foxys` jika butuh performa native (C/Rust).
3.  **Native String Ops:** Implementasi `find`, `split`, `replace` secara native di `teks.fox` untuk menghilangkan ketergantungan method string Python.

---
*Terakhir diperbarui: Audit Fase 2 (FoxProtocol)*
