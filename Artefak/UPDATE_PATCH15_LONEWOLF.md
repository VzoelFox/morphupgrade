# Update Patch 15: The LoneWolf Update & Network Ascension

**Tanggal:** 12 Desember 2025
**Engineer:** Jules AI
**Founder:** Vzoel Fox's (Lutpan)

Patch ini menandai transisi signifikan menuju **FoxVM Ascension**. Kami telah membangun "Driver" (Networking & System Wrappers) dan "Kernel" (Sistem Penanganan Kegagalan LoneWolf) di atas fondasi Hybrid VM.

## 1. LoneWolf: Sistem Kekebalan Tubuh FoxVM

LoneWolf (`greenfield/cotc/lonewolf/`) adalah kerangka kerja otomatisasi penanganan kegagalan yang memungkinkan proses Morph untuk bertahan hidup dari crash dan pulih secara mandiri.

*   **Catch:** `Serigala` menangkap unhandled panic dan exception dari proses yang dilindungi.
*   **Dump:** `vmdumpbox` menyimpan state kegagalan (traceback, error message, memori RSS) ke dalam file `.z` (JSON).
*   **Diagnose:** `Bangkai` menganalisa file dump untuk menentukan apakah kegagalan bersifat **FATAL** (Logika/Sintaks) atau **RETRY** (I/O, Network, Timeout).
*   **Recover:** `Pemburu` dan `Sarang` memeriksa kesehatan sistem (CPU/Memori) dan memutuskan apakah akan menjadwalkan ulang tugas atau mengarsipkannya ke log.

## 2. Jaringan Lengkap (Network Stack)

Kami telah mengimplementasikan stack jaringan penuh di `greenfield/cotc/jaringan/`, didukung oleh update pada Host VM (`ivm`).

*   **Protokol:**
    *   **TCP:** `tcp.fox` (Socket API yang kompatibel dengan Host dan Rust).
    *   **HTTP:** `http.fox` (Klien HTTP/1.1 dengan dukungan HTTPS).
    *   **WebSocket:** `websocket.fox` (Implementasi Handshake dan Framing dasar).
*   **Keamanan & FFI:**
    *   **SSL:** `pinjam/ssl.fox` (Wrapper untuk enkripsi socket).
    *   **SSH:** `pinjam/ssh_wrapper.fox` (Wrapper untuk Paramiko).

## 3. Infrastruktur "Pinjam" (Interop/FFI)

Direktori `greenfield/cotc/pinjam/` sekarang menjadi rumah bagi wrapper yang menjembatani logika Morph dengan library Host (Python/Rust).

*   `psutil.fox`: Monitoring sistem (Memori, CPU).
*   `nursery.fox`: Abstraksi Structured Concurrency (`trio`) untuk manajemen child process di masa depan.
*   `ssl.fox` & `ssh_wrapper.fox`: Keamanan jaringan.

## 4. Perbaikan VM & Stabilitas

*   **Host VM (`ivm`):** Menambahkan `net_*` system calls di `PythonBackend` untuk mendukung operasi jaringan.
*   **Native VM (`fox_vm`):** Memperbaiki logika `_tangani_error` di `prosesor.fox` untuk menangkap stack trace *sebelum* stack unwinding, memastikan data debug yang akurat untuk Dumpbox.
*   **Bridge Fox:** Mengimplementasikan teknik *Local Global Capture* (`biar sys = sys_raw`) untuk mengatasi bug scope resolution pada Host VM di dalam blok `catch`.

---
*FoxVM tidak lagi sekadar bahasa mainan. Ia kini memiliki sistem saraf dan kekebalan tubuhnya sendiri.*
