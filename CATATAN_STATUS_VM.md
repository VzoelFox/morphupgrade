# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟢 **Aktif (Beta)**
*   Interpreter Loop (`prosesor.fox`) berfungsi dan stabil.
*   Limitasi Parser Bootstrap telah diatasi sepenuhnya.
*   Dukungan **Struktur Data Native** (Tumpukan, Antrian) dan **Akses Objek** telah terverifikasi.

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
| **Variable Access** | | |
| `LOAD_LOCAL` | ✅ | Stabil |
| `STORE_LOCAL` | ✅ | Stabil |
| `LOAD_VAR` | ✅ | Stabil |
| `STORE_VAR` | ✅ | Stabil |
| **Control Flow** | | |
| `JMP` | ✅ | |
| `JMP_IF_FALSE` | ✅ | |
| `CALL` | ✅ | Mendukung fungsi Native & Morph |
| `RET` | ✅ | |
| **Data Structures** | | |
| `BUILD_LIST` | ✅ | Terverifikasi (`test_struktur_lanjut.fox`) |
| `BUILD_MAP` | ✅ | Terverifikasi (`BUILD_DICT`) |
| **Objects** | | |
| `LOAD_ATTR` | ✅ | Terverifikasi Akses Properti & Metode |
| `STORE_ATTR` | ✅ | Terverifikasi |
| **System** | | |
| `PRINT` | ✅ | |

## 2. Rencana Pengembangan (Roadmap)

1.  **Ekspansi Opcode:** Melengkapi dukungan Struktur Data (`List`, `Map`) dan Objek (`Attribute Access`). (Selesai ✅)
2.  **Full Call Support:** Mendukung pemanggilan fungsi Morph user-defined. (Selesai ✅)
3.  **Bootstrap Penuh:** Menggunakan Native VM ini untuk menjalankan `morph.mvm` (Compiler Self-Hosted) itu sendiri. (Sedang Berjalan 🟡)

---
*Diperbarui terakhir: Stabilisasi Struktur Data & Aritmatika Native.*
