# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Eksperimental (Prototype)**
*   Interpreter Loop (`prosesor.fox`) berfungsi.
*   Stack Frame & Call Stack berfungsi.
*   Mendukung Aritmatika Dasar, Control Flow, dan Struktur Data (List/Dict).
*   Belum terintegrasi penuh dengan Compiler untuk menjalankan kode `.fox` sembarang (masih mengandalkan bytecode manual/tes).

## 1. Matriks Opcode

| Opcode | Status | Catatan |
| :--- | :---: | :--- |
| **Stack Ops** | | |
| `PUSH_CONST` | ✅ | |
| `POP` | ❌ | |
| `DUP` | ❌ | |
| **Arithmetic** | | |
| `ADD` (`+`) | ✅ | |
| `SUB` (`-`) | ✅ | |
| `MUL` (`*`) | ✅ | |
| `DIV` (`/`) | ✅ | |
| `MOD` (`%`) | ✅ | |
| **Logic/Comparison** | | |
| `EQ` (`==`) | ✅ | |
| `GT` (`>`) | ✅ | |
| `LT` (`<`) | ✅ | |
| `AND` | ❌ | |
| `OR` | ❌ | |
| `NOT` | ❌ | |
| **Variable Access** | | |
| `LOAD_LOCAL` | ✅ | |
| `STORE_LOCAL` | ✅ | |
| `LOAD_GLOBAL` | ❌ | Belum ada mekanisme global space yang solid |
| `STORE_GLOBAL` | ❌ | |
| `LOAD_ATTR` | ❌ | Properti objek |
| `LOAD_INDEX` | ✅ | Akses List/Dict (`obj[idx]`) |
| **Control Flow** | | |
| `JMP` | ✅ | Unconditional Jump |
| `JMP_IF_FALSE` | ✅ | Conditional Jump |
| `CALL` | ✅ | Panggilan fungsi & passing argumen |
| `RET` | ✅ | Return value & frame pop |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | |
| `BUILD_DICT` | ✅ | |
| `BUILD_FUNCTION` | ❌ | Untuk closure/lambda runtime |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Integrasi Loader:** Menghubungkan `pemuat.fox` agar bisa membaca file `.mvm` hasil kompilasi `greenfield/morph.fox`. (Selesai ✅)
2.  **Struktur Data:** Implementasi `BUILD_LIST` dan `BUILD_DICT` agar VM bisa memproses data kompleks. (Selesai ✅)
3.  **Global & Builtins:** Mekanisme untuk memanggil fungsi builtin (`panjang`, `tambah`, dll) dari dalam Native VM.
4.  **Objek & Kelas:** Implementasi `BUILD_CLASS`, `LOAD_ATTR` untuk mendukung OOP dasar.

---
*Diperbarui terakhir: Implementasi List & Dictionary.*
