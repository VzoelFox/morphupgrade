# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Eksperimental (Prototype)**
*   Interpreter Loop (`prosesor.fox`) berfungsi secara struktural.
*   **Peringatan:** Logika eksekusi dinonaktifkan sebagian karena keterbatasan Parser Bootstrap (Lihat `CATATAN_TEMUAN.md`).
*   Integrasi Builtin (`panjang`, `tulis`) sudah disiapkan di level struktur.

## 1. Matriks Opcode

| Opcode | Status | Catatan |
| :--- | :---: | :--- |
| **Stack Ops** | | |
| `PUSH_CONST` | ✅ | |
| `POP` | ❌ | |
| `DUP` | ❌ | |
| **Arithmetic** | | |
| `ADD` (`+`) | ✅ | (Dinonaktifkan sementara) |
| `SUB` (`-`) | ✅ | (Dinonaktifkan sementara) |
| `MUL` (`*`) | ✅ | (Dinonaktifkan sementara) |
| `DIV` (`/`) | ✅ | (Dinonaktifkan sementara) |
| `MOD` (`%`) | ✅ | (Dinonaktifkan sementara) |
| **Logic/Comparison** | | |
| `EQ` (`==`) | ✅ | (Dinonaktifkan sementara) |
| `GT` (`>`) | ✅ | (Dinonaktifkan sementara) |
| `LT` (`<`) | ✅ | (Dinonaktifkan sementara) |
| **Variable Access** | | |
| `LOAD_LOCAL` | ✅ | (Dinonaktifkan sementara) |
| `STORE_LOCAL` | ✅ | (Dinonaktifkan sementara) |
| `LOAD_GLOBAL` | 🟡 | Struktur ada, logika non-aktif |
| `STORE_GLOBAL` | 🟡 | Struktur ada, logika non-aktif |
| **Control Flow** | | |
| `JMP` | ✅ | (Dinonaktifkan sementara) |
| `JMP_IF_FALSE` | ✅ | (Dinonaktifkan sementara) |
| `CALL` | 🟡 | Native Call support ditambahkan (Disabled) |
| `RET` | ✅ | (Dinonaktifkan sementara) |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | (Dinonaktifkan sementara) |
| `BUILD_DICT` | ✅ | (Dinonaktifkan sementara) |
| **System** | | |
| `PRINT` | ✅ | (Dinonaktifkan sementara) |

## 2. Rencana Pengembangan (Roadmap)

1.  **Integrasi Loader:** Menghubungkan `pemuat.fox` agar bisa membaca file `.mvm` hasil kompilasi `greenfield/morph.fox`. (Selesai ✅)
2.  **Struktur Data:** Implementasi `BUILD_LIST` dan `BUILD_DICT` agar VM bisa memproses data kompleks. (Selesai ✅)
3.  **Global & Builtins:** Mekanisme untuk memanggil fungsi builtin (`panjang`, `tambah`, dll) dari dalam Native VM. (Struktur Selesai, Logika Blocked)
4.  **Migrasi Parser:** Mengganti Bootstrap Parser dengan Self-Hosted Parser agar bisa menjalankan logika VM yang kompleks tanpa error.

---
*Diperbarui terakhir: Implementasi Native Function Bridge (Blocked by Parser).*
