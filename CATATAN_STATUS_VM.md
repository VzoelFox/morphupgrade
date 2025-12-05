# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟢 **Aktif (Alpha)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan telah direfactor untuk modularitas.
*   Limitasi Parser Bootstrap telah diatasi menggunakan teknik pemecahan fungsi.
*   Integrasi Builtin (`panjang`, `tulis`) sudah berfungsi (dengan wrapper).

## 1. Matriks Opcode

| Opcode | Status | Catatan |
| :--- | :---: | :--- |
| **Stack Ops** | | |
| `PUSH_CONST` | ✅ | |
| `POP` | ✅ | |
| `DUP` | ✅ | |
| **Arithmetic** | | |
| `ADD` (`+`) | ✅ | |
| `SUB` (`-`) | ✅ | |
| `MUL` (`*`) | ✅ | |
| `DIV` (`/`) | 🟡 | Belum diimplementasi |
| `MOD` (`%`) | 🟡 | Belum diimplementasi |
| **Logic/Comparison** | | |
| `EQ` (`==`) | ✅ | |
| `GT` (`>`) | 🟡 | Belum diimplementasi |
| `LT` (`<`) | ✅ | |
| **Variable Access** | | |
| `LOAD_LOCAL` | 🟡 | Perlu verifikasi scope |
| `STORE_LOCAL` | 🟡 | Perlu verifikasi scope |
| `LOAD_VAR` | ✅ | Mencakup Lokal & Global sederhana |
| `STORE_VAR` | ✅ | Mencakup Lokal sederhana |
| **Control Flow** | | |
| `JMP` | ✅ | |
| `JMP_IF_FALSE` | ✅ | |
| `CALL` | 🟡 | Basic Native Support Only |
| `RET` | ✅ | |
| **Data Structures** | | |
| `BUILD_LIST` | 🟡 | Sedang dikerjakan (Prioritas) |
| `BUILD_MAP` | 🟡 | Sedang dikerjakan (Prioritas) |
| **Objects** | | |
| `LOAD_ATTR` | 🟡 | Sedang dikerjakan (Prioritas) |
| `STORE_ATTR` | 🟡 | Sedang dikerjakan (Prioritas) |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Ekspansi Opcode:** Melengkapi dukungan Struktur Data (`List`, `Map`) dan Objek (`Attribute Access`). (Sedang Berjalan)
2.  **Full Call Support:** Mendukung pemanggilan fungsi Morph user-defined (bukan hanya native).
3.  **Bootstrap Penuh:** Menggunakan Native VM ini untuk menjalankan `morph.mvm` (Compiler Self-Hosted) itu sendiri.

---
*Diperbarui terakhir: Pengaktifan kembali Native VM dengan Refactoring Modular.*
