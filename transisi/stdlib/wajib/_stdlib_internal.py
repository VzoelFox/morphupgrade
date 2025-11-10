# transisi/stdlib/wajib/_stdlib_internal.py
import datetime

"""
File helper internal untuk modul-modul standard library.
Menyediakan fungsi Python murni yang dapat dipanggil melalui FFI
untuk melakukan operasi yang tidak didukung secara sintaksis atau
tipe oleh MORPH saat ini.
"""

def pisah(teks, pembatas):
    return teks.split(pembatas)

def gabung(daftar, penghubung):
    return penghubung.join(daftar)

def potong_spasi(teks):
    return teks.strip()

def huruf_besar(teks):
    return teks.upper()

def huruf_kecil(teks):
    return teks.lower()

def ganti(teks, cari, ganti_dengan):
    return teks.replace(cari, ganti_dengan)

def mulai_dengan(teks, awalan):
    return teks.startswith(awalan)

def berakhir_dengan(teks, akhiran):
    return teks.endswith(akhiran)

# --- Helper untuk Waktu ---

def tambah_hari_ke_datetime(dt_obj, jumlah_hari):
    return dt_obj + datetime.timedelta(days=jumlah_hari)

def selisih_hari_antara_datetime(dt_obj1, dt_obj2):
    return (dt_obj1 - dt_obj2).days

# --- Helper untuk Daftar ---

def panjang_daftar(daftar):
    return len(daftar)

def tambah_ke_daftar(daftar, item):
    daftar.append(item)
    return daftar # Kembalikan daftar yang dimodifikasi

def hapus_dari_daftar(daftar, indeks):
    if 0 <= indeks < len(daftar):
        daftar.pop(indeks)
    return daftar

def urut_daftar(daftar):
    return sorted(daftar)

def balik_daftar(daftar):
    return list(reversed(daftar))

def cari_di_daftar(daftar, item):
    try:
        return daftar.index(item)
    except ValueError:
        return -1 # Kembalikan -1 jika tidak ditemukan
