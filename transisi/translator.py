# transisi/translator.py
"""
File ini menyediakan akses kompatibilitas mundur ke kelas Penerjemah dan tipe runtime-nya.

Di masa mendatang, impor harus diperbarui untuk menunjuk langsung ke:
`from transisi.penerjemah import <NamaKelas>`
"""
from .penerjemah import (
    Penerjemah,
    Lingkungan,
    Fungsi,
    FungsiAsink,
    MorphKelas,
    MorphInstance,
    InstansiVarian,
    KonstruktorVarian,
    TipeVarian,
    FungsiBawaan,
    FungsiBawaanAsink,
    NilaiKembalian,
    BerhentiLoop,
    LanjutkanLoop,
)

__all__ = [
    'Penerjemah',
    'Lingkungan',
    'Fungsi',
    'FungsiAsink',
    'MorphKelas',
    'MorphInstance',
    'InstansiVarian',
    'KonstruktorVarian',
    'TipeVarian',
    'FungsiBawaan',
    'FungsiBawaanAsink',
    'NilaiKembalian',
    'BerhentiLoop',
    'LanjutkanLoop',
]
