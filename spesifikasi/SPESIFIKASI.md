
---

🌿 Aturan Sintaks Morph (versi estetik & otomatis)

1. Struktur Dasar

Morph menggunakan gaya blok eksplisit:

fungsi <nama>(<argumen>...) -> <tipe_keluaran>
    <isi fungsi>
akhir_fungsi

Semua blok harus punya pasangan kata akhir (akhir_fungsi, akhir_jika, akhir_selama, dll).
Indentasi opsional tapi direkomendasikan untuk keindahan visual.


---

2. Deklarasi Variabel

biar <nama>: <tipe> = <nilai>
tetap <nama>: <tipe> = <nilai>

biar → bisa diubah.

tetap → tidak bisa diubah.

Penugasan ganda ke tetap = error sintaks.


Contoh:

biar umur: bil_bulat = 19
tetap nama: tulisan = "Morph"


---

3. Percabangan

jika <kondisi> maka
    <kode>
lainnya jika <kondisi> maka
    <kode>
lainnya
    <kode>
akhir_jika


---

4. Perulangan

selama <kondisi> lakukan
    <kode>
akhir_selama

Atau:

untuk setiap <item> dalam <daftar> lakukan
    <kode>
akhir_untuk


---

5. Fungsi

fungsi hitung(a: bil_bulat, b: bil_bulat) -> bil_bulat
    kembali a + b
akhir_fungsi


---

6. Komentar

# komentar satu baris
/* komentar
   banyak baris */

---

7. Pengelolaan Modul & Berkas

Untuk berinteraksi dengan berkas atau modul lain, Morph menggunakan kata kunci yang intuitif:

`ambil <nama_modul>`
`dari <nama_modul> ambil <fungsi_atau_variabel>`

`buka <nama_berkas> sebagai <alias>`
`tutup <alias>`

Contoh:

dari matematika ambil pi
biar lingkaran = 2 * pi * radius

berkas_data = buka "data.txt" sebagai data
// proses data...
tutup data


---

💡 Aturan Semantik Morph (otomatis dan prediktif)

Konsep	Aturan Semantik

Tipe Data	Morph punya tipe kuat dan statis (bil_bulat, bil_pecahan, tulisan, benar_salah, daftar<T>).
Pembagian /	Selalu menghasilkan bil_pecahan agar tidak ada kehilangan presisi.
Perbandingan	== membandingkan isi, bukan alamat memori.
Mutabilitas	tetap tidak dapat diubah setelah inisialisasi. Pelanggaran → error kompilasi.
Nilai Kosong	kosong hanya bisa dipakai pada tipe opsional (tulisan?, bil_bulat?).
Scoping	Setiap blok (fungsi, jika, selama, dll) punya ruang lingkup sendiri. Variabel di dalamnya tidak bocor keluar.
Fungsi	Jika fungsi punya panah ->, wajib kembali <nilai> sesuai tipe. Jika tidak, fungsi dianggap void.
Tipe inferensi	Compiler Morph bisa menebak tipe dari nilai awal: biar a = 5 → otomatis bil_bulat.



---

🌈 Contoh Lengkap

fungsi halo_dunia()
    tulis("Halo, Dunia Morph!")
akhir_fungsi

fungsi bagi(a: bil_bulat, b: bil_bulat) -> bil_pecahan
    jika b == 0 maka
        tulis("Error: pembagi nol.")
        kembali 0
    akhir_jika
    kembali a / b
akhir_fungsi

fungsi utama()
    tetap nama: tulisan = "Vzoel"
    biar hasil = bagi(10, 4)
    
    jika hasil > 2 maka
        tulis("Halo " + nama + ", hasilmu lebih dari dua!")
    lainnya
        tulis("Halo " + nama + ", hasilmu kecil.")
    akhir_jika
akhir_fungsi


---

✨ Ringkasan Filosofis Morph

Sintaks Morph: mengikuti struktur bahasa manusia, tanpa simbol berlebihan.

Semantik Morph: logika otomatis dan tegas, tidak ambigu.

Estetika: visual bersih, bisa dibaca seperti narasi.

Arsitektur Internal: Seluruh komponen internal—mulai dari token (PENGENAL, TEKS), node AST (NodeProgram, NodePengenal), hingga kelas inti (Leksikal, Pengurai, Penerjemah)—dirancang sepenuhnya dalam Bahasa Indonesia untuk mencapai koherensi visi yang menyeluruh.

Tujuan akhir: kode = puisi logika. Dapat dimengerti oleh mesin dan manusia awam.



---


ADS
