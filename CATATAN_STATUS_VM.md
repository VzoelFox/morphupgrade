# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟢 **Aktif (Beta - Lexer Capable)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan stabil.
*   Limitasi Parser Bootstrap telah diatasi sepenuhnya.
*   **Interop Host Object:** Native VM kini bisa memanggil Method Host (`BoundMethod`) dan mengakses atribut Host Object via Bridge.
*   **Lexer Execution:** Native VM terbukti mampu memuat dan menjalankan logika `greenfield/lx_morph.fox` (Self-Hosted Lexer).

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
| `LOAD_VAR` | ✅ | Stabil |
| `STORE_VAR` | ✅ | Stabil |
| **Control Flow** | | |
| `JMP` | ✅ | |
| `JMP_IF_FALSE` | ✅ | |
| `CALL` | ✅ | Support: NativeFunc, Morph Code, Host BoundMethod |
| `RET` | ✅ | |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | |
| `BUILD_DICT` | ✅ | |
| **Objects** | | |
| `LOAD_ATTR` | ✅ | Support: Dict & Host/Morph Instance via Bridge |
| `STORE_ATTR` | ✅ | |
| **Modules** | | |
| `IMPORT` | ✅ | Menggunakan `ini.modules` cache |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Stabilisasi Interop:** Menyempurnakan pemanggilan `FungsiNative` di dalam Native VM (type check string issue).
2.  **Lexer Completion:** Memastikan Lexer berjalan sampai selesai tanpa infinite loop (perbaikan logika `CALL` return value).
3.  **Bootstrap Penuh:** Menjalankan Compiler (`morph.mvm`) di atas Native VM.

---
*Diperbarui terakhir: Sukses menjalankan loop Lexer Morph di atas Native VM.*
