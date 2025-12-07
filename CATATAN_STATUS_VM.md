# Status Native FoxVM (Self-Hosted)

Dokumen ini melacak progres pengembangan VM Morph yang ditulis dalam Morph murni (`greenfield/fox_vm/`). VM ini merupakan implementasi dari komponen `sfox` (Simple Fox) dalam arsitektur FoxVM.

**Status:** 🟡 **Aktif (Beta - Runtime Debugging)**

> **PERINGATAN AUDIT (Jujur):** Meskipun banyak fitur "Native" telah diimplementasikan, ekosistem ini masih memiliki area yang perlu diperbaiki. Eksekusi Lexer Self-Hosted masih mengalami kendala runtime (IndexError pada op `LOAD_INDEX` string).

### Kapabilitas Aktual (Terverifikasi)
*   **Interpreter Loop (`prosesor.fox`):** Berfungsi stabil untuk logika dasar dan aritmatika.
*   **Exception Handling:** Mendukung `PUSH_TRY`/`THROW`. Terverifikasi.
*   **OOP Native:** Instansiasi kelas dan pemanggilan metode berfungsi.
*   **System I/O:** Menggunakan Opcode Intrinsik yang dipetakan ke Python (Stabil).
*   **Self-Hosting:** Alat verifikasi (`verifikasi.fox`) kini **BERFUNGSI** sepenuhnya untuk memeriksa sintaks dan dependensi.

## 1. Matriks Opcode & Status Audit

| Opcode | Status | Audit Note |
| :--- | :---: | :--- |
| **Stack Ops** | ✅ | Stabil. |
| **Arithmetic** | ✅ | Terverifikasi Native. |
| **Logic/Comparison** | ✅ | |
| **Variable Access** | ✅ | Stabil. |
| **Control Flow** | ✅ | Label backpatching di compiler bekerja. |
| **Data Structures** | ✅ | `Tumpukan` & `Antrian` (Native). |
| **Objects** | ✅ | Native Dictionary Mock. |
| **LOAD_ATTR** | ⚠️ | Fragile pada Host Object tertentu. Isu `.punya` pada dictionary global (Native) sedang diinvestigasi. |
| **System & I/O** | ✅ | Opcode Intrinsik (Valid). |

## 2. Status Pustaka Standar (`cotc`)

| Modul | Status | Temuan Audit |
| :--- | :--- | :--- |
| `json.fox` | ✅ **Native** | Pure Morph (Manual Parser). |
| `base64.fox` | ✅ **Native** | Pure Morph (Bitwise). |
| `teks.fox` | ✅ **Hybrid** | Pure Wrapper + Intrinsik. |
| `berkas.fox` | ✅ **Native** | Intrinsik I/O. |
| `netbase/` | ❌ **Wrapper** | Masih menggunakan FFI Python (Perlu Refactor). |

## 3. Rencana Perbaikan (Roadmap Jujur)

1.  **Prioritas Utama (Bugfix):**
    *   **Native VM Runtime:** Debugging `IndexError` pada eksekusi Lexer di Native VM.
    *   **Global Injection:** Memastikan `cpu.globals` Native VM terpopulasi dengan benar untuk modul yang diimpor (Isu `Variabel tidak ditemukan`).
2.  **Verifikasi & Tes:**
    *   Suite tes (`run_ivm_tests.py`) telah diperluas untuk mencakup `greenfield/examples`.
    *   `test_pattern_matching.fox` ditambahkan untuk memverifikasi `jodohkan`.

---
*Diperbarui terakhir: Audit Kejujuran Sistem & Perbaikan Tool Verifikasi.*
