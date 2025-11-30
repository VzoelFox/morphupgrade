# KNOWLEDGE SNAPSHOT
**Versi:** 1.0
**Tanggal:** 2024 (Sesi Terkini)
**Tujuan:** File ini berfungsi sebagai "memori eksternal" untuk instance Jules lainnya. File ini berisi ringkasan arsitektur, aturan, dan status terkini proyek Morph untuk memastikan kesinambungan konteks antar sesi pengembangan.

---

## 1. Filosofi Pengembangan (The Soul of Independent AGI)
*   **Efisien > Cepat:** "Efficient is Smart". Lebih baik pelan tapi teliti daripada cepat tapi banyak bug.
*   **Knowledge Memory:** Prioritaskan pemahaman mendalam (deep analysis) sebelum coding. Dokumentasikan temuan.
*   **Atomic Commits:** Satu commit untuk satu tugas logika. Jangan mencampur perbaikan bug dengan fitur baru (scope creep).
*   **Metode Testing:** 3 Tahap (Simple -> Intensive -> Integration).
*   **Fail Loud:** Kegagalan parsing atau kompilasi harus melempar exception, bukan hanya log error (Fail-Silent is bad).

## 2. Arsitektur Proyek
Proyek dibagi menjadi tiga direktori utama:
1.  **`transisi/` (Bootstrap/Legacy):** Frontend bahasa berbasis Python (Lexer, Parser, Interpreter lama). Hanya diubah jika memblokir Greenfield.
2.  **`ivm/` (New Python VM):** Virtual Machine baru berbasis Python (`StandardVM`). Menjalankan bytecode yang dihasilkan Greenfield.
3.  **`greenfield/` (Self-Hosted Toolchain):** Kompiler Morph yang ditulis dalam Morph murni. Ini adalah prioritas pengembangan utama.

---

## 3. Status Terkini: Greenfield Compiler (`greenfield/kompiler.fox`)
*Analisis dari Sesi Terakhir:*
*   **Kapabilitas:**
    *   [OK] Aritmatika dasar (Tambah, Kurang, Kali, Bagi).
    *   [OK] Deklarasi Variabel Global (`biar x = 10`).
    *   [OK] Pernyataan Output (`tulis(...)`).
    *   [OK] Logika dasar (`jika`, `selama` - *perlu verifikasi lebih lanjut tapi kode ada*).
*   **Keterbatasan (CRITICAL):**
    *   [FAIL] **Definisi Fungsi:** Belum didukung. Node `FungsiDeklarasi` ditolak atau diabaikan.
    *   [FAIL] **Definisi Kelas:** Belum didukung.
    *   [ISSUE] **Fail-Silent:** Kompiler saat ini hanya mencetak pesan `"[Kompiler] Node belum didukung"` ke stdout tanpa melempar exception/menghentikan proses. Ini berbahaya untuk testing otomatis.
*   **Integrasi:** Script entry point `greenfield/morph.fox` belum menggunakan `kompiler.fox` untuk eksekusi, masih sebatas parsing.

---

## 4. Aturan Bahasa Morph (Syntax & Semantics)
*   **Import:** Gunakan sintaks `dari "path/file.fox" ambil_sebagian A, B`. Jangan gunakan `from` (Inggris).
*   **Assignment:** Wajib menggunakan kata kunci `ubah` (misal: `ubah x = 10` atau `ubah data['k'] = v`).
*   **List:** Mutable. Method tambah elemen adalah `.append(item)`, BUKAN `.tambah()`.
*   **String:** Gunakan fungsi `teks(obj)` (dari `stdlib/core.fox`) untuk konversi eksplisit. String concatenation dengan Integer akan error tanpa ini.
*   **Reserved Keywords:** Jangan gunakan kata berikut sebagai nama variabel/parameter:
    *   `jenis` (gunakan `tipe_cmd` atau lainnya).
    *   `tipe` (gunakan `nama_tipe`).
    *   `akhir` (penutup blok).
*   **Struktur Blok:**
    *   `jika ... maka ... akhir` (Wajib multi-line untuk keamanan parser).
    *   `kelas ... maka ... akhir` (Body hanya boleh berisi metode `fungsi`/`asink`. Inisialisasi properti harus di dalam `inisiasi`).

---

## 5. Detail Teknis Komponen

### A. Greenfield Parser (`greenfield/crusher.fox`)
*   Menggunakan **Precedence Climbing** untuk ekspresi.
*   Mendukung **List/Dict Literals** (`[]`, `{}`).
*   Mendukung **Pattern Matching** (`jodohkan ... dengan ...`).
*   **Constraint:** Error recovery (`_sinkronisasi`) kadang menyembunyikan error parsing (false positive success).

### B. IVM (`ivm/`)
*   **StandardVM:** Hybrid stack/register.
*   **Opcode:** Didefinisikan sebagai Integer eksplisit di `ivm/core/opcodes.py`.
*   **Handling:** Exception handler bersifat frame-local.
*   **Fitur:** `PRINT_RAW` (tanpa newline), `Op.SLICE` (iris string/list).
*   **Running:** Jalankan via `python3 -m ivm.main path/to/script.fox`.

### C. Standard Library (`greenfield/cotc/`)
*   **Fokus:** Logika murni dan Matematika (`matematika/`, `logika/`).
*   **IO:** `io/berkas.fox` membungkus intrinsik Python (`_io_*`).
*   **Intrinsik:** `stdlib/core.fox` mengekspos fungsi built-in VM (`panjang`, `tambah`, `teks`).

---

## 6. Panduan Testing & Debugging
*   **Command:** Gunakan `python3 run_ivm_tests.py` untuk suite tes baru, atau `python3 -m pytest` untuk suite lengkap (butuh `aiohttp`).
*   **Legacy Tests:** Kode tes lama dipindahkan ke `tests/legacy_disabled/`.
*   **Debugging:** Bersihkan file `.pyc` jika terjadi anomali aneh (caching isu).
*   **Dependency:** `requirements.txt` berisi daftar paket Python yang dibutuhkan (misal `pytest`).
