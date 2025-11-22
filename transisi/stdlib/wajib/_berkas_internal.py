"""
Internal helper untuk operasi file system.
Dipanggil via FFI dari berkas.fox

Refactored: Menggunakan transisi.common.result.Result untuk robustness.
"""

import os
import shutil
from pathlib import Path
from transisi.common.result import Result, ObjekError

def _ok(data=None):
    return Result.sukses(data)

def _gagal(pesan):
    return Result.gagal(ObjekError(pesan=pesan, baris=0, kolom=0, jenis="ErrorIO"))

def baca_file_helper(path_str):
    """Read file and return content as string."""
    try:
        path = Path(path_str)
        if not path.exists():
            return _gagal(f"File tidak ditemukan: {path_str}")

        if not path.is_file():
            return _gagal(f"Path adalah direktori: {path_str}")

        with open(path, 'r', encoding='utf-8') as f:
            return _ok(f.read())
    except UnicodeDecodeError:
        try:
            with open(path, 'rb') as f:
                return _ok(f.read().decode('utf-8', errors='replace'))
        except Exception as e:
            return _gagal(f"Gagal membaca file binary: {e}")
    except PermissionError:
        return _gagal(f"Tidak ada izin untuk membaca: {path_str}")
    except Exception as e:
        return _gagal(f"Error sistem tidak terduga: {e}")

def tulis_file_helper(path_str, konten):
    """Write content to file, create parent dirs if needed."""
    try:
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(konten))
        return _ok(True)
    except PermissionError:
        return _gagal(f"Tidak ada izin untuk menulis: {path_str}")
    except Exception as e:
        return _gagal(f"Gagal menulis file: {e}")

def ada_file_helper(path_str):
    """Check if file or directory exists."""
    try:
        return _ok(Path(path_str).exists())
    except Exception as e:
        return _gagal(str(e))

def hapus_file_helper(path_str):
    """Delete file or directory."""
    try:
        path = Path(path_str)
        if not path.exists():
            return _gagal(f"Path tidak ditemukan: {path_str}")

        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return _ok(True)
    except PermissionError:
        return _gagal(f"Tidak ada izin menghapus: {path_str}")
    except Exception as e:
        return _gagal(f"Gagal menghapus: {e}")

def buat_direktori_helper(path_str):
    """Create directory recursively."""
    try:
        Path(path_str).mkdir(parents=True, exist_ok=True)
        return _ok(True)
    except Exception as e:
        return _gagal(f"Gagal membuat direktori: {e}")

def daftar_file_helper(path_str):
    """List files in directory."""
    try:
        path = Path(path_str)
        if not path.is_dir():
            return _gagal(f"Bukan direktori: {path_str}")
        return _ok([str(item.name) for item in path.iterdir()])
    except Exception as e:
        return _gagal(f"Gagal listing direktori: {e}")

def info_file_helper(path_str):
    """Get file/directory information."""
    try:
        path = Path(path_str)
        if not path.exists():
            return _gagal(f"Path tidak ditemukan: {path_str}")
        stat = path.stat()
        data = {
            "ukuran": stat.st_size,
            "dibuat": stat.st_ctime,
            "diubah": stat.st_mtime,
            "adalah_file": path.is_file(),
            "adalah_direktori": path.is_dir(),
            "path_absolut": str(path.absolute())
        }
        return _ok(data)
    except Exception as e:
        return _gagal(f"Gagal mengambil info: {e}")

def salin_file_helper(src_str, dst_str):
    """Copy file or directory."""
    try:
        src = Path(src_str)
        dst = Path(dst_str)
        if not src.exists():
            return _gagal(f"Sumber tidak ditemukan: {src_str}")

        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        return _ok(True)
    except Exception as e:
        return _gagal(f"Gagal menyalin: {e}")

def pindah_file_helper(src_str, dst_str):
    """Move/rename file or directory."""
    try:
        if not Path(src_str).exists():
            return _gagal(f"Sumber tidak ditemukan: {src_str}")
        shutil.move(src_str, dst_str)
        return _ok(True)
    except Exception as e:
        return _gagal(f"Gagal memindahkan: {e}")

def path_absolut_helper(path_str):
    try:
        return _ok(str(Path(path_str).absolute()))
    except Exception as e:
        return _gagal(str(e))

def gabung_path_helper(parts):
    try:
        return _ok(str(Path(*parts)))
    except Exception as e:
        return _gagal(str(e))
