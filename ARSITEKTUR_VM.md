# Arsitektur Fox VM: Visi dan Peta Jalan

Dokumen ini menguraikan visi arsitektur untuk ekosistem Fox VM, sebuah runtime environment cerdas untuk bahasa Morph.

## 1. Filosofi Inti: Pemisahan Fundamental

Arsitektur Fox VM didasarkan pada filosofi pemisahan fundamental antara alur eksekusi yang sukses dan alur yang kompleks atau gagal. Tujuannya adalah untuk mencapai efisiensi sumber daya dan ketahanan sistem yang superior.

-   **Proses Utama (RAM/CPU Cepat):** Didedikasikan untuk **"Jalur Bahagia" (`mapping sukses`)**. Ini adalah eksekusi linier dari tugas-tugas yang berhasil tanpa halangan.
-   **Proses Sekunder (Storage/Virtual Sandbox):** Didedikasikan untuk **"Jalur Kompleks" (`looping gagal`, `retry`)**. Semua proses yang berulang, gagal, atau membutuhkan manajemen state yang rumit akan di-*offload* dari sumber daya utama.

Kegagalan dalam model ini bukanlah akhir dari eksekusi, melainkan jenis tugas lain yang dikelola secara terpisah, memastikan alur utama tetap cepat dan responsif.

## 2. Hierarki Eksekusi Fox VM (Jangka Pendek)

Fox VM bertindak sebagai orkestrator cerdas yang memilih mode eksekusi terbaik untuk sebuah program Morph. `ManajerFox` adalah implementasi inti dari orkestrator ini.

### 2.1. `sfox`/`mfox` (Simple/Mini Fox) - Interpreter VM

-   **Peran:** Mode eksekusi dasar, paling portabel, dan menjadi fondasi untuk validasi kebenaran.
-   **Proses:** Mengeksekusi bytecode atau AST secara langsung tanpa kompilasi lanjutan.
-   **Kasus Penggunaan:** Pengembangan, debugging, tugas-tugas sederhana, dan operasi I/O langsung.

### 2.2. `tfox` (Thunder Fox) - JIT VM

-   **Peran:** Mode eksekusi adaptif untuk meningkatkan performa kode yang sering berjalan.
-   **Proses:** VM akan memulai dalam mode interpretasi. "Proses ThunderFox" akan memonitor eksekusi dan mengidentifikasi "hot spots" (misalnya, loop yang sering dieksekusi). Bagian kode ini kemudian akan di-compile secara *Just-In-Time* (JIT) ke format yang lebih cepat.
-   **Kasus Penggunaan:** Aplikasi yang berjalan lama (seperti server) di mana performa dapat ditingkatkan secara dinamis seiring waktu.

### 2.3. `wfox` (Water Fox) - AOT VM

-   **Peran:** Mode eksekusi dengan performa tertinggi, dioptimalkan untuk *deployment*.
-   **Proses:** "Proses WaterFox" akan meng-compile seluruh program Morph *Ahead-Of-Time* (AOT) ke format yang paling efisien, seperti bytecode yang sangat dioptimalkan atau bahkan kode mesin asli.
-   **Kasus Penggunaan:** Rilis produksi di mana waktu startup dan performa mentah adalah prioritas.

### 2.4. Kontrol Kualitas

-   **Peran:** Fondasi yang memastikan konsistensi di semua mode eksekusi.
-   **Proses:** Sebuah kerangka kerja pengujian yang terpadu yang memverifikasi bahwa sebuah program Morph menghasilkan output yang **identik** tidak peduli apakah ia dijalankan oleh Interpreter, JIT, atau AOT. Ini adalah kunci untuk mencegah bug dan memastikan keandalan.

## 3. Visi Ekosistem VM Spesialis (Jangka Panjang)

Untuk mewujudkan filosofi "Pemisahan Fundamental", arsitektur jangka panjang akan mencakup ekosistem VM yang saling bekerja sama, diorkestrasi oleh `FoxIPC`.

### 3.1. `VM Snapshot/Rollback/Ingat` (VM Manajemen State)

-   **Peran:** Menjalankan alur kerja yang kompleks dan berpotensi gagal dengan cara yang tangguh dan dapat dipulihkan.
-   **Konsep:**
    -   **`bekukan hasil`**: Membuat "checkpoint" atau "commit" dari sebuah langkah komputasi yang berhasil.
    -   **`ingat hasil`**: Menyimpan state yang berhasil ini ke media persisten.
    -   **`.z File`**: Jika sebuah langkah gagal, state-nya (termasuk loop yang gagal) akan di-serialisasi ke dalam sebuah file `.z`, yang berfungsi sebagai tiket "coba lagi nanti".
    -   **`undur ke proses 0 lalu jalankan no 2`**: Ini adalah alur kerja pipeline. Setelah langkah 1 berhasil dan disimpan, VM akan mengatur ulang state-nya ke kondisi awal yang bersih sebelum memuat state yang diperlukan untuk menjalankan langkah 2. Ini menjamin isolasi antar langkah.
-   **Tujuan:** Memisahkan manajemen state yang rumit dari eksekusi logika bisnis.

### 3.2. `VM Hot Path` (VM Deployment)

-   **Peran:** Meng-compile kode Morph yang sudah terverifikasi ke target backend berperforma tinggi.
-   **Target:** WebAssembly (WASM) untuk eksekusi di browser dan lingkungan serverless, dan JavaScript (JS) untuk kompatibilitas yang lebih luas.
-   **Tujuan:** Memungkinkan Morph berjalan secara native di berbagai platform dengan performa maksimal.

### 3.3. `FoxIPC` (Orkestrator Antar-Proses)

-   **Peran:** Bertindak sebagai "sistem saraf" yang menghubungkan semua VM spesialis.
-   **Proses:**
    -   Mengelola antrian tugas.
    -   Mendelegasikan tugas "Jalur Bahagia" ke VM utama.
    -   Mengambil file `.z` yang dihasilkan oleh `VM Snapshot` dan menjadwalkannya untuk dieksekusi ulang oleh `VM Backup` atau dalam mode *retry*.
    -   Mengelola komunikasi antara VM yang berjalan di lingkungan yang berbeda (misalnya, antara backend dan frontend WASM).
-   **Tujuan:** Menciptakan sistem terdistribusi yang tangguh di mana kegagalan adalah kejadian yang diharapkan dan dikelola, bukan pengecualian.
