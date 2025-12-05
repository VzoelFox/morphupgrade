import os
import shutil

# === Helper Internals ===
# Fungsi-fungsi ini sekarang mengembalikan nilai mentah (raw values).
# Error akan dilempar sebagai Exception Python standar, yang akan ditangkap
# oleh VM/FFI Bridge dan diteruskan sebagai Morph Error jika ada blok coba/tangkap.
# Wrapper di greenfield/cotc/io/berkas.fox yang bertanggung jawab membungkusnya dalam Result.

def builtins_baca_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def builtins_baca_file_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def builtins_tulis_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))
    return None

def builtins_tulis_file_bytes(path, content):
    with open(path, "wb") as f:
        f.write(content)
    return None

def builtins_ada_file(path):
    return os.path.exists(path)

def builtins_hapus_file(path):
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)
    return None

def builtins_buat_direktori(path):
    os.makedirs(path, exist_ok=True)
    return None

def builtins_daftar_file(path):
    return os.listdir(path)

def builtins_info_file(path):
    stat = os.stat(path)
    return {
        "ukuran": stat.st_size,
        "waktu_akses": stat.st_atime,
        "waktu_modifikasi": stat.st_mtime,
        "apakah_file": os.path.isfile(path),
        "apakah_folder": os.path.isdir(path)
    }

def builtins_salin_file(src, dst):
    shutil.copy2(src, dst)
    return None

def builtins_pindah_file(src, dst):
    shutil.move(src, dst)
    return None

def builtins_path_absolut(path):
    return os.path.abspath(path)

def builtins_gabung_path(*parts):
    return os.path.join(*parts)

FILE_IO_BUILTINS = {
    "_io_baca_file": builtins_baca_file,
    "_io_baca_file_bytes": builtins_baca_file_bytes,
    "_io_tulis_file": builtins_tulis_file,
    "_io_tulis_file_bytes": builtins_tulis_file_bytes,
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
