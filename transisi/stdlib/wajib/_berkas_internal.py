"""
Internal helper untuk operasi file system.
Dipanggil via FFI dari berkas.fox
"""

import os
import shutil
from pathlib import Path

def baca_file_helper(path_str):
    """Read file and return content as string."""
    try:
        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {path_str}")

        if not path.is_file():
            raise IsADirectoryError(f"Path adalah direktori: {path_str}")

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Handle binary files
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')
    except PermissionError as e:
        raise PermissionError(f"Tidak ada izin untuk membaca: {path_str}") from e

def tulis_file_helper(path_str, konten):
    """Write content to file, create parent dirs if needed."""
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(konten)

    return True

def ada_file_helper(path_str):
    """Check if file or directory exists."""
    return Path(path_str).exists()

def hapus_file_helper(path_str):
    """Delete file or directory."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path untuk dihapus tidak ditemukan: {path_str}")

    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    # No need for an else, the initial check covers non-existent paths.
    return True

def buat_direktori_helper(path_str):
    """Create directory recursively."""
    Path(path_str).mkdir(parents=True, exist_ok=True)
    return True

def daftar_file_helper(path_str):
    """List files in directory."""
    path = Path(path_str)
    if not path.is_dir():
        raise NotADirectoryError(f"Bukan direktori: {path_str}")

    return [str(item.name) for item in path.iterdir()]

def info_file_helper(path_str):
    """Get file/directory information."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path tidak ditemukan: {path_str}")
    stat = path.stat()

    return {
        "ukuran": stat.st_size,
        "dibuat": stat.st_ctime,
        "diubah": stat.st_mtime,
        "adalah_file": path.is_file(),
        "adalah_direktori": path.is_dir(),
        "path_absolut": str(path.absolute())
    }

def salin_file_helper(src_str, dst_str):
    """Copy file or directory."""
    src = Path(src_str)
    dst = Path(dst_str)

    if not src.exists():
        raise FileNotFoundError(f"Sumber tidak ditemukan: {src_str}")

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)

    return True

def pindah_file_helper(src_str, dst_str):
    """Move/rename file or directory."""
    if not Path(src_str).exists():
        raise FileNotFoundError(f"Sumber tidak ditemukan: {src_str}")
    shutil.move(src_str, dst_str)
    return True

def path_absolut_helper(path_str):
    """Get absolute path."""
    return str(Path(path_str).absolute())

def gabung_path_helper(parts):
    """Join path components from a list."""
    return str(Path(*parts))
