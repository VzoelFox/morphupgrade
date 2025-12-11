# Update Log: Greenfield Patch 5

**Versi:** 0.1.5
**Tanggal:** 11 Desember 2025
**Fokus:** Pembersihan Technical Debt & Inisialisasi Native VM (Rust)

## 1. Arsitektur Baru: Native VM (Rust)
Kami telah memulai langkah besar menuju kemandirian penuh dengan menginisialisasi proyek Native VM berbasis Rust.
- **Lokasi:** `greenfield/morph_vm/`
- **Status:** Pre-Alpha / Experimental.
- **Fitur Saat Ini:**
    - Struktur proyek Cargo (Edition 2021).
    - Parser dasar format `.mvm` (Magic Bytes, Header, Module Name).
- **Tujuan:** Menggantikan Host VM (Python) secara bertahap.

## 2. Refactoring Kriptografi & Railwush
Modul Railwush (sistem profil & token) yang sebelumnya menyebabkan masalah pada CI/CD (karena efek samping file) telah diarsipkan.
- **Dihapus/Diarsipkan:** Folder `greenfield/cotc/railwush/` dipindahkan ke `TODO/railwush_concept/`.
- **Baru:** Modul `greenfield/cotc/stdlib/kripto.fox`.
    - Menyediakan fungsi kriptografi stateless (XOR Cipher, SHA256 Wrapper).
    - Aman untuk digunakan di CI/CD tanpa efek samping file.

## 3. Perbaikan Infrastruktur (CI/CD)
- **Pytest:** Konfigurasi `pytest.ini` diperbarui untuk mengabaikan folder `archived_morph`, mencegah kegagalan tes pada kode lawas.
- **Workflow:** Workflow Github Actions dibersihkan dari langkah-langkah yang tidak relevan.

## 4. Syscalls (Konfirmasi)
Sesuai rencana Patch 5, layer `syscalls.fox` telah dikonfirmasi sebagai satu-satunya gerbang interaksi ke Host System, mempersiapkan migrasi ke Rust VM.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
