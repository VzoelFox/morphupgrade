# -*- coding: utf-8 -*-

"""
- PATCH-013: Standardisasi format pesan kesalahan.
"""


class ErrorFormatter:
    """Utility terpusat untuk formatting error messages yang konsisten"""

    @staticmethod
    def format_leksikal_error(baris, kolom, pesan):
        return f"Kesalahan di baris {baris}, kolom {kolom}: {pesan}"

    @staticmethod
    def format_pengurai_error(token, pesan, cuplikan=""):
        base = f"Kesalahan di baris {token.baris}, kolom {token.kolom}: {pesan}"
        return f"{base}\n{cuplikan}" if cuplikan else base

    @staticmethod
    def format_runtime_error(token, pesan):
        return f"Kesalahan di baris {token.baris}, kolom {token.kolom}: {pesan}"
