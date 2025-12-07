# Morph: Bahasa Pemrograman Self-Hosting (Python-to-Morph Bootstrap)

> *"The Soul of Independent AGI"*

Selamat datang di repositori resmi bahasa pemrograman **Morph**. Proyek ini bertujuan menciptakan ekosistem bahasa pemrograman yang mandiri, dimulai dari fondasi Python hingga akhirnya berjalan di atas mesin virtualnya sendiri.

## Status Proyek: 🟡 **Self-Hosting (Hybrid / Partial)**

Saat ini, Morph memiliki dua sisi:
1.  **Host Environment (IVM):** VM berbasis Python yang **STABIL**, digunakan untuk menjalankan Compiler Morph dan Development Tools.
2.  **Native Environment (Greenfield):** VM eksperimental yang ditulis dalam Morph murni. Saat ini dalam status **BETA dengan REGRESI**.
    *   ✅ Aritmatika & Logika Murni.
    *   ✅ Native Data Structures (`Tumpukan`, `Antrian`).
    *   ✅ Native I/O (File & System via Opcode).
    *   ✅ **Native Base64:** Implementasi Pure Morph tanpa FFI.
    *   ⚠️ **Isu:** Eksekusi kode kompleks (seperti Lexer sendiri) masih gagal karena bug interop.
    *   ⚠️ **Dependency:** Modul jaringan lama (`netbase`) masih menggunakan FFI Python.

### Fitur Utama
*   **Sintaks Bahasa Indonesia:** `fungsi`, `jika`, `maka`, `akhir`, `biar`, `ubah`.
*   **Modular:** Sistem `ambil` (import) dan `pinjam` (FFI) yang robust.
*   **Pattern Matching:** `jodohkan ... dengan ...` yang mendukung list dan varian.
*   **Data Structures:** Implementasi `Tumpukan` dan `Antrian` murni dalam Morph.
*   **Binary Compilation:** Kompilasi ke format binary `.mvm` ("VZOEL FOXS") yang efisien.

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

# Tes Native I/O & Sistem (Stabil)
python3 -m ivm.main greenfield/examples/test_foxys_io.fox
```

### 3. Verifikasi Penuh
Untuk menjalankan seluruh suite tes:
```bash
python3 run_ivm_tests.py
```

## Lisensi
MIT License.
