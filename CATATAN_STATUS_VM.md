# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan stabil.
*   **Interop Host Object:** Native VM kini bisa memanggil Method Host (`BoundMethod`), mengakses atribut Host Object via Bridge, dan menginstansiasi Host Class.
*   **Exception Handling:** Mendukung `PUSH_TRY`, `POP_TRY`, dan `THROW` untuk penanganan error.
*   **Lexer Execution:** Terverifikasi menjalankan `greenfield/lx_morph.fox`.
*   **Parser Execution:** Terverifikasi menjalankan `greenfield/crusher.fox` dan menghasilkan AST.
*   **Compiler Execution:** Test harness (`test_vm_compiler_wip.fox`) berhasil berjalan.
    *   **BUG AKTIF:** Runtime Error `LOAD_INDEX` pada `nil` saat eksekusi logika kompiler.

## 1. Matriks Opcode

| Opcode | Status | Catatan |
| :--- | :---: | :--- |
| **Stack Ops** | | |
| `PUSH_CONST` | ✅ | |
| `POP` | ✅ | |
| `DUP` | ✅ | |
| **Arithmetic** | | |
| `ADD` (`+`) | ✅ | Terverifikasi Native |
| `SUB` (`-`) | ✅ | Terverifikasi Native |
| `MUL` (`*`) | ✅ | Terverifikasi Native |
| `DIV` (`/`) | ✅ | Terverifikasi Native |
| `MOD` (`%`) | ✅ | Terverifikasi Native |
| `BIT_AND` (`&`) | ❓ | Perlu verifikasi untuk `bytes.fox` native |
| `BIT_OR` (`|`) | ❓ | Perlu verifikasi untuk `bytes.fox` native |
| `LSHIFT` (`<<`) | ❓ | Perlu verifikasi untuk `bytes.fox` native |
| `RSHIFT` (`>>`) | ❓ | Perlu verifikasi untuk `bytes.fox` native |
| **Logic/Comparison** | | |
| `EQ` (`==`) | ✅ | |
| `GT` (`>`) | ✅ | Terverifikasi Native |
| `LT` (`<`) | ✅ | |
| `AND`, `OR`, `NOT` | ✅ | Terverifikasi di Lexer logic |
| **Variable Access** | | |
| `LOAD_LOCAL` | ✅ | Stabil |
| `STORE_LOCAL` | ✅ | Stabil |
| `LOAD_VAR` | ✅ | Support `ProxyHostGlobals` |
| `STORE_VAR` | ✅ | Stabil |
| **Control Flow** | | |
| `JMP` | ✅ | |
| `JMP_IF_FALSE` | ✅ | |
| `CALL` | ✅ | Support: NativeFunc, Morph Code, Host BoundMethod, **Host Class (Instantiation)** |
| `RET` | ✅ | |
| **Exception Handling** | | |
| `PUSH_TRY` | ✅ | Implementasi Stack-Based |
| `POP_TRY` | ✅ | |
| `THROW` | ✅ | Unwind Stack otomatis |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | |
| `BUILD_DICT` | ✅ | |
| `LOAD_INDEX` | ✅ | **BUG:** Crash jika target `nil`. Perlu guard/error lebih jelas. |
| `STORE_INDEX` | ✅ | Support Host Object via `_setitem` |
| **Objects** | | |
| `LOAD_ATTR` | ✅ | Support: Dict & Host/Morph Instance via Bridge |
| `STORE_ATTR` | ✅ | |
| **Modules** | | |
| `IMPORT` | ✅ | Menggunakan `ini.modules` cache |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Migrasi Native Stdlib (Hutang Teknis):**
    *   **`bytes.fox`:** Implementasi `pack/unpack` native (Bitwise). **(SELANJUTNYA)**
    *   **`himpunan.fox`:** Implementasi Set native.
2.  **Debugging Compiler Execution:** Memperbaiki bug runtime `LOAD_INDEX`.
3.  **VM Optimization:** Implementasi Constant Folding sederhana.

---
*Diperbarui terakhir: Dokumentasi Hutang Teknis & Roadmap Native.*
