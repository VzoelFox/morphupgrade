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
| `NodeAST`                  | Kelas dasar untuk semua node.                    |
| `NodeModul`                | Kelas dasar untuk node level-atas (root).        |
| `NodePernyataan`           | Kelas dasar untuk semua jenis *statement*.       |
| `NodeEkspresi`             | Kelas dasar untuk semua jenis *expression*.      |
| `NodeOperator`             | Kelas dasar untuk token operator.                |

### Kategori: Node Level Atas (Struktur Program)

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `NodeProgram`              | Mewakili seluruh program/file.                   |

### Kategori: Literal, Variabel & Struktur Data

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `NodeKonstanta`            | Nilai literal (angka, teks, boolean, nil).       |
| `NodeNama`                 | Identifier (nama variabel/fungsi).               |
| `NodeDaftar`               | Literal daftar (contoh: `[1, 2, 3]`).              |
| `NodeKamus`                | Literal kamus (contoh: `{"k": "v"}`).           |

### Kategori: Ekspresi

| Nama Kelas Saat Ini        | Deskripsi                                        |
| -------------------------- | ------------------------------------------------ |
| `NodeOperasiBiner`         | Operasi dengan dua operand (`kiri op kanan`).    |
| `NodeOperasiUnary`         | Operasi dengan satu operand (`op operand`).      |
| `NodePanggilFungsi`        | Pemanggilan fungsi (`fungsi(arg)`).              |
| `NodeAksesMember`          | Akses anggota (`objek["kunci"]` atau `daftar[0]`). |

### Kategori: Pernyataan (Statements) Inti MORPH

| Nama Kelas Saat Ini          | Deskripsi                                                      |
| ---------------------------- | -------------------------------------------------------------- |
| `NodeDeklarasiVariabel`      | `biar nama = nilai` atau `tetap nama = nilai`.                 |
| `NodeAssignment`             | `nama = nilai` (perlu diganti dengan sintaks `ubah`).          |
| `NodeJikaMaka`               | Struktur kontrol `jika-maka-lain`.                             |
| `NodeFungsiDeklarasi`        | Deklarasi fungsi `fungsi nama(...) maka ... akhir`.            |
| `NodePernyataanKembalikan`   | Pernyataan `kembalikan nilai`.                                 |
| `NodeAmbil`                  | Fungsi bawaan `ambil("prompt")`.                               |
| `NodeImpor`                  | Pernyataan `ambil` untuk modul (perlu disempurnakan).          |
| `NodePinjam`                 | FFI `pinjam "file.py"`.                                        |
| `NodeSelama`                 | Perulangan `selama kondisi maka ... akhir`.                    |
| `NodePilih`                  | Struktur `pilih-ketika-lainnya`.                               |
| `NodeKasusPilih`             | Cabang `ketika` dalam blok `pilih`.                            |
| `NodeKasusLainnya`           | Cabang `lainnya` dalam blok `pilih`.                           |

---

### 3. Node Pengaruh Python (Perlu Tinjauan Ulang)

Bagian ini berisi node-node yang diadopsi langsung dari AST Python. Node-node ini perlu dievaluasi: apakah kita akan membuat padanan murni MORPH, atau menghapusnya jika tidak sesuai dengan filosofi bahasa.

| Nama Kelas Saat Ini        | Deskripsi (Konsep Python)                          | Rekomendasi Awal                                        |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------- |
| `NodeKonteksEkspresi`      | Konteks `Load`, `Store`, `Del`.                    | Hapus/Sederhanakan. Konteks ini implisit di MORPH.      |
| `NodeMuat`, `NodeSimpan`     | Varian dari `NodeKonteksEkspresi`.                 | Hapus/Sederhanakan.                                     |
| `NodeAksesTitik`           | Akses properti `objek.properti`.                   | Pertimbangkan. Apakah MORPH akan memiliki objek?        |
| `NodePerulanganFor`        | `for item in koleksi`.                             | Pertahankan, tetapi mungkin dengan kata kunci berbeda.  |
| `NodeAugAssign`            | `+=`, `-=`, `*=`, `/=`.                              | Hapus. Bertentangan dengan prinsip "eksplisit".       |
| `NodeDelete`               | `del variabel`.                                    | Evaluasi. Apakah MORPH butuh penghapusan manual?        |
| `NodeWith`                 | `with resource as r:`.                             | Evaluasi. Konsep *context manager* mungkin terlalu rumit. |
| `NodeAssert`               | `assert kondisi`.                                  | Hapus. Mungkin bisa diganti fungsi pustaka standar.     |
| `NodeGlobal`, `NodeNonlocal` | Manajemen scope eksplisit.                       | Hapus. Scope MORPH harus sederhana dan intuitif.        |
| `NodeNamedExpr`            | Operator Walrus `:=`.                              | Hapus. Terlalu rumit dan tidak eksplisit.             |
| `NodeListComp`, `NodeSetComp`, `NodeDictComp`, `NodeGeneratorExp` | List/Set/Dict Comprehensions & Generator Expressions. | Hapus. Ganti dengan perulangan biasa agar lebih mudah dibaca pemula. |
