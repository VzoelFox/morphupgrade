# Konsep Masa Depan: Railwush "1 User 1 Token"

**Status:** Dinonaktifkan Sementara (Patch 5)
**Alasan:** Mencegah kegagalan CI/CD akibat perubahan file otomatis ("Dirty Git Status").

## Konsep
Railwush dirancang dengan filosofi "1 Profil 1 Token". Setiap kali fungsi `buat_token_baru()` dipanggil, sistem seharusnya:
1.  Membaca counter terakhir dari `greenfield/cotc/railwush/checksum.dat`.
2.  Menambahkan counter tersebut (+1).
3.  Menulis kembali counter baru ke `checksum.dat`.
4.  Menghasilkan token unik berdasarkan counter tersebut.
5.  Menghasilkan file profil `.mnet` yang sesuai.

Mekanisme ini menciptakan efek samping (side-effect) permanen pada file system setiap kali kode dijalankan (termasuk saat testing), yang menyebabkan repository menjadi "kotor" dan menggagalkan pipeline CI/CD yang ketat.

## Implementasi Asli (Referensi)

Berikut adalah logika asli yang telah dinonaktifkan di `greenfield/cotc/railwush/cryptex.fox`:

```morph
fungsi _baca_checksum() maka
    # ... logika membaca file checksum.dat ...
akhir

fungsi _tulis_checksum(nilai_baru) maka
    # ... logika menulis ke file checksum.dat ...
akhir

fungsi buat_token_baru() maka
    # ...
    biar nomor_akun = _baca_checksum()
    _tulis_checksum(nomor_akun + 1)
    # ...
akhir
```

## Cara Mengaktifkan Kembali
Untuk mengaktifkan kembali fitur ini di masa depan (saat Native VM sudah memiliki sistem file terisolasi atau mekanisme testing yang lebih canggih):

1.  Buka `greenfield/cotc/railwush/cryptex.fox`.
2.  Hapus logika "Dummy Token" atau "Mock".
3.  Kembalikan logika pembacaan dan penulisan `checksum.dat`.
4.  Pastikan file `greenfield/cotc/railwush/checksum.dat` ada dan berisi angka awal (misalnya `1`).

---
*Dokumen ini dibuat sebagai referensi untuk pengembangan Railwush di masa depan.*
