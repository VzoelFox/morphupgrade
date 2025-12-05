# Morph: Bahasa Pemrograman Self-Hosting (Python-to-Morph Bootstrap)

> *"The Soul of Independent AGI"*

Selamat datang di repositori resmi bahasa pemrograman **Morph**. Proyek ini bertujuan menciptakan ekosistem bahasa pemrograman yang sepenuhnya mandiri (self-hosting), dimulai dari fondasi Python hingga akhirnya berjalan di atas mesin virtualnya sendiri (Native FoxVM).

## Status Proyek: 🟢 **Self-Hosting (Hybrid & Native VM Beta)**

Saat ini, Morph memiliki dua "jantung":
1.  **Host Environment (IVM):** VM berbasis Python yang stabil, digunakan untuk menjalankan Compiler Morph.
2.  **Native Environment (Greenfield):** VM yang ditulis dalam Morph murni (`greenfield/fox_vm/`), kini mampu menjalankan aritmatika dan struktur data kompleks (`List`, `Map`, `Queue`, `Stack`).

### Fitur Utama
*   **Sintaks Bahasa Indonesia:** `fungsi`, `jika`, `maka`, `akhir`, `biar`, `ubah`.
*   **Modular:** Sistem `ambil` (import) dan `pinjam` (FFI) yang robust.
*   **Pattern Matching:** `jodohkan ... dengan ...` yang mendukung list dan varian.
*   **Native Data Structures:** Implementasi `Tumpukan` dan `Antrian` murni dalam Morph.

## Struktur Direktori

*   `transisi/`: Komponen bootstrap lama (Lexer/Parser Python).
*   `ivm/`: Host Virtual Machine (Python) & Host Compiler.
*   `greenfield/`: **(Inti Pengembangan)** Source code Self-Hosted Compiler & Native VM.
    *   `kompiler/`: Logika kompilasi Morph-to-Bytecode.
    *   `fox_vm/`: Native VM implementation.
    *   `cotc/`: Core of the Core (Standard Library).

## Cara Menjalankan

### 1. Persiapan
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Tes
Gunakan runner `ivm/main.py` untuk menjalankan file `.fox`:

```bash
# Tes Integrasi "Hello World"
python3 -m ivm.main greenfield/examples/hello_world.fox

# Tes Native VM (Data Structures)
python3 -m ivm.main greenfield/examples/test_struktur_lanjut.fox
```

### 3. Verifikasi Penuh
Untuk menjalankan seluruh suite tes:
```bash
python3 run_ivm_tests.py
```

## Lisensi
MIT License.
