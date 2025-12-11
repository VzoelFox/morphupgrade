# Konsep Masa Depan: Syscalls & Penghapusan Ketergantungan Python

**Status:** Draft (Patch 5)
**Tujuan:** Mengisolasi ketergantungan `pinjam` ke Python dalam satu layer tipis (Syscalls), memudahkan porting ke Native VM (C/Rust) di masa depan.

## Latar Belakang
Saat ini, `greenfield/fox_vm` dan `greenfield/cotc` masih banyak menggunakan `pinjam "..."` untuk mengakses fungsi host (Python), seperti `builtins`, `os`, `sys`, dll. Ini membuat VM Self-Hosted tidak benar-benar mandiri.

## Rencana Implementasi

### 1. Layer `greenfield/cotc/sys/syscalls.fox`
Semua operasi yang memerlukan interaksi dengan sistem operasi atau host runtime HARUS melalui modul ini.
Modul lain (seperti `io/berkas.fox`, `stdlib/core.fox`) tidak boleh melakukan `pinjam` langsung ke modul Python.

Contoh struktur `syscalls.fox`:
```morph
# Syscall Interface
# Saat ini membungkus Python, nanti diganti dengan Native Trap

pinjam "os" sebagai _os_impl
pinjam "builtins" sebagai _py_impl

fungsi sys_buka_file(path, mode) maka
    kembali _py_impl.open(path, mode)
akhir

fungsi sys_keluar(kode) maka
    _py_impl.exit(kode)
akhir
```

### 2. Refactor `stdlib/core.fox`
Menghapus `pinjam` dan menggantinya dengan panggilan ke `syscalls` atau implementasi Pure Morph jika memungkinkan.

### 3. Native VM (Future)
Ketika Native VM (misalnya ditulis ulang dengan Rust) siap, modul `syscalls.fox` akan diganti implementasinya menjadi instruksi native (opcode `SYSCALL`) yang langsung berkomunikasi dengan VM Rust tersebut, tanpa lapisan Python sama sekali.
