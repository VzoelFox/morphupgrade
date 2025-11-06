# fox_engine/internal/operasi_file.py
# PATCH-016B: Modul baru untuk operasi file yang dioptimalkan.
# PATCH-017A: Ganti galat bawaan dengan eksepsi kustom FoxEngine.
"""
Modul ini menyediakan fungsionalitas tingkat lanjut untuk operasi file,
dioptimalkan untuk digunakan oleh MiniFoxStrategy.
"""
import os
from typing import Tuple, Generator

from ..errors import IOKesalahan, FileTidakDitemukan

# Ukuran buffer default (misalnya, 8KB), dapat disesuaikan.
UKURAN_BUFFER_DEFAULT = 8 * 1024

def baca_file_dengan_buffer(path: str, ukuran_buffer: int = UKURAN_BUFFER_DEFAULT) -> Tuple[bytes, int]:
    """
    Membaca seluruh isi file ke dalam bytes menggunakan buffer.

    Args:
        path (str): Path lengkap ke file.
        ukuran_buffer (int): Ukuran buffer untuk setiap operasi baca.

    Returns:
        Tuple[bytes, int]: Isi file dalam bentuk bytes dan jumlah total byte yang dibaca.

    Raises:
        FileTidakDitemukan: Jika file di path yang diberikan tidak ada.
        IOKesalahan: Jika terjadi galat I/O lainnya saat membaca.
    """
    konten = bytearray()
    total_byte_dibaca = 0
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(ukuran_buffer)
                if not chunk:
                    break
                konten.extend(chunk)
                total_byte_dibaca += len(chunk)
        return bytes(konten), total_byte_dibaca
    except FileNotFoundError:
        raise FileTidakDitemukan(path)
    except IOError as e:
        raise IOKesalahan("Gagal membaca file", path) from e

def tulis_file_dengan_buffer(path: str, data: bytes, ukuran_buffer: int = UKURAN_BUFFER_DEFAULT) -> Tuple[None, int]:
    """
    Menulis data bytes ke file menggunakan buffer.

    Args:
        path (str): Path lengkap ke file tujuan.
        data (bytes): Data yang akan ditulis.
        ukuran_buffer (int): Ukuran buffer untuk setiap operasi tulis.

    Returns:
        Tuple[None, int]: None dan jumlah total byte yang ditulis.

    Raises:
        IOKesalahan: Jika terjadi galat I/O saat menulis.
    """
    total_byte_ditulis = 0
    try:
        with open(path, "wb") as f:
            for i in range(0, len(data), ukuran_buffer):
                chunk = data[i:i + ukuran_buffer]
                bytes_ditulis = f.write(chunk)
                total_byte_ditulis += bytes_ditulis
        return None, total_byte_ditulis
    except IOError as e:
        raise IOKesalahan("Gagal menulis ke file", path) from e

def stream_file_per_baris(path: str) -> Generator[Tuple[bytes, int], None, None]:
    """
    Membaca file baris per baris sebagai generator (streaming).

    Yields:
        Generator[Tuple[bytes, int], None, None]: Menghasilkan tuple berisi
                                                  satu baris (dalam bytes) dan ukurannya.

    Raises:
        FileTidakDitemukan: Jika file di path yang diberikan tidak ada.
        IOKesalahan: Jika terjadi galat I/O lainnya saat streaming.
    """
    try:
        with open(path, "rb") as f:
            for line in f:
                yield line, len(line)
    except FileNotFoundError:
        raise FileTidakDitemukan(path)
    except IOError as e:
        raise IOKesalahan("Gagal melakukan streaming dari file", path) from e
