# transisi/stdlib/wajib/ffi_daftar.py
"""
Modul FFI Python langsung untuk operasi Daftar.
Ini diimpor menggunakan 'pinjam' di kode Morph dan diekspos
sebagai modul Python asli.
"""

# Impor fungsi helper yang sudah ada.
from ._stdlib_internal import (
    panjang_daftar,
    tambah_ke_daftar,
    hapus_dari_daftar,
    urut_daftar,
    balik_daftar,
    cari_di_daftar,
)

# Ganti nama agar lebih sesuai dengan konvensi pemanggilan Python
# (meskipun tidak wajib, ini adalah praktik yang baik).
panjang = panjang_daftar
tambah = tambah_ke_daftar
hapus = hapus_dari_daftar
urut = urut_daftar
balik = balik_daftar
cari = cari_di_daftar
