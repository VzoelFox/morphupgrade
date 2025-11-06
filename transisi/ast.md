# Inventaris Abstract Syntax Tree (AST) dan Konsep Inti MORPH

Dokumen ini berfungsi sebagai "cetak biru" dan inventaris untuk semua node AST dan konsep inti yang ada dalam ekosistem MORPH. Tujuannya adalah untuk mendokumentasikan keadaan saat ini dan menjadi dasar bagi Anda, Vzoel Fox's, untuk memberikan nama-nama baru yang puitis dan definitif untuk implementasi `absolut_sntx.py` di masa depan.

---

## 1. Konsep Inti Murni MORPH (Berdasarkan `fox_engine`)

Bagian ini berisi konsep-konsep tingkat tinggi dan primitif konkurensi yang sudah memiliki nama murni dalam bahasa MORPH. Ini adalah fondasi filosofi bahasa.

| Nama Konsep MORPH          | Padanan Konsep Python                     | Lokasi File                                      |
| -------------------------- | ----------------------------------------- | ------------------------------------------------ |
| **`JalurUtamaMultiArah`**  | `concurrent.futures.ThreadPoolExecutor`   | `fox_engine/internal/jalur_utama_multi_arah.py`  |
| **`JalurEvakuasi`**        | `threading.Thread`                        | `fox_engine/internal/jalur_evakuasi.py`          |
| **`Kunci`**                | `threading.RLock`                         | `fox_engine/internal/kunci.py`                   |
| **`GarisTugas`**           | `asyncio.Semaphore`                       | `fox_engine/internal/garis_tugas.py`             |
| **`HasilMasaDepan`**       | `concurrent.futures.Future`               | `fox_engine/internal/hasil_masa_depan.py`        |
| **`TugasFox`**             | _(Struktur Data Tugas)_                   | `fox_engine/core.py`                             |
| **`MetrikFox`**            | _(Struktur Data Metrik)_                  | `fox_engine/core.py`                             |
| **`StatusTugas`**          | `Enum` (untuk status tugas)               | `fox_engine/core.py`                             |
| **`FoxMode`**              | `Enum` (untuk mode eksekusi)              | `fox_engine/core.py`                             |
| **`IOType`**               | `Enum` (untuk jenis I/O)                  | `fox_engine/core.py`                             |
| **`AliansiNilaiTetap`**    | `Enum`                                    | `fox_engine/internal/aliansi_nilai_tetap.py`     |
| **`kelasdata`**            | `dataclasses.dataclass`                   | `fox_engine/internal/kelas_data.py`              |

---

## 2. Inventaris Node AST (Berdasarkan `morph_engine/node_ast.py`)

Bagian ini mengkategorikan semua node AST yang saat ini ada di `node_ast.py`. Banyak di antaranya terinspirasi oleh AST Python dan perlu ditinjau kembali.

### Kategori: Node Dasar (Kelas Induk)

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `MRPH`                  | Kelas dasar untuk semua node.                    |
| `Core`                | Kelas dasar untuk node level-atas (root).        |
| `st`           | Kelas dasar untuk semua jenis *statement*.       |
| `XPrs`             | Kelas dasar untuk semua jenis *expression*.      |
| `Operator`             | Kelas dasar untuk token operator.                |

### Kategori: Node Level Atas (Struktur Program)

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `Bagian`              | Mewakili seluruh program/file.                   |

### Kategori: Literal, Variabel & Struktur Data

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `Konstanta`            | Nilai literal (angka, teks, boolean, nil).       |
| `Identitas`                 | Identifier (nama variabel/fungsi).               |
| `Daftar`               | Literal daftar (contoh: `[1, 2, 3]`).              |
| `Kamus`                | Literal kamus (contoh: `{"k": "v"}`).           |

### Kategori: Ekspresi

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `FoxBinary`         | Operasi dengan dua operand (`kiri op kanan`).    |
| `FoxUnary`         | Operasi dengan satu operand (`op operand`).      |
| `PanggilFungsi`        | Pemanggilan fungsi (`fungsi(arg)`).              |
| `Akses`          | Akses anggota (`objek["kunci"]` atau `daftar[0]`). |

### Kategori: Pernyataan (Statements) Inti MORPH

| Nama Kelas Saat Ini          | Deskripsi                                                      |
| ---------------------------- | -------------------------------------------------------------- |
| `DeklarasiVariabel`      | `biar nama = nilai` atau `tetap nama = nilai`.                 |
| `Assignment`             | `nama = nilai` (perlu diganti dengan sintaks `ubah`).          |
| `Jika_Maka`               | Struktur kontrol `jika-maka-lain`.                             |
| `FungsiDeklarasi`        | Deklarasi fungsi `fungsi nama(...) maka ... akhir`.            |
| `PernyataanKembalikan`   | Pernyataan `kembalikan nilai`.                                 |
| `ambil`                  | Fungsi bawaan `ambil("prompt")`.                               |
| `Ambil`                  | Pernyataan `ambil` untuk modul (perlu disempurnakan).          |
| `Pinjam`                 | FFI `pinjam "file.py"`.                                        |
| `Selama`                 | Perulangan `selama kondisi maka ... akhir`.                    |
| `Pilih`                  | Struktur `pilih-ketika-lainnya`.                               |
| `PilihKasus`             | Cabang `ketika` dalam blok `pilih`.                            |
| `KasusLainnya`           | Cabang `lainnya` dalam blok `pilih`.                           |

---

### 3. Node Pengaruh Python (Perlu Tinjauan Ulang)

Bagian ini berisi node-node yang diadopsi langsung dari AST Python. Node-node ini perlu dievaluasi: apakah kita akan membuat padanan murni MORPH, atau menghapusnya jika tidak sesuai dengan filosofi bahasa.

| Nama Kelas Saat Ini        | Deskripsi (Konsep Python)                          | Rekomendasi Awal                                        |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------- |
| `KonteksEkspresi`      | Konteks `Load`, `Store`, `Del`.                    | Hapus/Sederhanakan. Konteks ini implisit di MORPH.      |
| `Muat`, `Simpan`     | Varian dari `KonteksEkspresi`.                 | Hapus/Sederhanakan.                                     |
| `AksesTitik`           | Akses properti `objek.properti`.                   | Pertimbangkan. Apakah MORPH akan memiliki objek?        |
| `PerulanganFor`        | `for item in koleksi`.                             | Pertahankan, tetapi mungkin dengan kata kunci berbeda.  |
| `AugAssign`            | `+=`, `-=`, `*=`, `/=`.                              | Hapus. Bertentangan dengan prinsip "eksplisit".       |
| `HapusVariabel`               | `del variabel`.                                    | Evaluasi. Apakah MORPH butuh penghapusan manual?        |
| `With`                 | `with resource as r:`.                             | Evaluasi. Konsep *context manager* mungkin terlalu rumit. |
| `Assert`               | `assert kondisi`.                                  | Hapus. Mungkin bisa diganti fungsi pustaka standar.     |
| `Global`, `Nonlocal` | Manajemen scope eksplisit.                       | Hapus. Scope MORPH harus sederhana dan intuitif.        |
| `NamaExpr`            | Operator Walrus `:=`.                              | Hapus. Terlalu rumit dan tidak eksplisit.             |
| `ListComp`, `NodeSetComp`, `DictComp`, `GeneratorExp` | List/Set/Dict Comprehensions & Generator Expressions. | Hapus. Ganti dengan perulangan biasa agar lebih mudah dibaca pemula. |
