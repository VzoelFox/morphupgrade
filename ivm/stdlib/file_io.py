import os
import shutil
from transisi.common.result import Result

# === Helper Internals ===
# Fungsi-fungsi ini sekarang menerima argumen yang di-unpack (*args),
# sesuai dengan konvensi di core.py dan panggilan VM, dan mengembalikan Result.

def builtins_baca_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return Result.sukses(f.read())
    except Exception as e:
        return Result.gagal(str(e))

def builtins_tulis_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))
        return Result.sukses(None)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_ada_file(path):
    # Fungsi ini tidak melempar error, jadi kita bisa langsung bungkus hasilnya.
    return Result.sukses(os.path.exists(path))

def builtins_hapus_file(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return Result.sukses(None)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_buat_direktori(path):
    try:
        os.makedirs(path, exist_ok=True)
        return Result.sukses(None)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_daftar_file(path):
    try:
        return Result.sukses(os.listdir(path))
    except Exception as e:
        return Result.gagal(str(e))

def builtins_info_file(path):
    try:
        stat = os.stat(path)
        info = {
            "ukuran": stat.st_size,
            "waktu_akses": stat.st_atime,
            "waktu_modifikasi": stat.st_mtime,
            "apakah_file": os.path.isfile(path),
            "apakah_folder": os.path.isdir(path)
        }
        return Result.sukses(info)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_salin_file(src, dst):
    try:
        shutil.copy2(src, dst)
        return Result.sukses(None)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_pindah_file(src, dst):
    try:
        shutil.move(src, dst)
        return Result.sukses(None)
    except Exception as e:
        return Result.gagal(str(e))

def builtins_path_absolut(path):
    try:
        return Result.sukses(os.path.abspath(path))
    except Exception as e:
        return Result.gagal(str(e))

def builtins_gabung_path(*parts):
    try:
        return Result.sukses(os.path.join(*parts))
    except Exception as e:
        return Result.gagal(str(e))

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
}
