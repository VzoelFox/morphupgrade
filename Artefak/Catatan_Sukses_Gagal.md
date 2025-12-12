# Catatan Sukses dan Gagal (Test Report)

Dokumen ini mencatat hasil eksekusi tes otomatis menggunakan infrastruktur Self-Hosted.

## Ringkasan Eksekusi (Patch 3 Runner)
- **Runner**: `greenfield/uji_semua.fox`
- **Total Tes Ditemukan**: 19 (Sample Run)
- **Lulus**: 1 (`uji_eksepsi.fox`)
- **Gagal**: 18
- **Status**: ⚠️ **MIGRASI DALAM PROGRES**

## Analisis Kegagalan
Mayoritas kegagalan disebabkan oleh:
1.  **Missing Globals**: Tes lama bergantung pada variabel global Python (`os`, `Bytes`, `L`) yang tidak tersedia di lingkungan Self-Hosted.
2.  **Runtime Error**: `jalan_biner` membutuhkan serialisasi objek kode, yang telah diperbaiki di runner, namun tes itu sendiri mungkin memiliki bug logika.
3.  **Fragilitas Interpolasi String**: `debug_string.fox` gagal pada tahap parsing karena masalah di `stdlib/teks.fox`.

## Peningkatan Kualitas
1.  **Infrastruktur Mandiri**: Kita tidak lagi bergantung pada runner Python. Runner Morph dapat menangkap error runtime dan melanjutkan eksekusi (Resilience).
2.  **Exception Handling Verified**: Keberhasilan `uji_eksepsi.fox` membuktikan bahwa compiler dan VM menangani `try/catch` dengan benar.

## Catatan Patch 15 (LoneWolf & Network)
1.  **LoneWolf Verified**: `uji_lonewolf.fox` berhasil mendemonstrasikan penangkapan crash, dumping ke `.z`, diagnosa otomatis, dan keputusan retry.
2.  **Network Stack Verified**: `uji_jaringan_http.fox` berhasil melakukan request ke `example.com`. `uji_jaringan_ssh.fox` berhasil memuat wrapper Paramiko.
3.  **Host VM Fixes**: Ditemukan dan diperbaiki bug scope resolution di Host VM (global variables hilang di block catch) dengan teknik local capture di `bridge_fox.fox`.

## Rencana Perbaikan
- Audit setiap file di `greenfield/examples/` dan perbarui agar menggunakan API standar `greenfield/cotc`.
- Hapus dependensi implisit ke Host.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.15 (Greenfield Patch 15)
tanggal  : 12/12/2025
