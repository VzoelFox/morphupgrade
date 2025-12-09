# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**

> **UPDATE:** Isu "Heisenbug" pada serialisasi bytecode dan akses globals telah diperbaiki. Native VM kini memiliki fondasi yang jauh lebih stabil untuk menjalankan kode kompleks seperti Lexer.

### Kapabilitas Aktual (Terverifikasi)
*   **Interpreter Loop (`prosesor.fox`):** Berfungsi stabil. Akses variabel globals kini menggunakan logika robust (index fallback to `.ambil`) untuk mendukung Dictionary Native dan Host Object.
*   **Bytecode Serialization (`struktur.fox`):** ✅ **Pure Morph**. Dependensi `py.type` dihapus. Timestamp deterministik.
*   **Data Structures:** `Tumpukan` dan `Antrian` terverifikasi Pure Morph.
*   **Exception Handling:** Mendukung `PUSH_TRY`/`THROW`. Terverifikasi.
*   **OOP Native:** Instansiasi kelas dan pemanggilan metode berfungsi.
*   **Self-Hosting:** Compiler mampu mengkompilasi dirinya sendiri (CI Passing).

## 1. Matriks Opcode & Status Audit

| Opcode | Status | Audit Note |
| :--- | :---: | :--- |
| **Stack Ops** | ✅ | Stabil. |
| **Arithmetic** | ✅ | Terverifikasi Native. |
| **Variable Access** | ✅ | **FIXED:** `_ops_variabel` sekarang menangani Native Dict vs Host Object vs Proxy secara otomatis. |
| **Control Flow** | ✅ | Label backpatching bekerja. |
| **Data Structures** | ✅ | `Tumpukan` & `Antrian` (Native). |
| **Objects** | ✅ | Native Dictionary & Class Mock. |
| **Serialization** | ✅ | **FIXED:** Identitas tipe (`tipe_objek`) sekarang konsisten antara VM dan Serializer. |
| **LOAD_ATTR** | ✅ | **FIXED:** Dukungan metode primitif string (`kecil`, `besar`, dll) ditambahkan via mapping otomatis. |
| **Comparisons** | ✅ | **ADDED:** `NEQ`, `LT`, `LTE`, `GT`, `GTE` opcodes now implemented in Native VM. |

## 2. Status Pustaka Standar (`cotc`)

| Modul | Status | Temuan Audit |
| :--- | :--- | :--- |
| `json.fox` | ✅ **Native** | Pure Morph (Manual Parser). |
| `base64.fox` | ✅ **Native** | Pure Morph (Bitwise). |
| `teks.fox` | ✅ **Hybrid** | Pure Wrapper + Intrinsik. |
| `berkas.fox` | ✅ **Native** | **Wired:** Terhubung ke Opcode `IO_*` via `core.fox`. Terverifikasi baca/tulis disk. |
| `foxys.fox` | ✅ **Native** | **Wired:** Terhubung ke Opcode `SYS_*` via `core.fox`. Terverifikasi waktu/tidur. |
| `railwush` | 🟡 **Hybrid** | Menggunakan FFI (`datetime`, `os`) untuk fitur kriptografi/sistem. |
| `bytecode/struktur.fox`| ✅ **Native** | Refactored to remove FFI (`pinjam`). |
| `netbase/` | 📦 **Archived** | Dipindahkan ke `archived_morph/` untuk pembersihan. |

## 3. Rencana Perbaikan (Roadmap Jujur)

1.  **Prioritas Utama (Runtime):**
    *   **Lexer on Native VM:** Skrip `test_vm_lexer_wip.fox` sudah memiliki logika injeksi globals yang benar. Langkah selanjutnya adalah debugging runtime Lexer itu sendiri (indeks string, logika token).
    *   **System Calls:** Memperluas `foxys.fox` untuk mencakup lebih banyak syscall tanpa FFI langsung.

2.  **Stabilisasi:**
    *   Memastikan `tipe_objek` konsisten di seluruh VM (Native & Standard).
    *   **Verification Tool:** `greenfield/verifikasi.fox` now supports "Fail Fast" exit codes.

---
*Diperbarui terakhir: Perbaikan Wiring I/O & Audit Ulang.*
