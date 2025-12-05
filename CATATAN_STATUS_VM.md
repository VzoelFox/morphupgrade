# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟢 **Aktif (Beta - Lexer Executed)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan stabil.
*   **Interop Host Object:** Native VM kini bisa memanggil Method Host (`BoundMethod`), mengakses atribut Host Object via Bridge, dan menginstansiasi Host Class.
*   **Interop FungsiNative:** VM menggunakan Duck Typing untuk mendeteksi instance `FungsiNative`.
*   **Lexer Execution:** Native VM terbukti mampu memuat dan menjalankan logika `greenfield/lx_morph.fox` (Self-Hosted Lexer) hingga menghasilkan Token.

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
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | |
| `BUILD_DICT` | ✅ | |
| `LOAD_INDEX` | ✅ | Support Host Object via `_getitem` |
| `STORE_INDEX` | ✅ | Support Host Object via `_setitem` |
| **Objects** | | |
| `LOAD_ATTR` | ✅ | Support: Dict & Host/Morph Instance via Bridge |
| `STORE_ATTR` | ✅ | |
| **Modules** | | |
| `IMPORT` | ✅ | Menggunakan `ini.modules` cache |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Stabilisasi Interop:** Menyempurnakan pemanggilan `FungsiNative` di dalam Native VM (type check string issue) - **(SELESAI)**.
2.  **Lexer Completion:** Memastikan Lexer berjalan sampai selesai - **(SELESAI)**.
3.  **Bootstrap Penuh:** Menjalankan Compiler (`morph.mvm`) di atas Native VM.

---
*Diperbarui terakhir: Sukses menjalankan Lexer.buat_token di Native VM.*
