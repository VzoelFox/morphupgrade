# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan stabil.
*   **Interop Host Object:** Native VM kini bisa memanggil Method Host (`BoundMethod`), mengakses atribut Host Object via Bridge, dan menginstansiasi Host Class.
*   **Exception Handling:** Mendukung `PUSH_TRY`, `POP_TRY`, dan `THROW` untuk penanganan error. Terverifikasi oleh `test_vm_features.fox`.
*   **OOP Native:** Mendukung `BUILD_CLASS`, `BUILD_FUNCTION`, `CALL` (Instantiation), `LOAD_ATTR` (BoundMethod). Terverifikasi oleh `test_vm_features.fox`.
*   **Lexer Execution:** Terverifikasi menjalankan `greenfield/lx_morph.fox`.
*   **Parser Execution:** Terverifikasi menjalankan `greenfield/crusher.fox` dan menghasilkan AST.
*   **Compiler Execution:** Test harness (`test_vm_compiler_wip.fox`) berhasil berjalan.

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
| `BIT_AND` (`&`) | ✅ | Terverifikasi Native |
| `BIT_OR` (`|`) | ✅ | Terverifikasi Native |
| `LSHIFT` (`<<`) | ✅ | Terverifikasi Native |
| `RSHIFT` (`>>`) | ✅ | Terverifikasi Native |
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
| `CALL` | ✅ | Support: NativeFunc, Morph Code, Host BoundMethod, **Host Class (Instantiation)**, **Native Class** |
| `RET` | ✅ | |
| **Exception Handling** | | |
| `PUSH_TRY` | ✅ | Implementasi Stack-Based (Native List Index Target) |
| `POP_TRY` | ✅ | |
| `THROW` | ✅ | Unwind Stack otomatis |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | |
| `BUILD_DICT` | ✅ | |
| `LOAD_INDEX` | ✅ | |
| `STORE_INDEX` | ✅ | Support Host Object via `_setitem` |
| **Objects** | | |
| `BUILD_CLASS` | ✅ | Native Implementation (Mock Dict) |
| `BUILD_FUNCTION` | ✅ | Native Implementation (Mock Dict) |
| `LOAD_ATTR` | ✅ | Support: Dict & Host/Morph Instance via Bridge |
| `STORE_ATTR` | ✅ | |
| **String Optimization** | | |
| `STR_LOWER` | ✅ | Native Lowercase |
| `STR_UPPER` | ✅ | Native Uppercase |
| `STR_FIND` | ✅ | Native Search (Index) |
| `STR_REPLACE` | ✅ | Native Replace |
| **System & I/O (Native)** | | |
| `SYS_TIME` | ✅ | Unix Timestamp |
| `SYS_SLEEP` | ✅ | Native Sleep |
| `SYS_PLATFORM` | ✅ | OS Info |
| `NET_SOCKET_NEW` | ✅ | Create Socket Handle |
| `NET_CONNECT` | ✅ | Connect Socket |
| `NET_SEND/RECV` | ✅ | Socket I/O |
| `NET_CLOSE` | ✅ | Close Socket |
| `IO_OPEN` | ✅ | Open File Handle |
| `IO_READ/WRITE` | ✅ | File I/O |
| `IO_CLOSE` | ✅ | Close Handle |
| **Modules** | | |
| `IMPORT` | ✅ | Menggunakan `ini.modules` cache |
| **System (Legacy)** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Migrasi Native Stdlib:**
    *   **`bytes.fox`:** ✅ **SELESAI** (Native Implementation).
    *   **`json.fox`:** ✅ **SELESAI** (Native Recursive Descent Parser).
    *   **`base64.fox`:** ✅ **SELESAI** (Native Bitwise Logic).
    *   **`teks.fox`:** ✅ **SELESAI** (Native Opcode).
    *   **`foxys.fox`:** ✅ **SELESAI** (Native Opcode).
    *   **`berkas.fox`:** ✅ **SELESAI** (Native Opcode).
    *   **`himpunan.fox`:** Implementasi Set native. **(SELANJUTNYA)**
2.  **Debugging Compiler Execution:** Memperbaiki bug runtime `LOAD_INDEX` pada compiler logic.
3.  **VM Optimization:** Implementasi Constant Folding sederhana.

---
*Diperbarui terakhir: Implementasi Opcode System, Network, I/O, dan String.*
