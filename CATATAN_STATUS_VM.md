# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**

> **PERINGATAN AUDIT:** Beberapa fitur sistem (IO/Net/Sys) saat ini masih dalam status *stub* atau *hybrid* (meminjam Python), meskipun Opcode native sudah tersedia di Host VM.

### Kapabilitas Aktual (Terverifikasi)
*   **Interpreter Loop (`prosesor.fox`):** Berfungsi stabil. Akses variabel globals kini menggunakan logika robust.
*   **Bytecode Serialization (`struktur.fox`):** ✅ **Pure Morph**. Dependensi `py.type` dihapus. Timestamp deterministik.
*   **Data Structures:** `Tumpukan` dan `Antrian` terverifikasi Pure Morph.
*   **Exception Handling:** Mendukung `PUSH_TRY`/`THROW`. Terverifikasi.
*   **OOP Native:** Instansiasi kelas dan pemanggilan metode berfungsi (Terverifikasi oleh `test_vm_features.fox`).
*   **Self-Hosting:** Compiler mampu mengkompilasi dirinya sendiri (CI Passing). Namun, `morph run` (binary execution) masih memiliki isu output silent.

## 1. Matriks Opcode & Status Audit

| Opcode | Status | Audit Note |
| :--- | :---: | :--- |
| **Stack Ops** | ✅ | Stabil. |
| **Arithmetic** | ✅ | Terverifikasi Native. |
| **Variable Access** | ✅ | **FIXED:** Menangani Native Dict vs Host Object vs Proxy. |
| **Control Flow** | ✅ | Label backpatching bekerja. |
| **Data Structures** | ✅ | `Tumpukan` & `Antrian` (Native). |
| **Objects** | ✅ | Native Dictionary & Class Mock. |
| **Serialization** | ✅ | Konsistensi `tipe_objek` terjaga. |
| **LOAD_ATTR** | ✅ | Dukungan metode primitif string (`kecil`, `besar`, dll) via mapping. |
| **Comparisons** | ✅ | `NEQ`, `LT`, `LTE`, `GT`, `GTE` opcodes native. |

## 2. Status Pustaka Standar (`cotc`)

| Modul | Status | Temuan Audit |
| :--- | :--- | :--- |
| `json.fox` | ✅ **Native** | Pure Morph (Manual Parser). |
| `base64.fox` | ✅ **Native** | Pure Morph (Bitwise). |
| `teks.fox` | ✅ **Hybrid** | Pure Wrapper + Intrinsik (Opcode STR_*). |
| `berkas.fox` | 🔴 **Stub** | Menggunakan fungsi kosong di `core.fox`. Belum terhubung ke Opcode `IO_*`. |
| `foxys.fox` | 🔴 **Stub** | Menggunakan fungsi kosong di `core.fox`. Belum terhubung ke Opcode `SYS_*`. |
| `railwush` | 🟡 **Hybrid** | Fungsional, tapi menggunakan FFI (`datetime`, `os`, `platform`). Bukan Pure Morph. |
| `bytecode/struktur.fox`| ✅ **Native** | Refactored to remove FFI (`pinjam`). |
| `netbase/` | 📦 **Archived** | Dipindahkan ke `archived_morph/` untuk pembersihan. |

## 3. Rencana Perbaikan (Roadmap Jujur)

1.  **Prioritas Utama (Wiring):**
    *   Menghubungkan `greenfield/cotc/stdlib/core.fox` ke Opcode Native yang sebenarnya (`IO_*`, `SYS_*`) agar `berkas.fox` dan `foxys.fox` berfungsi. Saat ini mereka hanya memanggil fungsi kosong.

2.  **Stabilisasi:**
    *   Memperbaiki `morph run` agar output stdout tertangkap dan ditampilkan.
    *   Melanjutkan debugging Lexer di atas Native VM.

---
*Diperbarui terakhir: Audit Kejujuran oleh Jules.*
