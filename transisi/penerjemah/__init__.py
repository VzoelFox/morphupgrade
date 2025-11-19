# transisi/penerjemah/__init__.py
"""
Modul Penerjemah (Interpreter) untuk Morph.

Modul ini menggabungkan berbagai komponen dari interpreter AST-walking:
- Tipe data runtime (`tipe_runtime.py`)
- Visitor untuk ekspresi (`visitor_ekspresi.py`)
- Visitor untuk pernyataan (`visitor_pernyataan.py`)
- Visitor untuk sistem tipe dan modul (`visitor_sistem.py`)
- Kelas Penerjemah utama yang menyatukan semuanya (`utama.py`)
"""

from .utama import Penerjemah

__all__ = ['Penerjemah']
