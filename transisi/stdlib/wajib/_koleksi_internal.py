"""
Internal helper untuk operasi koleksi (list/daftar).
Mengembalikan Result object.
"""
from transisi.common.result import Result, ObjekError

def _ok(data):
    return Result.sukses(data)

def _gagal(pesan):
    return Result.gagal(ObjekError(pesan=pesan, baris=0, kolom=0, jenis="ErrorKoleksi"))

def panjang(daftar):
    try:
        return _ok(len(daftar))
    except Exception as e:
        return _gagal(str(e))

def tambah(daftar, item):
    try:
        # Perhatikan: List di Python mutable, tapi di Morph kita mungkin ingin behavior immutable atau mutable explicit.
        # StandardVM passing list by reference.
        daftar.append(item)
        return _ok(daftar)
    except Exception as e:
        return _gagal(str(e))

def hapus_indeks(daftar, indeks):
    try:
        if 0 <= indeks < len(daftar):
            val = daftar.pop(indeks)
            return _ok(val)
        return _gagal("Indeks di luar jangkauan")
    except Exception as e:
        return _gagal(str(e))

def urutkan(daftar):
    try:
        # Return new sorted list (immutable style safer for functional calls)
        return _ok(sorted(daftar))
    except Exception as e:
        return _gagal(str(e))

def balik(daftar):
    try:
        return _ok(list(reversed(daftar)))
    except Exception as e:
        return _gagal(str(e))

def cari(daftar, item):
    try:
        return _ok(daftar.index(item))
    except ValueError:
        return _ok(-1)
    except Exception as e:
        return _gagal(str(e))

def gabung_list(daftar1, daftar2):
    try:
        return _ok(daftar1 + daftar2)
    except Exception as e:
        return _gagal(str(e))
