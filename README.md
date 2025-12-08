# Morph: Bahasa Pemrograman Self-Hosting

> *"The Soul of Independent AGI"*

Selamat datang di repositori resmi bahasa pemrograman **Morph**. Proyek ini bertujuan menciptakan ekosistem bahasa pemrograman yang mandiri (Self-Hosting), dimulai dari fondasi Python hingga akhirnya berjalan di atas mesin virtualnya sendiri.

## Status Proyek: 🚀 **Self-Hosting (Compiler Mandiri)**

Saat ini, Morph telah mencapai tonggak sejarah penting:
1.  **Compiler Self-Hosting (Stabil):** Compiler Morph (`greenfield/kompiler`) sudah ditulis sepenuhnya dalam bahasa Morph dan mampu mengkompilasi dirinya sendiri (diverifikasi oleh CI/CD).
2.  **Native VM (Beta Stabil):** VM eksperimental (`greenfield/fox_vm`) telah mencapai stabilitas untuk eksekusi logika inti, struktur data, dan serialisasi bytecode tanpa ketergantungan FFI.
3.  **Pustaka Standar Murni (Pure Morph):** Modul inti seperti `teks` (string), `matematika` (trigonometri/kalkulus), `himpunan` (set), dan `struktur` (stack/queue/serialization) telah diimplementasikan ulang tanpa ketergantungan Python.

### Fitur Utama
*   **Sintaks Bahasa Indonesia:** `fungsi`, `jika`, `maka`, `akhir`, `biar`, `ubah`.
*   **Modular:** Sistem `ambil` (import) dan `pinjam` (FFI) yang robust.
*   **Pattern Matching:** `jodohkan ... dengan ...` yang mendukung list dan varian.
*   **Pure Morph Stdlib:** Algoritma string (`kmp`/naive), matematika (`taylor series`), dan struktur data (`set`, `queue`) ditulis dalam Morph.
*   **Binary Compilation:** Kompilasi ke format binary `.mvm` ("VZOEL FOXS") yang deterministik.

## Struktur Direktori

*   `transisi/`: Komponen bootstrap lama (Lexer/Parser Python) - *Maintenance Mode*.
*   `ivm/`: Host Virtual Machine (Python) & Host Compiler - *Stable Foundation*.
*   `greenfield/`: **(Inti Pengembangan)** Source code Self-Hosted Compiler & Native VM.
    *   `kompiler/`: Logika kompilasi Morph-to-Bytecode.
    *   `fox_vm/`: Native VM implementation.
    *   `cotc/`: Core of the Core (Standard Library).

## Cara Menjalankan

### 1. Persiapan
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Kode
Gunakan runner `ivm/main.py` untuk menjalankan file `.fox` atau binary `.mvm`:

```bash
# Menjalankan Source Code
python3 -m ivm.main greenfield/examples/hello_world.fox

# Membangun Binary (Menggunakan Self-Hosted Compiler)
python3 -m ivm.main greenfield/morph.fox build greenfield/examples/hello_world.fox

# Menjalankan Binary
python3 -m ivm.main greenfield/examples/hello_world.fox.mvm
```

### 3. Verifikasi Penuh
Untuk menjalankan seluruh suite tes:
```bash
python3 run_ivm_tests.py
```

## Kontribusi & Roadmap
Fokus pengembangan saat ini adalah **Tier 1 (Essential Stdlib)** dan **Native VM Optimization**. Lihat `CATATAN_STATUS_VM.md` untuk detail teknis.

## Lisensi
MIT License.
