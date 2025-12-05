# Visi Morph Alami: Pemrograman Percakapan (*Conversational Programming*)

Dokumen ini merangkum visi jangka panjang untuk evolusi sintaks Morph menuju **Bahasa Alami** (*Natural Language*). Tujuannya adalah memungkinkan pemrogram (atau AGI) untuk menulis logika dalam bentuk narasi dan dialog, bukan sekadar instruksi kaku.

## Filosofi Dasar

Morph Alami mengubah paradigma dari "Memerintah Mesin" menjadi "Berdiskusi dengan Mesin". Kode program berbentuk kalimat tanya-jawab yang mendefinisikan hubungan, menguji hipotesis, dan menarik kesimpulan.

## 1. Pola Sintaksis (*Syntax Patterns*)

Sintaks ini dibangun di atas tiga elemen dasar interaksi:

### A. Pola Penyebut (*Subject Pattern*)
Entitas utama yang menjadi topik pembicaraan atau fakta dasar yang sudah diketahui.
*   Contoh: `a`, `b` (dalam konteks `a = b`).

### B. Pola Pembanding (*Comparator Pattern*)
Entitas baru yang diuji hubungannya terhadap Pola Penyebut.
*   Contoh: `c` (dalam pertanyaan `apakah c sama dengan a?`).

### C. Pola Penegas (*Affirmation/Inference Pattern*)
Kesimpulan logis yang diambil berdasarkan hasil perbandingan, seringkali memberikan peran atau definisi baru pada entitas.
*   Kata Kunci: `berarti`, `adalah`, `maka`.
*   Contoh: `berarti c adalah pola pembanding`.

---

## 2. Logika Interogatif (*Interrogative Logic*)

Morph Alami memperluas logika boolean/ternary menjadi sistem penalaran berbasis pertanyaan:

### `apakah ... ?` (Logika Kepastian)
Digunakan untuk menanyakan fakta atau status kebenaran saat ini.
*   **Output:** `Benar`, `Salah`, atau `Tidak Tahu` (*Unknown*).
*   **Contoh:** `apakah c sama dengan a atau b?`

### `mungkinkah ... ?` (Logika Spekulasi)
Digunakan untuk mengeksplorasi potensi atau probabilitas di masa depan, tanpa menuntut kepastian saat ini.
*   **Output:** Probabilitas (0.0 - 1.0) atau Status Potensial (`Bisa Jadi`, `Mustahil`).
*   **Contoh:** `mungkinkah d muncul nanti?`

### `namun mengapa ... ?` (Logika Kausalitas)
Digunakan untuk meminta alasan atau jejak penalaran (*traceback*) di balik sebuah fakta atau kejadian. Sangat berguna untuk *debugging* otomatis dan *Explainable AI*.
*   **Output:** Rantai Penjelasan (*Reasoning Chain*) atau Pohon Bukti (*Proof Tree*).
*   **Contoh:** `namun mengapa c tidak sama dengan a?` (Mesin menjawab dengan riwayat perubahan nilai `c`).

---

## 3. Contoh Kanonik

Berikut adalah contoh kode visi yang menggabungkan semua konsep di atas:

```morph
# Definisi Fakta Awal
a = b

# Dialog Logika
apakah c sama dengan a atau b?      # Pertanyaan Kepastian
apakah ada d?                       # Pertanyaan Eksistensi

# Fakta Baru (Respon/Kondisi)
tidak ada d..
dan c tidak sama dengan a maupun b

# Kesimpulan (Inferensi)
berarti c adalah pola pembanding untuk menjadi pola penegas a atau b
```

Dalam contoh di atas:
1.  Kita menetapkan fakta `a = b`.
2.  Kita menguji `c` dan keberadaan `d`.
3.  Berdasarkan fakta bahwa `d` tidak ada dan `c` berbeda dari `a/b`, kita menyimpulkan definisi baru untuk `c`.

## Roadmap Implementasi
Fitur ini direncanakan sebagai lapisan abstraksi tinggi di atas Parser Morph (Greenfield) di masa depan, setelah VM Native dan fitur "Deep Logic" stabil.
