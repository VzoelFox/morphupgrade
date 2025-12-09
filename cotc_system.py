"""
SKELETON SELF-HOSTING: COTC SYSTEM (CORE LIBRARIES)
===================================================
File ini berisi konsep kode Morph untuk pustaka inti (Core of the Core).
"""

MORPH_SOURCE = r"""
# cotc/sistem.fox
# Wrapper sistem inti

pinjam "sys" sebagai _sys
pinjam "os" sebagai _os

fungsi keluar(kode) maka
    _sys.exit(kode)
akhir

fungsi get_env(kunci) maka
    kembali _os.environ.get(kunci)
akhir

kelas Berkas maka
    biar handle

    fungsi buka(path, mode) maka
        ini.handle = open(path, mode)
    akhir

    fungsi baca() maka
        kembali ini.handle.read()
    akhir

    fungsi tutup() maka
        ini.handle.close()
    akhir
akhir
"""
