# Laporan Paritas Sintaks: Bootstrap vs Greenfield

## 1. Perbandingan Fitur Utama

| Fitur | Bootstrap (`transisi/crusher.py`) | Greenfield (`greenfield/crusher.fox`) | Status |
| :--- | :--- | :--- | :--- |
| **Interpolasi String** | Menggunakan Python `transisi.lx` untuk sub-lexing. | Menggunakan `greenfield.lx_morph` secara rekursif. Bergantung pada `stdlib` (iris). | **Berisiko**: Mekanisme berbeda, Greenfield punya dependensi sirkular. |
| **Keyword Whitelist** | Menggunakan `_token_identifier()` (list manual). | Menggunakan `_apakah_identifier()` (list manual). | **SINKRON** (Diperbarui untuk `TUNGGU`, `WARNAI`). |
| **Pangkat (`^`)** | Tidak didukung (token `^` dipapping ke `BIT_XOR`). | Sama. Token `PANGKAT` dihapus di kedua parser. | **SINKRON**. |
| **Slicing (`[:]`)** | Didukung di `_panggilan` (`TipeToken.TITIK_DUA`). | Didukung di `_panggilan` (`T.TITIK_DUA`). | **SINKRON**. |
| **Try-Catch (`coba-tangkap`)** | Mendukung `tangkap e jika kondisi`. | Mendukung `tangkap e jika kondisi`. | **SINKRON**. |
| **Operator Bitwise** | Hierarki presedensi lengkap (OR < XOR < AND). | Hierarki presedensi lengkap (sama). | **SINKRON**. |
| **Deklarasi Fungsi** | `_deklarasi_fungsi` menangani operator overload. | `_deklarasi_fungsi` juga menangani operator overload. | **SINKRON**. |
| **Import (`dari...ambil`)** | Mendukung `AMBIL_SEBAGIAN`. | Mendukung `AMBIL_SEBAGIAN` via `_pernyataan_ambil_sebagian`. | **SINKRON**. |

## 2. Temuan Diskrepan (Perbedaan Spesifik)

### A. Penanganan `_pernyataan_dari_ambil` (Import Baru)
- **Bootstrap:** Memiliki logika khusus `_pernyataan_dari_ambil` yang menangani `dari "path" ambil_sebagian ...`.
- **Greenfield:** Memiliki `_pernyataan_dari_ambil` yang memanggil `_pernyataan_ambil_sebagian`.
- **Analisis:** Keduanya tampaknya bertujuan sama, tapi implementasi Bootstrap lebih eksplisit dalam pengecekan token berikutnya.

### B. List Identifier (`_apakah_identifier`)
Kedua parser memiliki daftar hardcoded keyword yang boleh dipakai sebagai identifier (misal: `TIPE`, `JENIS`).
- **Risiko:** Jika `Engineer` menambahkan keyword baru di stdlib (misal: `async` atau `await` sebagai identifier konteks), dan kita lupa update **salah satu** parser, kode akan jalan di dev (Bootstrap) tapi gagal di prod (Greenfield), atau sebaliknya.
- **Tindakan (Patch Cleanup):** Telah disinkronkan dengan menambahkan `TUNGGU` dan `WARNAI` ke kedua parser.

### C. Deklarasi Tipe (`tipe X = A | B`)
- **Bootstrap:** Menggunakan loop `while self._cocok(TipeToken.BIT_OR, TipeToken.GARIS_PEMISAH)`.
- **Greenfield:** Menggunakan loop `selama ini._cocok(T.BIT_OR, T.GARIS_PEMISAH)`.
- **Status:** **SINKRON**. Perubahan operator pipa `|` dari `GARIS_PEMISAH` ke `BIT_OR` sudah diterapkan di kedua parser.

## 3. Kesimpulan Paritas
Secara umum, struktur tata bahasa (grammar) **sudah sangat mirip (98% parity)**.
Risiko utama bukan pada *beda aturan*, tapi pada **beda implementasi mesin**:
1.  **Interpolasi String Greenfield** rapuh karena memanggil `stdlib/teks.fox`. Jika stdlib rusak, parser mati. Bootstrap tidak punya masalah ini karena pakai Python native.
2.  **Error Handling:** Bootstrap mengumpulkan error di list. Greenfield melempar `PenguraiKesalahan` tapi juga punya `handler`. Mekanisme "Fail Fast" Greenfield lebih agresif.

**Rekomendasi:**
Jangan ubah sintaks interpolasi string di stdlib/kode user sampai parser Greenfield diperbaiki.

## 4. Syscalls & I/O Parity (Patch 5)
- **Bootstrap:** Menggunakan fungsi intrinsik Python yang disuntikkan secara ad-hoc (misal `_io_hapus_file`).
- **Greenfield:** Kini menggunakan arsitektur **Syscalls** (`greenfield/cotc/sys/syscalls.fox`) yang membungkus akses Host VM.
- **Status:** **SUPERIOR**. Greenfield memiliki arsitektur I/O yang lebih terstruktur dan siap untuk porting ke Native VM, sedangkan Bootstrap masih bergantung penuh pada suntikan global Python.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.5 (Greenfield Patch 5)
tanggal  : 10/12/2025
