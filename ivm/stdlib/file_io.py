import os
import shutil
import time

# === Helper Internals ===
# Fungsi-fungsi ini dipanggil langsung oleh VM sebagai builtin.
# Mereka menerima satu argumen `args` yang merupakan list dari argumen yang dipush ke stack.

def _arg(args, index, name):
    if index >= len(args):
        raise TypeError(f"Fungsi butuh argumen '{name}' di posisi {index}")
    return args[index]

def builtins_baca_file(args):
    path = _arg(args, 0, "path")
    # Strict checking? Or rely on open()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def builtins_tulis_file(args):
    path = _arg(args, 0, "path")
    content = _arg(args, 1, "konten")
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))
    return None

def builtins_ada_file(args):
    path = _arg(args, 0, "path")
    return os.path.exists(path)

def builtins_hapus_file(args):
    path = _arg(args, 0, "path")
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)
    return None

def builtins_buat_direktori(args):
    path = _arg(args, 0, "path")
    os.makedirs(path, exist_ok=True)
    return None

def builtins_daftar_file(args):
    path = _arg(args, 0, "path")
    return os.listdir(path)

def builtins_info_file(args):
    path = _arg(args, 0, "path")
    stat = os.stat(path)
    return {
        "ukuran": stat.st_size,
        "waktu_akses": stat.st_atime,
        "waktu_modifikasi": stat.st_mtime,
        "apakah_file": os.path.isfile(path),
        "apakah_folder": os.path.isdir(path)
    }

def builtins_salin_file(args):
    src = _arg(args, 0, "sumber")
    dst = _arg(args, 1, "tujuan")
    shutil.copy2(src, dst)
    return None

def builtins_pindah_file(args):
    src = _arg(args, 0, "sumber")
    dst = _arg(args, 1, "tujuan")
    shutil.move(src, dst)
    return None

def builtins_path_absolut(args):
    path = _arg(args, 0, "path")
    return os.path.abspath(path)

def builtins_gabung_path(args):
    # Menerima list string
    parts = _arg(args, 0, "bagian_path")
    if not isinstance(parts, list):
        raise TypeError("gabung_path butuh list string")
    return os.path.join(*parts)


FILE_IO_BUILTINS = {
    "_io_baca_file": builtins_baca_file,
    "_io_tulis_file": builtins_tulis_file,
    "_io_ada_file": builtins_ada_file,
    "_io_hapus_file": builtins_hapus_file,
    "_io_buat_direktori": builtins_buat_direktori,
    "_io_daftar_file": builtins_daftar_file,
    "_io_info_file": builtins_info_file,
    "_io_salin_file": builtins_salin_file,
    "_io_pindah_file": builtins_pindah_file,
    "_io_path_absolut": builtins_path_absolut,
    "_io_gabung_path": builtins_gabung_path,

    # Legacy support (optional, maybe remove later to force _io usage)
    # "baca_file": builtins_baca_file,
    # "tulis_file": builtins_tulis_file,
}
