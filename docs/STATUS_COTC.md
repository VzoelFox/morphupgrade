# Status Pustaka Standar (COTC)

Dokumen ini mengklasifikasikan modul-modul dalam `greenfield/cotc` berdasarkan tingkat kemandirian (Self-Hosting) dan kemurnian logika Morph.

> **CATATAN AUDIT:** Status di bawah ini telah diperbarui berdasarkan pemeriksaan kode aktual. Beberapa klaim "Native" sebelumnya telah diturunkan statusnya menjadi "Stub" atau "Hybrid" karena ditemukan implementasi yang kosong atau bergantung pada FFI.

## Klasifikasi Status

*   🟢 **Murni (Pure):** Logika ditulis 100% dalam Morph.
*   🟡 **Hibrida (Hybrid):** Logika utama dalam Morph, tetapi meminjam fungsi Python (`pinjam`) untuk fitur kritis.
*   🔴 **Broken/Stub:** Kode ada, tetapi fungsi dasarnya kosong (`maka akhir`) atau belum terhubung ke VM.
*   🟣 **Native Opcode:** Menggunakan Opcode intrinsik VM yang **terverifikasi** berfungsi.

## Tabel Audit

| Modul | Status | Keterangan Audit |
| :--- | :---: | :--- |
| **Data & Struktur** | | |
| `cotc/data/json.fox` | 🟢 | Parser Recursive Descent murni. Terverifikasi. |
| `cotc/data/base64.fox` | 🟢 | Logika Bitwise murni. Terverifikasi. |
| `cotc/struktur/tumpukan.fox` | 🟢 | Wrapper List Morph. |
| `cotc/struktur/antrian.fox` | 🟢 | Wrapper List Morph. |
| `cotc/bytes.fox` | 🟢 | Implementasi `pack/unpack` murni bitwise. |
| **Logika & Matematika** | | |
| `cotc/logika/*.fox` | 🟢 | Logika formal & unifikasi murni. |
| `cotc/matematika/*.fox` | 🟢 | Algoritma matematika murni. |
| **Protokol & Jaringan** | | |
| `cotc/protokol/url.fox` | 🟢 | Parser URL murni string manipulation. |
| `cotc/protokol/http.fox` | 🟢 | Serializer/Parser HTTP 1.1 murni. |
| `cotc/railwush/*.fox` | 🟡 | **Hibrida (FFI).** Fungsional dan stabil, tetapi menggunakan `pinjam` untuk `datetime`, `os`, `platform`. Bukan murni. |
| `cotc/netbase/*.fox` | ❌ | **DIHAPUS.** |
| **Sistem & IO** | | |
| `cotc/sistem/foxys.fox` | 🟣 | **Native Intrinsik.** Opcode `SYS_*` terhubung dan terverifikasi (Waktu, Tidur, Platform). |
| `cotc/io/berkas.fox` | 🟣 | **Native Intrinsik.** Opcode `IO_*` terhubung dan terverifikasi (Baca, Tulis, Hapus). |
| `cotc/stdlib/teks.fox` | 🟣 | **Native Intrinsik.** Terverifikasi menggunakan Opcode `STR_*` via `builtins_str`. |

## Rekomendasi Perbaikan

1.  **Wiring Builtins:** Perbaiki `greenfield/cotc/stdlib/core.fox` agar fungsi-fungsi seperti `_io_buka` benar-benar memanggil Opcode, bukan blok kosong.
2.  **Hapus Klaim Palsu:** Jangan tandai modul sebagai "Native" jika hanya berupa definisi fungsi kosong.

---
*Terakhir diperbarui: Perbaikan Wiring I/O (Core.fox).*
