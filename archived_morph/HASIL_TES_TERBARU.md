# Laporan Hasil Tes Otomatis
Tanggal: Tue Dec  9 02:48:30 UTC 2025

```
--- Menjalankan Tes IVM (36 file) ---
 menjalankan: tests/fitur_dasar/test_aritmetika.fox ... LULUS
 menjalankan: tests/fitur_dasar/test_logika.fox ... LULUS
 menjalankan: greenfield/examples/test_pattern_matching.fox ...--- Uji Literal ---
[LULUS] Cocok angka 10
 LULUS
 menjalankan: greenfield/examples/test_railwush.fox ...--- Uji Siklus Hidup Profil ---
[1] Membuat Profil Baru...
\u001b[32m[LULUS] \u001b[0mToken tidak boleh nil
\u001b[32m[LULUS] \u001b[0mToken harus cukup panjang
    Token berhasil dibuat: morph-20251209-024812-9I-linux
\u001b[32m[LULUS] \u001b[0mFile profil harus ada di disk
    File profil ditemukan: greenfield/cotc/railwush/data/f966bfb3ed6efa78da82d3aa4c68eed5e006afdbce83617321eb605f50a22c9f.mnet
\u001b[32m[LULUS] \u001b[0mKonten file tidak boleh diawali '{' (harus terenkripsi/base64)
    Konten file terverifikasi terenkripsi (Base64 signature)
[2] Memuat Profil Kembali...
\u001b[32m[LULUS] \u001b[0mGagal memuat profil dengan token valid
\u001b[32m[LULUS] \u001b[0mUsername harus cocok
\u001b[32m[LULUS] \u001b[0mKode harus cocok
\u001b[32m[LULUS] \u001b[0mCounter default harus 1
    Data profil cocok!
[3] Uji Token Salah...
Gagal membuka file: [Errno 2] No such file or directory: 'greenfield/cotc/railwush/data/7e9c080eace5f7db91790e8e99ee0328435edac7eae50c7854b9bf7054aa8fdd.mnet'
\u001b[32m[LULUS] \u001b[0mHarus return nil untuk token salah
    Penanganan token salah berhasil.
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_native_bytes.fox ...PASS: pack_int(123456789) correct.
PASS: unpack_int match original.
PASS: Float 1.5 last byte correct (0x3F).
PASS: unpack_float(1.5) match.
PASS: unpack_float(-123.456) match.
All Native Bytes Tests Finished.
 LULUS
 menjalankan: greenfield/examples/test_waktu.fox ...--- Tes Foxys (Syscall) ---
Timestamp Awal: 1765248492.5027874
\u001b[32m[LULUS] \u001b[0mWaktu harus valid (modern era)
Tidur 1 detik...
Timestamp Akhir: 1765248493.5034175
\u001b[32m[LULUS] \u001b[0mWaktu harus berjalan maju
--- Tes Logika Kabisat ---
\u001b[32m[LULUS] \u001b[0m2000 adalah kabisat
\u001b[32m[LULUS] \u001b[0m2020 adalah kabisat
\u001b[32m[LULUS] \u001b[0m2024 adalah kabisat
\u001b[32m[LULUS] \u001b[0m2021 bukan kabisat
\u001b[32m[LULUS] \u001b[0m1900 bukan kabisat (div 100 tapi not 400)
--- Tes Konversi Waktu ---
Hasil Konversi: 2023-12-25 10:30:00
\u001b[32m[LULUS] \u001b[0mTahun salah
\u001b[32m[LULUS] \u001b[0mBulan salah
\u001b[32m[LULUS] \u001b[0mHari salah
\u001b[32m[LULUS] \u001b[0mJam salah
\u001b[32m[LULUS] \u001b[0mMenit salah
\u001b[32m[LULUS] \u001b[0mDetik salah
--- Tes Waktu Nyata (Sekarang) ---
Waktu Saat Ini (UTC): 2025-12-09 02:48:13
\u001b[32m[LULUS] \u001b[0mTahun harus >= 2024
=== SEMUA TES WAKTU LULUS ===
 LULUS
 menjalankan: greenfield/examples/test_data_json.fox ...--- Tes JSON Angka (Pure Atoi) ---
12345 ->  12345
\u001b[32m[LULUS] \u001b[0mInteger positif gagal
\u001b[32m[LULUS] \u001b[0mTipe data salah
-987 ->  -987
\u001b[32m[LULUS] \u001b[0mInteger negatif gagal
12.34 ->  12.34
\u001b[32m[LULUS] \u001b[0mFloat gagal
--- Tes JSON Kompleks ---
Data:  {"id": 101}
Dekode Objek:  {"id": 101}
\u001b[32m[LULUS] \u001b[0mField id salah
SEMUA TES JSON BERHASIL
 LULUS
 menjalankan: greenfield/examples/test_foxys_io_extended.fox ...--- Tes Buat Direktori ---
Info: Direktori sudah ada, akan dicoba overwrite/idempotency.
Sukses buat direktori
\u001b[32m[LULUS] \u001b[0mDirektori harusnya ada
Sukses buat ulang (idempotent)
\u001b[32m[LULUS] \u001b[0mDirektori harus tetap ada
SEMUA TES IO EXTENDED BERHASIL
 LULUS
 menjalankan: greenfield/examples/test_fox_vm_loader.fox ...=== Fase 1: Build ===
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [], 'tipe': 'script'}]
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [[1, None]], 'tipe': 'script'}]
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [[1, None], [48, None]], 'tipe': 'script'}]
Binary tersimpan di: greenfield/examples/hello_world.fox.mvm
=== Fase 2: Load & Run (FoxVM) ===
[Pemuat] Membaca greenfield/examples/hello_world.fox.mvm ...
[Pemuat] Deserialisasi...
[Pemuat] Eksekusi...
[Pemuat] Selesai.
=== Tes Selesai ===
 LULUS
 menjalankan: greenfield/examples/test_json.fox ...=== Memulai Test JSON ===
Testing JSON Encode/Decode...
  JSON Output: {"aktif": 1, "skor": 100, "nama": "Jules"}
\u001b[32m[LULUS] \u001b[0mHasil JSON tidak boleh kosong
\u001b[32m[LULUS] \u001b[0mNama tidak cocok setelah decode
\u001b[32m[LULUS] \u001b[0mSkor tidak cocok setelah decode
  [OK] Simple Encode/Decode
Testing JSON List...
\u001b[32m[LULUS] \u001b[0mElement 0 salah
\u001b[32m[LULUS] \u001b[0mElement 3 salah
  [OK] List Encode/Decode
=== Semua Test JSON Berhasil ===
 LULUS
 menjalankan: greenfield/examples/test_struktur_lanjut.fox ...=== Mulai Tes Struktur ===
--- Tes Tumpukan (Stack) ---
Top: 3
Pop: 3
Pop: 2
Pop: 1
Kosong: True
--- Tes Antrian (Queue) ---
Front: A
Deq: A
Deq: B
Deq: C
Kosong: True
=== Selesai ===
 LULUS
 menjalankan: greenfield/examples/test_vm_compiler_wip.fox ...--- Persiapan Native VM untuk Kompiler ---
CodeObject Kompiler siap. Tipe: objek
--- Mengeksekusi Wrapper Kompiler ---
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 169, in execute
    elif opcode == Op.LOAD_INDEX: i = self.stack.pop(); t = self.stack.pop(); self.stack.append(t[i])
                                                                                                ~^^^
TypeError: 'NoneType' object is not subscriptable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "'NoneType' object is not subscriptable", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 108', 'utama at PC 269', 'jalan at PC 96', '_eksekusi_instruksi at PC 48', '_ops_data_objek at PC 272']}

 menjalankan: greenfield/examples/test_base64.fox ...=== Memulai Test Base64 ===
Testing Text Encoding/Decoding...
\u001b[32m[LULUS] \u001b[0mEnkode teks gagal
\u001b[32m[LULUS] \u001b[0mDekode teks gagal
  [OK] Text Encoding/Decoding
Testing Bytes Encoding/Decoding...
\u001b[32m[LULUS] \u001b[0mEnkode bytes gagal
\u001b[31m[GAGAL] \u001b[0mDekode bytes gagal (Harapan: b'ABC', Aktual: [65, 66, 67])
  [OK] Bytes Encoding/Decoding
=== Semua Test Berhasil ===
 LULUS
 menjalankan: greenfield/examples/uji_closure_self.fox ...--- UJI CLOSURE SELF-HOSTED ---
Hasil Closure Sederhana (10+5): 15
Counter: 1, 2
--- SUKSES SEMUA ---
 LULUS
 menjalankan: greenfield/examples/test_vm_native.fox ...--- Memulai Native VM (Aritmatika) ---
30
25
30
5.0
1
Selesai Tes Aritmatika
--- VM Selesai ---
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 259']}

 menjalankan: greenfield/examples/test_bytes_unit.fox ...Testing Integer Packing...
\u001b[32m[LULUS] \u001b[0mPanjang bytes harus 4
\u001b[32m[LULUS] \u001b[0mUnpack integer positif
\u001b[32m[LULUS] \u001b[0mOffset update
\u001b[32m[LULUS] \u001b[0mUnpack integer negatif
Testing Float Packing...
\u001b[32m[LULUS] \u001b[0mPanjang bytes float harus 8
\u001b[32m[LULUS] \u001b[0mUnpack float positif
\u001b[32m[LULUS] \u001b[0mUnpack float negatif
\u001b[32m[LULUS] \u001b[0mUnpack float zero
Testing String Packing...
\u001b[32m[LULUS] \u001b[0mPanjang string packed
\u001b[32m[LULUS] \u001b[0mUnpack string konten
\u001b[32m[LULUS] \u001b[0mUnpack string offset
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
Testing Integer Packing...
\u001b[32m[LULUS] \u001b[0mPanjang bytes harus 4
\u001b[32m[LULUS] \u001b[0mUnpack integer positif
\u001b[32m[LULUS] \u001b[0mOffset update
\u001b[32m[LULUS] \u001b[0mUnpack integer negatif
Testing Float Packing...
\u001b[32m[LULUS] \u001b[0mPanjang bytes float harus 8
\u001b[32m[LULUS] \u001b[0mUnpack float positif
\u001b[32m[LULUS] \u001b[0mUnpack float negatif
\u001b[32m[LULUS] \u001b[0mUnpack float zero
Testing String Packing...
\u001b[32m[LULUS] \u001b[0mPanjang string packed
\u001b[32m[LULUS] \u001b[0mUnpack string konten
\u001b[32m[LULUS] \u001b[0mUnpack string offset
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_vm_features.fox ...--- Tes Exception Handling ---
Ups Error
Selesai
--- Tes OOP Native ---
Meong
 LULUS
 menjalankan: greenfield/examples/test_formal_logic.fox ...Verifikasi SUKSES: Bukti valid untuk klaim (P -> P)
\u001b[32m[LULUS] \u001b[0mIdentitas P -> P harus terbukti
Verifikasi SUKSES: Bukti valid untuk klaim ((P -> Q) -> (P -> Q))
\u001b[32m[LULUS] \u001b[0mModus Ponens (Function Application) harus terbukti
Verifikasi SUKSES: Bukti valid untuk klaim ((P & Q) -> P)
\u001b[32m[LULUS] \u001b[0mEliminasi Dan (Proyeksi Kiri) harus terbukti
Verifikasi GAGAL: Mismatch.
Bukti menyimpulkan: (P -> P)
Klaim menginginkan: (P -> Q)
\u001b[32m[LULUS] \u001b[0mBukti P->P tidak boleh membuktikan P->Q
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_hashable.fox ...SUKSES: Node AST bisa jadi key dictionary.
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 17']}

 menjalankan: greenfield/examples/test_vm_call.fox ...--- Memulai Native VM (Call Test) ---
Error: CALL unknown type <Instance ObjekKode>
None
--- VM Selesai ---
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 156']}

 menjalankan: greenfield/examples/test_pure_teks_unit.fox ...--- Tes Teks Dasar ---
\u001b[32m[LULUS] \u001b[0mPanjang salah
\u001b[32m[LULUS] \u001b[0mKecil salah
\u001b[32m[LULUS] \u001b[0mBesar salah
\u001b[32m[LULUS] \u001b[0mIris salah
--- Tes Cari Ganti ---
\u001b[32m[LULUS] \u001b[0mTemukan salah
\u001b[32m[LULUS] \u001b[0mTemukan tidak ada salah
\u001b[32m[LULUS] \u001b[0mGanti salah
--- Tes Pisah ---
Buah:  ['apel', 'jeruk', 'mangga']
\u001b[32m[LULUS] \u001b[0mBuah 1 salah
\u001b[32m[LULUS] \u001b[0mBuah 2 salah
\u001b[32m[LULUS] \u001b[0mBuah 3 salah
\u001b[32m[LULUS] \u001b[0mPisah tunggal salah
SEMUA TES TEKS BERHASIL
 LULUS
 menjalankan: greenfield/examples/test_fox_vm_loop.fox ...Menjalankan FoxVM Loop 1..5
Hasil Loop: 15
\u001b[32m[LULUS] \u001b[0mSum 1..5 harus 15
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_logika_unit.fox ...\u001b[32m[LULUS] \u001b[0mX harus bind ke a
\u001b[32m[LULUS] \u001b[0mX bind a dalam struktur
\u001b[32m[LULUS] \u001b[0mY bind b dalam struktur
\u001b[32m[LULUS] \u001b[0mOccurs check berhasil dideteksi
\u001b[32m[LULUS] \u001b[0mX bind a
\u001b[32m[LULUS] \u001b[0mY bind b
\u001b[32m[LULUS] \u001b[0mX tetap a
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_vm_builtins.fox ...--- Memulai Native VM (Builtins Test) ---
3
Halo Builtin
None
--- VM Selesai ---
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 160']}

 menjalankan: greenfield/examples/test_base64_teks_berkas.fox ...=== Base64 Enkode String ASCII ===
\u001b[32m[LULUS] \u001b[0mEnkode 'Hello World' gagal
=== Base64 Dekode String ASCII ===
\u001b[32m[LULUS] \u001b[0mDekode 'Hello World' gagal
=== Base64 Enkode Bytes List ===
\u001b[32m[LULUS] \u001b[0mEnkode bytes gagal
=== Teks Pisah ===
\u001b[32m[LULUS] \u001b[0mPanjang hasil pisah salah
\u001b[32m[LULUS] \u001b[0mElemen 0 salah
\u001b[32m[LULUS] \u001b[0mElemen 1 salah
\u001b[32m[LULUS] \u001b[0mElemen 2 salah
=== Teks Ganti ===
\u001b[32m[LULUS] \u001b[0mGanti teks gagal
=== Teks Kapital/Kecil ===
\u001b[32m[LULUS] \u001b[0mKapital gagal
\u001b[32m[LULUS] \u001b[0mKecil gagal
=== Teks Potong ===
\u001b[32m[LULUS] \u001b[0mPotong spasi gagal
=== Teks Cari ===
\u001b[32m[LULUS] \u001b[0mCari index gagal
\u001b[32m[LULUS] \u001b[0mCari tidak ketemu gagal
=== Teks Iris ===
\u001b[32m[LULUS] \u001b[0mIris string gagal
\u001b[32m[LULUS] \u001b[0mIris awal gagal
=== Berkas Tulis Baca OOP ===
Gagal buka file: Must have exactly one of create/read/write/append mode and at most one plus
\u001b[31m[GAGAL] \u001b[0mGagal buka file
\u001b[31m[GAGAL] \u001b[0mGagal baca file: File belum dibuka
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 98']}

 menjalankan: greenfield/examples/test_loader.fox ...--- Kompilasi Source ---
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [], 'tipe': 'script'}]
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [[1, None]], 'tipe': 'script'}]
DEBUG CTX: <Instance Kompiler>
DEBUG TUMPUKAN: [{'instruksi': [[1, None], [48, None]], 'tipe': 'script'}]
--- Menjalankan Loader ---
[Pemuat] Membaca greenfield/examples/temp_hello.mvm ...
[Pemuat] Deserialisasi...
[Pemuat] Eksekusi...
[Pemuat] Selesai.
 GAGAL
    1. Kesalahan Kritis: Traceback (most recent call last):
  File "/app/ivm/vms/standard_vm.py", line 74, in run
    self.execute(instruction)
  File "/app/ivm/vms/standard_vm.py", line 155, in execute
    else: raise RuntimeError(f"Global '{name}' not found.")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Global 'utama' not found.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/run_ivm_tests.py", line 80, in jalankan_tes
    vm.run()
  File "/app/ivm/vms/standard_vm.py", line 84, in run
    self._handle_exception(error_obj)
  File "/app/ivm/vms/standard_vm.py", line 1118, in _handle_exception
    raise RuntimeError(f"Unhandled Panic (Global): {error_obj}")
RuntimeError: Unhandled Panic (Global): {'pesan': "Global 'utama' not found.", 'baris': 0, 'kolom': 0, 'jenis': 'ErrorSistem', 'jejak': ['<module> at PC 95']}

 menjalankan: greenfield/examples/test_binary_layout.fox ...\u001b[32m[LULUS] \u001b[0mUkuran output harus > header 16 bytes
Mencoba eksekusi hasil serialisasi...
Halo Dunia
\u001b[32m[LULUS] \u001b[0mEksekusi biner berhasil
Hasil tipe: None
\u001b[32m[LULUS] \u001b[0mHasil tidak boleh nil
\u001b[32m[LULUS] \u001b[0mSerialisasi nested berhasil
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_foxys_io.fox ...\u001b[32m[LULUS] \u001b[0mWaktu berjalan
\u001b[32m[LULUS] \u001b[0mTidur berfungsi minimal
\u001b[32m[LULUS] \u001b[0mPlatform valid: linux
\u001b[32m[LULUS] \u001b[0mTulis Sukses
\u001b[32m[LULUS] \u001b[0mBaca Sukses
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_vm_parser_wip.fox ...--- Persiapan Native VM untuk Parser ---
CodeObject Parser siap. Tipe: objek
--- Mengeksekusi Wrapper Parser ---
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t2
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t3
Error: Lokal tidak ditemukan: t4
Error: Lokal tidak ditemukan: t4
<Instance Bagian>
--- Selesai Eksekusi ---
 LULUS
 menjalankan: greenfield/examples/test_vm_lexer_wip.fox ...--- Persiapan Native VM untuk Lexer ---
Fungsi Lexer Native siap.
--- Mengeksekusi Wrapper ---
Error: CALL unknown type None
Error: CALL unknown type None
Token Result:
None
None
--- Selesai Eksekusi ---
 LULUS
 menjalankan: greenfield/examples/test_pure_teks.fox ...\u001b[32m[LULUS] \u001b[0mKecil (Pure)
\u001b[32m[LULUS] \u001b[0mBesar (Pure)
\u001b[32m[LULUS] \u001b[0mMengandung 'Morph'
\u001b[32m[LULUS] \u001b[0mMengandung 'Halo'
\u001b[32m[LULUS] \u001b[0mTidak Mengandung 'Zilch'
\u001b[32m[LULUS] \u001b[0mTemukan 'Halo' di 0
\u001b[32m[LULUS] \u001b[0mTemukan 'Morph' di 5
\u001b[32m[LULUS] \u001b[0mTemukan 'Zilch' -1
\u001b[32m[LULUS] \u001b[0mGanti 'satu' -> 'nol'
\u001b[32m[LULUS] \u001b[0mGanti tidak ada match
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_bitwise.fox ...1 << 2 = 4
16 >> 2 = 4
5 & 3 = 1
5 | 3 = 7
5 ^ 3 = 6
~5 = -6
Bitwise Test Complete
 LULUS
 menjalankan: greenfield/examples/test_foxprotocol.fox ...--- Tes URL Parser ---
\u001b[32m[LULUS] \u001b[0mSkema salah
\u001b[32m[LULUS] \u001b[0mHost salah
\u001b[32m[LULUS] \u001b[0mPort salah
\u001b[32m[LULUS] \u001b[0mDefault port HTTP salah
--- Tes HTTP Request ---
\u001b[32m[LULUS] \u001b[0mRequest Line salah
\u001b[32m[LULUS] \u001b[0mHeader Host hilang
\u001b[32m[LULUS] \u001b[0mAuto CL salah. Body len: 11
\u001b[32m[LULUS] \u001b[0mBody separator/content salah
--- Tes HTTP Response ---
\u001b[32m[LULUS] \u001b[0mStatus code salah
\u001b[32m[LULUS] \u001b[0mReason phrase salah
\u001b[32m[LULUS] \u001b[0mHeader Server tidak ditemukan
\u001b[32m[LULUS] \u001b[0mHeader Server salah
\u001b[32m[LULUS] \u001b[0mBody salah
=== SEMUA TES FOXPROTOCOL LULUS ===
 LULUS
 menjalankan: greenfield/examples/test_data_base64.fox ...--- Tes Enkode Dasar ---
Asli: Halo Dunia
Base64: SGFsbyBEdW5pYQ==
\u001b[32m[LULUS] \u001b[0mEnkripsi 'Halo Dunia' salah
--- Tes Dekode Dasar ---
Base64: SGFsbyBEdW5pYQ==
Hasil: Halo Dunia
\u001b[32m[LULUS] \u001b[0mDekripsi gagal
--- Tes Bytes Roundtrip ---
Encoded Bytes: AP8KFA==
Tipe Hasil: daftar
\u001b[32m[LULUS] \u001b[0mByte 0 salah
\u001b[32m[LULUS] \u001b[0mByte 1 salah
\u001b[32m[LULUS] \u001b[0mByte 2 salah
\u001b[32m[LULUS] \u001b[0mByte 3 salah
SEMUA TES BASE64 BERHASIL
 LULUS
 menjalankan: greenfield/examples/test_fox_vm_basic.fox ...Memulai FoxVM Self-Hosted...
FoxVM Selesai.
\u001b[32m[LULUS] \u001b[0mHasil kalkulasi 10+20 harus 30 (disimpan di hasil_terakhir)
---------------------------------------------------
\u001b[32mTotal Tes: 0\u001b[0m
\u001b[32mSEMUA TES LULUS\u001b[0m
 LULUS
 menjalankan: greenfield/examples/test_http_client.fox ...--- Tes Koneksi Gagal (Memastikan Socket Aktif) ---
Sukses: Koneksi ditolak/gagal sesuai harapan: [Errno 111] Connection refused
LULUS: Pesan error ada
=== TES KLIEN HTTP SELESAI ===
 LULUS

--- Ringkasan Tes IVM ---
Total Tes Dijalankan: 36
Lulus: 29
Gagal: 7
Exiting with code 1 due to 7 failures.
```
