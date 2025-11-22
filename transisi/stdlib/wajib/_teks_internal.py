"""
Internal helper untuk operasi string (teks).
Mengembalikan Result object.
"""
from transisi.common.result import Result, ObjekError

def _ok(data):
    return Result.sukses(data)

def _gagal(pesan):
    return Result.gagal(ObjekError(pesan=pesan, baris=0, kolom=0, jenis="ErrorTeks"))

def pisah(teks, pembatas):
    try:
        return _ok(teks.split(pembatas))
    except Exception as e:
        return _gagal(str(e))

def gabung(daftar, penghubung):
    try:
        if not isinstance(daftar, list):
            return _gagal("Argumen pertama harus berupa daftar.")
        return _ok(penghubung.join([str(x) for x in daftar]))
    except Exception as e:
        return _gagal(str(e))

def potong_spasi(teks):
    try:
        return _ok(teks.strip())
    except Exception as e:
        return _gagal(str(e))

def huruf_besar(teks):
    try:
        return _ok(teks.upper())
    except Exception as e:
        return _gagal(str(e))

def huruf_kecil(teks):
    try:
        return _ok(teks.lower())
    except Exception as e:
        return _gagal(str(e))

def ganti(teks, cari, ganti_dengan):
    try:
        return _ok(teks.replace(cari, ganti_dengan))
    except Exception as e:
        return _gagal(str(e))

def mulai_dengan(teks, awalan):
    try:
        return _ok(teks.startswith(awalan))
    except Exception as e:
        return _gagal(str(e))

def berakhir_dengan(teks, akhiran):
    try:
        return _ok(teks.endswith(akhiran))
    except Exception as e:
        return _gagal(str(e))

def panjang(teks):
    try:
        return _ok(len(teks))
    except Exception as e:
        return _gagal(str(e))

def potong(teks, awal, akhir):
    try:
        return _ok(teks[awal:akhir])
    except Exception as e:
        return _gagal(str(e))
