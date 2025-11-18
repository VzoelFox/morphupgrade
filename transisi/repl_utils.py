# transisi/repl_utils.py
from enum import Enum, auto
import re

class StatusKelengkapan(Enum):
    LENGKAP = auto()
    BELUM_LENGKAP = auto()
    TIDAK_VALID = auto() # Saat ini tidak digunakan, tapi disimpan untuk masa depan

def periksa_kelengkapan_kode(sumber: str) -> StatusKelengkapan:
    """
    Memeriksa kelengkapan kode menggunakan pendekatan heuristik gabungan.
    Ini memeriksa keseimbangan kurung/kurawal dan kata kunci blok.
    """
    if not sumber.strip():
        return StatusKelengkapan.BELUM_LENGKAP

    # Hapus komentar sebelum pemeriksaan
    sumber_tanpa_komentar = re.sub(r'#.*', '', sumber)

    # Heuristik 1: Periksa keseimbangan kurung, kurawal, dan siku
    stack = []
    in_string = False
    string_char = ''

    for char in sumber_tanpa_komentar:
        if in_string:
            if char == string_char:
                in_string = False
        elif char in ('"', "'"):
            in_string = True
            string_char = char
        elif char in ('(', '[', '{'):
            stack.append(char)
        elif char == ')':
            if not stack or stack.pop() != '(': return StatusKelengkapan.LENGKAP
        elif char == ']':
            if not stack or stack.pop() != '[': return StatusKelengkapan.LENGKAP
        elif char == '}':
            if not stack or stack.pop() != '{': return StatusKelengkapan.LENGKAP

    if stack:
        return StatusKelengkapan.BELUM_LENGKAP

    # Heuristik 2: Periksa keseimbangan kata kunci blok menggunakan regex
    # \\b memastikan kita hanya mencocokkan kata utuh
    pembuka = len(re.findall(r'\bmaka\b', sumber_tanpa_komentar))
    penutup = len(re.findall(r'\bakhir\b', sumber_tanpa_komentar))

    if pembuka > penutup:
        return StatusKelengkapan.BELUM_LENGKAP

    # Heuristik 3: Baris yang diakhiri dengan operator biner atau koma
    baris_terakhir = sumber_tanpa_komentar.strip().split('\n')[-1].strip()
    if baris_terakhir.endswith(('+', '-', '*', '/', '=', ',', 'dan', 'atau', 'warisi')):
        return StatusKelengkapan.BELUM_LENGKAP

    return StatusKelengkapan.LENGKAP
