## Sprint 5.1 Test Results

### OCaml Build: [PASS]
- **Build output:** Build berhasil tanpa error, hanya ada beberapa peringatan tentang token dan state yang tidak digunakan, yang dapat diabaikan untuk saat ini.
- **Any warnings:** Ya, terdapat peringatan tentang *shift/reduce conflicts* dan token yang tidak digunakan, namun ini tidak menghalangi pembuatan executable.

### Sample Compilation: [PASS with issues]
- **test_tipe.morph:** [PASS] Berhasil dikompilasi menjadi `test_tipe.json`.
- **test_pilih.morph:** [PASS] Berhasil dikompilasi menjadi `test_pilih.json`.
- **test_jodohkan.morph:** [FAIL] Gagal dikompilasi dengan `Parse error at line 4, column 10`.

### Deserialization: [PASS]
- **TipeDeklarasi:** [PASS] Berhasil dideserialisasi dari `test_tipe.json`.
- **Pilih:** [PASS] Berhasil dideserialisasi dari `test_pilih.json`.
- **Jodohkan:** [N/A] Tidak bisa diuji karena kompilasi gagal.

### Integration Tests (pytest): [PASS]
- Seluruh 290 tes lulus setelah menginstal dependensi pengembangan (`requirements-dev.txt`). Tidak ada regresi yang terdeteksi.

### End-to-End Execution: [PASS after fix]
- Eksekusi `test_tipe.json` berhasil pada percobaan pertama.
- Eksekusi `test_pilih.json` awalnya gagal karena bug `AttributeError` di interpreter.
- Setelah bug di `transisi/translator.py` diperbaiki, eksekusi `test_pilih.json` berhasil dan menghasilkan output yang benar.

### Issues Found:
1. **OCaml Parser Bug for `jodohkan`**
   - **Error:** `Parse error at line 4, column 10` saat mengkompilasi sintaks `jodohkan`.
   - **Analysis:** Ini adalah bug kritis di `universal/parser.mly` yang menghalangi penggunaan fitur pattern matching. Perlu perbaikan di sisi OCaml.
2. **Interpreter Bug for `pilih`**
   - **Error:** `AttributeError: 'list' object has no attribute 'terima'` saat mengeksekusi AST untuk `pilih`.
   - **Analysis:** Interpreter tidak menangani dengan benar kasus di mana `ketika` memiliki beberapa nilai (misalnya, `ketika 1, 2`). **Status: FIXED**.

### Next Steps:
- [x] Fix Issue #2 (Interpreter Bug for `pilih`) - **DONE**
- [ ] Investigate and fix Issue #1 (OCaml Parser Bug for `jodohkan`)
- [ ] Create a comprehensive test for `jodohkan` once the parser is fixed.
- [ ] Finalize and submit the current working code.
