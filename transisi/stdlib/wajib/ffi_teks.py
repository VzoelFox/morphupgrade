# transisi/stdlib/wajib/ffi_teks.py
"""
Modul FFI Python langsung untuk operasi Teks/String.
"""

from ._stdlib_internal import (
    pisah,
    gabung,
    potong_spasi,
    huruf_besar,
    huruf_kecil,
    ganti,
    mulai_dengan,
    berakhir_dengan
)

def panjang(teks):
    return len(teks)

def karakter_di(teks, indeks):
    if 0 <= indeks < len(teks):
        return teks[indeks]
    # Kembalikan string kosong jika di luar jangkauan, untuk keamanan.
    return ""

def substring(teks, awal, akhir):
    return teks[awal:akhir]

def ke_angka(teks):
    try:
        nilai = float(teks)
        if nilai.is_integer():
            return int(nilai)
        return nilai
    except (ValueError, TypeError):
        return 0 # Kembalikan nilai default yang aman
