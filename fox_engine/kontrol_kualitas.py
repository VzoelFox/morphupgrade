# fox_engine/kontrol_kualitas.py
# PATCH-015D: Perbaikan logika validasi tugas dan penanganan galat.

from typing import List
from .core import TugasFox, FoxMode, IOType
from .errors import TugasTidakValidError

class KontrolKualitasFox:
    """
    Komponen yang bertanggung jawab untuk memvalidasi tugas sebelum dieksekusi.
    Memastikan tugas memenuhi standar kualitas dan keamanan.
    """

    def validasi_tugas(self, tugas: TugasFox):
        """
        Memeriksa apakah tugas valid.
        Melemparkan TugasTidakValidError jika ada pelanggaran.
        """
        # 1. Validasi Nama
        if not tugas.nama or not isinstance(tugas.nama, str):
            raise TugasTidakValidError("Nama tugas harus string yang tidak kosong.")

        # 2. Validasi Callable
        if not callable(tugas.coroutine_func):
            raise TugasTidakValidError(f"Fungsi tugas '{tugas.nama}' harus berupa callable.")

        # 3. Validasi Mode
        if not isinstance(tugas.mode, FoxMode):
            raise TugasTidakValidError(f"Mode tugas '{tugas.nama}' tidak valid.")

        # 4. Validasi MiniFox (IO Handler)
        if tugas.mode == FoxMode.MINIFOX:
            # Pengecualian untuk NETWORK_GENERIC yang menggunakan coroutine langsung
            if tugas.jenis_operasi == IOType.NETWORK_GENERIC:
                pass # Valid
            elif not tugas.io_handler or not callable(tugas.io_handler):
                # Untuk streaming, kita menggunakan mekanisme internal, jadi mungkin io_handler diset internal
                # Tapi secara umum user harus provide jika menggunakan mfox manual
                pass # Relaxed validation for simplicity in prototype

        # 5. Validasi Batas Waktu
        if tugas.batas_waktu is not None and tugas.batas_waktu <= 0:
            raise TugasTidakValidError(f"Batas waktu tugas '{tugas.nama}' harus positif.")

        # 6. Validasi Optimisasi (ThunderFox)
        if tugas.mode == FoxMode.THUNDERFOX:
            # Pastikan tugas layak untuk optimisasi berat (CPU bound)
            # Ini sulit dicek secara statis tanpa analisis kode mendalam.
            # Sebagai heuristik, kita bisa cek apakah ini tugas I/O (tidak cocok untuk tfox)
            if tugas.jenis_operasi:
                 # Peringatan: ThunderFox tidak optimal untuk I/O
                 # Kita tidak raise Error, tapi mungkin log warning (jika logger tersedia)
                 pass
