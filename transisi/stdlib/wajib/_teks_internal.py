# transisi/stdlib/wajib/_teks_internal.py

"""
File helper internal untuk modul teks.fox.
Menyediakan fungsi Python murni yang dapat dipanggil melalui FFI
untuk melakukan operasi string yang tidak didukung secara sintaksis
oleh MORPH saat ini (misalnya, pemanggilan metode seperti 'teks.split()').
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
