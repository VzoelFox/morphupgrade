# transisi/penerjemah/__init__.py
"""
Modul Penerjemah (Interpreter) untuk Morph.

Modul ini menggabungkan berbagai komponen dari interpreter AST-walking.
"""

from .tipe_runtime import (
    NilaiKembalian, BerhentiLoop, LanjutkanLoop,
    FungsiBawaan, FungsiBawaanAsink, Lingkungan,
    InstansiVarian, KonstruktorVarian, TipeVarian,
    MorphInstance, MorphKelas, Fungsi, FungsiAsink
)
from .utama import Penerjemah

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
