# Laporan Paritas Sintaks: Bootstrap vs Greenfield

## 1. Perbandingan Fitur Utama

| Fitur | Bootstrap (`transisi/crusher.py`) | Greenfield (`greenfield/crusher.fox`) | Status |
| :--- | :--- | :--- | :--- |
| **Interpolasi String** | Menggunakan Python `transisi.lx` untuk sub-lexing. | Menggunakan `greenfield.lx_morph` secara rekursif. Dependensi `stdlib` dihapus (pakai slice native). | **SINKRON** (Dipatch). |
| **Keyword Whitelist** | Menggunakan `_token_identifier()` (list manual). | Menggunakan `_apakah_identifier()` (list manual). | **SINKRON** (Diperbarui untuk `TUNGGU`, `WARNAI`). |
| **Pangkat (`^`)** | Tidak didukung (token `^` dipapping ke `BIT_XOR`). | Sama. Token `PANGKAT` dihapus di kedua parser. | **SINKRON**. |
| **Slicing (`[:]`)** | Didukung di `_panggilan` (`TipeToken.TITIK_DUA`). | Didukung di `_panggilan` (`T.TITIK_DUA`). | **SINKRON**. |
| **Try-Catch (`coba-tangkap`)** | Mendukung `tangkap e jika kondisi`. | Mendukung `tangkap e jika kondisi`. | **SINKRON**. |
| **Operator Bitwise** | Hierarki presedensi lengkap (OR < XOR < AND). | Hierarki presedensi lengkap (sama). | **SINKRON**. |
| **Deklarasi Fungsi** | `_deklarasi_fungsi` menangani operator overload. | `_deklarasi_fungsi` juga menangani operator overload. | **SINKRON**. |
| **Import (`dari...ambil`)** | Mendukung `AMBIL_SEBAGIAN` dan `DARI...AMBIL`. | Mendukung `AMBIL_SEBAGIAN` dan `DARI...AMBIL`. | **SINKRON**. |

## 2. Temuan Diskrepan (Perbedaan Spesifik)

### A. Penanganan `_pernyataan_dari_ambil` (Import Baru)
- **Status Sebelumnya:** Greenfield memanggil fungsi ini tetapi **TIDAK** mendefinisikannya, yang merupakan bug kritis.
- **Tindakan (Patch Cleanup):** Telah menambahkan definisi `_pernyataan_ambil_semua`, `_pernyataan_ambil_sebagian`, `_pernyataan_dari_ambil`, dan `_pernyataan_pinjam` ke `greenfield/crusher.fox` agar paritas dengan `transisi/crusher.py`.

### B. List Identifier (`_apakah_identifier`)
Kedua parser memiliki daftar hardcoded keyword yang boleh dipakai sebagai identifier (misal: `TIPE`, `JENIS`).
- **Risiko:** Jika `Engineer` menambahkan keyword baru di stdlib (misal: `async` atau `await` sebagai identifier konteks), dan kita lupa update **salah satu** parser, kode akan jalan di dev (Bootstrap) tapi gagal di prod (Greenfield), atau sebaliknya.
- **Tindakan (Patch Cleanup):** Telah disinkronkan dengan menambahkan `TUNGGU` dan `WARNAI` ke kedua parser.

### C. Deklarasi Tipe (`tipe X = A | B`)
- **Bootstrap:** Menggunakan loop `while self._cocok(TipeToken.BIT_OR, TipeToken.GARIS_PEMISAH)`.
- **Greenfield:** Menggunakan loop `selama ini._cocok(T.BIT_OR, T.GARIS_PEMISAH)`.
- **Status:** **SINKRON**.

### D. Fitur `warnai`
- **Status Sebelumnya:** Greenfield tidak mendukung `warnai` di parser.
- **Tindakan (Patch Cleanup):** Menambahkan `_pernyataan_warnai` ke `greenfield/crusher.fox`.

## 3. Kesimpulan Paritas
Tindakan perbaikan telah dilakukan untuk menyinkronkan parser Greenfield dengan Bootstrap.
1.  **Interpolasi String:** Risiko dependensi sirkular telah dihilangkan dengan menggunakan slicing native (`text[start:end]`).
2.  **Missing Functions:** Fungsi import yang hilang telah ditambahkan.
3.  **Paritas Fitur:** Dukungan `warnai` telah ditambahkan.

**Status Saat Ini:** **99% SINKRON**.
Pembeda utama hanya pada detail implementasi (Python vs Morph), tetapi logika tata bahasanya identik.

---
*Diperbarui: 20/10/2024 (Patch Cleanup oleh Jules)*
