# Laporan Analisa Mendalam: Status Self-Hosting & Arsitektur Morph

**Penulis:** Jules (AI Assistant)
**Tanggal:** 25 Oktober 2023 (Simulasi)

---

## 1. Ringkasan Eksekutif

Berdasarkan analisa mendalam dan verifikasi langsung, klaim bahwa Morph telah mencapai **"Compiler Self-Hosting (Stabil)"** adalah **tidak akurat**. Meskipun kerangka kerja (skeleton) compiler telah ada dalam bahasa Morph (`greenfield/kompiler`), implementasi inti untuk menghasilkan bytecode (Code Generation) dari pernyataan dasar (seperti `tulis`, `jika`, deklarasi variabel) **belum diimplementasikan sama sekali**.

Saat ini, compiler `greenfield/morph.fox` hanya mampu melakukan parsing dan menghasilkan file binary `.mvm` kosong (atau hampir kosong), yang tidak melakukan apa-apa saat dijalankan.

---

## 2. Temuan Kritis: Kegagalan Self-Hosting

### 2.1. Kompilasi "Berhasil" Palsu
Percobaan mengkompilasi program sederhana `greenfield/examples/hello_world.fox`:
```morph
tulis("Hello Self-Hosted Morph!")
```
Menggunakan perintah:
```bash
python3 -m ivm.main greenfield/morph.fox build greenfield/examples/hello_world.fox
```
Menghasilkan output "SUKSES" dan file binary `.mvm`. Namun, file tersebut hanya berukuran 41 bytes dan ketika dijalankan tidak menampilkan output apapun.

Analisa bytecode menunjukkan:
```
Instructions: [(PUSH_CONST, None), (RET, None)]
```
Ini berarti program hasil kompilasi hanya melakukan `return nil` dan keluar.

### 2.2. Penyebab: Implementasi Kosong (Stubs)
Akar masalah ditemukan di file `greenfield/kompiler/pernyataan.fox`. Hampir seluruh fungsi visitor untuk statement (pernyataan) hanya berisi stub:

```morph
fungsi kunjungi_Tulis(ctx, node) maka
    kembali nil  <-- TIDAK ADA EMISI BYTECODE
akhir

fungsi kunjungi_DeklarasiVariabel(ctx, node) maka
    kembali nil
akhir
```

Modul `greenfield/kompiler/ekspresi.fox` tampaknya memiliki implementasi parsial untuk ekspresi aritmatika dan pemanggilan fungsi, namun tanpa dukungan *statement* (seperti assignment atau expression statement yang terhubung dengan benar), kode program praktis tidak bisa dihasilkan.

### 2.3. Kegagalan Test Suite (Runtime Panics)
Menjalankan `python3 run_ivm_tests.py` menghasilkan 7 kegagalan kritis. Salah satu error yang paling signifikan adalah:
```
RuntimeError: Global 'utama' not found.
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", ...}
```
Ini terjadi pada `greenfield/examples/test_loader.fox`. VM (Host) mengharapkan setiap program Morph memiliki fungsi entri point bernama `utama` (mirip `main` di C/Go), atau setidaknya kode level atas dieksekusi. Namun, karena compiler menghasilkan bytecode kosong (tanpa definisi fungsi `utama`), VM panik saat mencoba memanggilnya.

Selain itu, tes `test_vm_parser_wip.fox` gagal dengan ratusan pesan:
```
Error: Lokal tidak ditemukan: t3
```
Ini menunjukkan bahwa mekanisme *scope resolution* (variabel lokal vs global) di parser/compiler yang sedang dikembangkan masih rusak atau tidak sinkron dengan ekspektasi VM.

---

## 3. Analisa Arsitektur & Performa

### 3.1. Struktur Compiler (Greenfield)
Struktur compiler sebenarnya dirancang dengan cukup baik dan modular:
*   **Lexer (`lx_morph.fox`) & Parser (`crusher.fox`)**: Tampaknya fungsional (porting dari Python).
*   **AST (`absolute_syntax_morph.fox`)**: Definisi pohon sintaks lengkap.
*   **Visitor Pattern**: Penggunaan pola visitor untuk traversing AST (`utama.fox` mendispatch ke `pernyataan.fox` dan `ekspresi.fox`) adalah pendekatan standar yang solid.

