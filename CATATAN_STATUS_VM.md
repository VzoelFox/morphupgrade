# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**

> **PERINGATAN AUDIT (Jujur):** Meskipun banyak fitur "Native" telah diimplementasikan, ekosistem ini masih sangat bergantung pada *Host Primitives* (Python Builtins) yang dijembatani. Fitur seperti JSON bukan 100% "Pure Morph" karena menggunakan fungsi `float()` atau `int()` dari Python. Eksekusi Lexer Self-Hosted saat ini sedang mengalami **REGRESI** (Gagal berjalan).

### Kapabilitas Aktual
*   **Interpreter Loop (`prosesor.fox`):** Berfungsi dan stabil untuk logika dasar.
*   **Exception Handling:** Mendukung `PUSH_TRY`/`THROW`. Terverifikasi.
*   **OOP Native:** Instansiasi kelas dan pemanggilan metode berfungsi, NAMUN interop dengan objek Host (misal `CodeObject`) masih rapuh (Bug `.punya` missing).
*   **System I/O:** Menggunakan **Opcode Intrinsik** (`IO_*`, `SYS_*`) yang dipetakan langsung ke fungsi Python di `StandardVM`. Ini efisien, tapi bukan implementasi kernel OS.

## 1. Matriks Opcode & Status Audit

| Opcode | Status | Audit Note |
| :--- | :---: | :--- |
| **Stack Ops** | | |
| `PUSH_CONST` | ✅ | |
| `POP`, `DUP` | ✅ | |
| **Arithmetic** | | |
| `ADD` s/d `MOD` | ✅ | Terverifikasi Native. |
| `BIT_*` (Bitwise) | ✅ | Terverifikasi Native. |
| **Logic/Comparison** | | |
| `EQ`, `GT`, `LT` | ✅ | |
| **Variable Access** | | |
| `LOAD_LOCAL/STORE` | ✅ | Stabil. |
| `LOAD_VAR/STORE` | ✅ | Support `ProxyHostGlobals`. |
| **Control Flow** | | |
| `JMP`, `CALL`, `RET` | ✅ | Label backpatching di compiler bekerja. |
| **Exception Handling** | | |
| `PUSH_TRY`, `THROW` | ✅ | Stack unwinding berfungsi. |
| **Data Structures** | | |
| `BUILD_LIST/DICT` | ✅ | |
| `LOAD/STORE_INDEX` | ✅ | |
| **Objects** | | |
| `BUILD_CLASS` | ✅ | Native Dictionary Mock. |
| `LOAD_ATTR` | ⚠️ | **PARTIAL/FRAGILE**. Gagal saat akses atribut Host Object tertentu (Regression: `.punya` missing on CodeObject). |
| **String Optimization** | | |
| `STR_LOWER` dll | ✅ | Opcode Intrinsik (Wrapper Method Python). |
| **System & I/O** | | |
| `SYS_*` (Time, Sleep) | ✅ | Opcode Intrinsik (Wrapper Module Python). |
| `NET_*` (Socket) | ✅ | Opcode Intrinsik (Wrapper Socket Python). |
| `IO_*` (File) | ✅ | Opcode Intrinsik (Wrapper `open()` Python). **Catatan:** Fitur direktori (`mkdir`, `listdir`) belum lengkap. |

## 2. Status Pustaka Standar (`cotc`)

| Modul | Status Klaim | Temuan Audit |
| :--- | :--- | :--- |
| `json.fox` | **Hybrid** | Logika parsing adalah Morph murni, tapi menggunakan `float()` dan `int()` dari Host Python. |
| `base64.fox` | **Native Pure** | ✅ **PURE MORPH**. Logika bitwise murni, tanpa dependensi FFI ke `py.bytes`. Terverifikasi oleh `test_data_base64.fox`. |
| `teks.fox` | **Native Opcode** | Menggunakan Opcode `STR_*` (Intrinsik). Efisien, tapi bergantung VM Host. |
| `berkas.fox` | **Native Opcode** | Menggunakan Opcode `IO_*` (Intrinsik). |
| `foxys.fox` | **Native Opcode** | Menggunakan Opcode `SYS_*` dan `NET_*` (Intrinsik). |
| `netbase/` | **Fake Native** | ❌ **NON-COMPLIANT**. Masih menggunakan `pinjam "os"` dan `pinjam "json"`. Belum migrasi ke `foxys`. |

## 3. Rencana Perbaikan (Roadmap Jujur)

1.  **Prioritas Utama (Bugfix):**
    *   Memperbaiki regresi `LOAD_ATTR` pada Host Object (Isu `.punya` pada `ObjekKode`). Ini memblokir eksekusi Lexer.
    *   Implementasi `PolaDaftar` (List Pattern Matching) di Host Compiler (`ivm`) agar tes `test_pattern_matching` bisa lulus.
2.  **Pembersihan Hutang Teknis:**
    *   Rewrite `netbase` untuk menggunakan `foxys.fox` sepenuhnya.
3.  **Verifikasi Lanjutan:**
    *   Menjalankan Compiler Self-Hosted secara penuh (saat ini masih *WIP* karena isu VM di atas).

---
*Diperbarui terakhir: Implementasi Pure Morph untuk Base64.*
