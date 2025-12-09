import os
import shutil

# === I/O Builtins for StandardVM ===
# Fungsi-fungsi ini dipetakan ke global VM agar bisa dipanggil oleh `cotc(stdlib)/core.fox`.
# Mereka menyediakan akses langsung ke operasi file Python.

def _io_open_builtin(path, mode):
    # Opcode IO_OPEN sebenarnya melakukan ini, tapi untuk konsistensi dengan core.fox
    # kita ekspos fungsi python langsung sebagai builtin
    return open(path, mode)

def _io_read_builtin(f, size):
    if size is None or size == -1:
        return f.read()
    return f.read(size)

def _io_write_builtin(f, content):
    f.write(content)

def _io_close_builtin(f):
    f.close()

def _io_exists_builtin(path):
    return os.path.exists(path)

def _io_delete_builtin(path):
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)

def _io_list_builtin(path):
    return os.listdir(path)

def _io_mkdir_builtin(path):
    os.makedirs(path, exist_ok=True)

# Compatibility / High Level Ops (used by old wrapper logic if any)
def builtins_baca_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def builtins_tulis_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))
    return None

def builtins_info_file(path):
    stat = os.stat(path)
    return {
        "ukuran": stat.st_size,
        "waktu_akses": stat.st_atime,
        "waktu_modifikasi": stat.st_mtime
    }

FILE_IO_BUILTINS = {
    # Primitives (Mapped to core.fox)
    "_io_open_builtin": _io_open_builtin,
    "_io_read_builtin": _io_read_builtin,
    "_io_write_builtin": _io_write_builtin,
    "_io_close_builtin": _io_close_builtin,
    "_io_exists_builtin": _io_exists_builtin,
    "_io_delete_builtin": _io_delete_builtin,
    "_io_list_builtin": _io_list_builtin,
    "_io_mkdir_builtin": _io_mkdir_builtin,

    # High Level / Helpers
    "_io_baca_file": builtins_baca_file,
    "_io_tulis_file": builtins_tulis_file,
    "_io_info_file": builtins_info_file,
}