**Masalah:** Implementasi visitor berhenti di *declaration*. Logika emisi opcode (`Gen.emit`) sudah ada di `generator.fox`, tetapi tidak dipanggil oleh visitor pernyataan.

### 3.2. Performa (Statik)
*   **Recursive Descent Parser**: Parser ditulis manual (bukan generator). Ini bagus untuk kontrol error, tapi di Morph (bahasa dinamis lambat) ini akan sangat lambat saat *bootstrap* (compiler mengkompilasi dirinya sendiri).
*   **String Manipulation**: Compiler banyak melakukan manipulasi string. Tanpa optimasi string interning di level VM Native, kinerja compiler akan berat.
*   **Dependensi `ivm`**: Saat ini, `greenfield/morph.fox` berjalan di atas `ivm` (Python). Ini menambah layer interpretasi (Morph di atas Python), membuat proses build sangat lambat.

---

## 4. Saran Perbaikan Teknis

Untuk memperbaiki situasi ini, disarankan melakukan langkah-langkah berikut secara bertahap:

### Langkah 1: Implementasi Dasar `pernyataan.fox`
Prioritaskan implementasi `PernyataanEkspresi` agar pemanggilan fungsi (seperti `tulis(...)`) bisa dieksekusi.

**Saran Kode (`greenfield/kompiler/pernyataan.fox`):**
```morph
fungsi kunjungi_PernyataanEkspresi(ctx, node) maka
    # Kunjungi ekspresi (misal: panggil fungsi)
    ctx._kunjungi(node.ekspresi)
    # Buang hasil (POP) karena ini statement, bukan assignment
    Gen.emit(ctx, ctx.Op["POP"], nil)
akhir

fungsi kunjungi_Tulis(ctx, node) maka
    # Evaluasi argumen yang akan ditulis
    ctx._kunjungi(node.argumen)
    # Emit Opcode PRINT (atau panggil fungsi native tulis)
    # Catatan: Morph pakai 'tulis' sebagai fungsi stdlib, bukan opcode khusus biasanya.
    # Jika 'tulis' adalah fungsi global:
    Gen.emit(ctx, ctx.Op["LOAD_GLOBAL"], "tulis")
    ctx._kunjungi(node.argumen)
    Gen.emit(ctx, ctx.Op["CALL"], 1)
    Gen.emit(ctx, ctx.Op["POP"], nil)
akhir
```

### Langkah 2: Perbaiki Handling 'Utama'
Compiler harus secara otomatis membungkus kode level atas ke dalam fungsi implisit, atau VM harus lebih toleran.
*   **Opsi A (Compiler):** Jika mendeteksi kode di luar fungsi/kelas, generate instruksi langsung di level modul.
*   **Opsi B (VM):** Jangan paksa panggil `utama` jika tidak ditemukan di global, cukup jalankan instruksi level modul (yang saat ini sudah dilakukan, tapi compiler menghasilkan `RET` terlalu dini).

### Langkah 3: Jujur dalam Dokumentasi
Ubah status di README dari "Stabil" menjadi "Experimental / W.I.P" (Work In Progress). Hapus klaim bahwa "Compiler Self-Hosting sudah ditulis sepenuhnya dan mampu mengkompilasi dirinya sendiri" karena ini menyesatkan kontributor baru.

### Langkah 4: Testing Otomatis yang Lebih Ketat
Buat tes yang memverifikasi *isi bytecode* output compiler.
Contoh tes (pseudo-code):
```python
def test_compile_hello():
    code = compile("tulis('hi')")
    assert len(code.instructions) > 2  # Jangan cuma RET
    assert code.constants[0] == "hi"
```

---
*Laporan ini dibuat secara otomatis oleh Jules sebagai bagian dari audit mendalam sistem Morph.*
