# Panduan Pengembang Baru (Morph CLI Era)

**Versi:** 0.1.18 (Patch 18)
**Status:** Micro LLVM Pivot

Dokumen ini menjelaskan cara kerja ekosistem Morph yang baru dengan filosofi "Morph as Kernel" dan penggunaan CLI `morph`.

## Filosofi
Morph bukan lagi sekadar script yang jalan di atas Python. Morph adalah **Kernel** yang mengontrol **Driver** (C++/LLVM) untuk berinteraksi dengan hardware.

## Struktur Komando (The Poetic Syntax)

Kami menggunakan sintaks yang unik untuk CLI:

### 1. Menjalankan Program
Perintah:
```bash
./morph run morph make "<file.fox>"
```
*   `run`: Masuk mode eksekusi.
*   `morph`: Memanggil kernel Morph.
*   `make`: Instruksi untuk membangun/menjalankan target.

### 2. Instalasi Paket (Masa Depan)
Perintah:
```bash
./morph install "star spawn <paket.fall>"
```
*   `install`: Masuk mode paket manajer.
*   `star spawn`: Mantra untuk mengekstrak dan menghidupkan paket data (`.fall`).

## Cara Membangun Driver
Driver ditulis dalam C++ (`greenfield/micro_llvm_driver/`).
Untuk membangunnya:
```bash
cd greenfield/micro_llvm_driver
make
```
Ini akan menghasilkan file binary `morph` di root repositori.

---
**Founder:** Vzoel Fox's (Lutpan)
**Engineer:** Jules AI
