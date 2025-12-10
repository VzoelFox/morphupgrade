# Update Patch 4: Compiler Completeness & Native VM Maturity

**Tanggal:** 10/12/2025
**Engineer:** Jules AI Agent

## 1. Misi Utama
Mencapai paritas fitur bahasa antara Self-Hosted Compiler dan Bootstrap Compiler, serta mematangkan Native VM untuk mendukung eksekusi logika kompleks (OOP, Pattern Matching).

## 2. Implementasi

### A. Self-Hosted Compiler (`greenfield/kompiler`)
1.  **Dukungan Import:** Mengimplementasikan visitor untuk `AmbilSemua`, `AmbilSebagian`, dan `Pinjam`. Compiler kini menghasilkan opcode `IMPORT` yang benar.
2.  **Pattern Matching (`jodohkan`):** Implementasi penuh logika pencocokan pola, termasuk:
    *   Pencocokan Literal (Angka, Teks).
    *   Pencocokan Varian (`Sukses(x)`).
    *   Backtracking stack state menggunakan opcode `SNAPSHOT`/`RESTORE`.
3.  **Deklarasi Tipe (`tipe`):** Kompilasi definisi tipe varian menjadi fungsi konstruktor native menggunakan `BUILD_VARIANT`.

### B. Native VM (`greenfield/fox_vm`)
1.  **OOP Support:**
    *   Implementasi *Method Lookup* di `_do_load_attr`: Jika atribut tidak ada di instance, VM mencari di kelas (`_kelas`).
    *   Implementasi *Bound Method*: VM membungkus metode dengan instance (`MetodeTerikat`) dan menyuntikkan `ini` (self) saat dipanggil.
2.  **Opcode Baru:** Implementasi `IS_INSTANCE`, `IS_VARIANT`, `UNPACK_VARIANT` (push items), `BUILD_VARIANT`, `SNAPSHOT`, `RESTORE`, `DISCARD_SNAPSHOT`.
3.  **Stability:** Perbaikan crash pada `CALL` fungsi native (pembungkusan instruksi raw ke dictionary kompatibel).

### C. Host VM Patch (`ivm`)
*   **Hybrid Bytecode:** Patch pada `standard_vm.py` untuk mendukung format instruksi `BUILD_VARIANT` dan `IS_VARIANT` baik dari Bootstrap Compiler (3-tuple) maupun Self-Hosted Compiler (Stack-based 2-tuple). Ini memastikan kompatibilitas transisi.

### D. Standard Library Refactor
*   **`json.fox`**: Refactoring total parser JSON untuk menggunakan `jodohkan`. Kode menjadi lebih deklaratif dan bersih.
*   **Fix Lexer**: Perbaikan escaping karakter `{` dalam string literal untuk mencegah konflik interpolasi string.

## 3. Hasil Validasi
*   `test_pattern_matching.fox`: **LULUS** (Literal & Varian).
*   `test_json.fox`: **LULUS** (Refactored implementation).
*   `test_vm_parser_wip.fox`: **LULUS** (Native VM menjalankan Self-Hosted Parser).
*   `manual_native_oop.fox`: **LULUS** (Verifikasi OOP Native).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.4 (Greenfield Patch 4)
tanggal  : 10/12/2025
