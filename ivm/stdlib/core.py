import sys

def builtins_tulis(*args):
    print(*args)
    return None

def builtins_cetak(*args):
    # Print without newline
    print(*args, end="", flush=True)
    return None

def builtins_masukan(*args):
    prompt = args[0] if args else ""
    return input(str(prompt))

def builtins_tipe(*args):
    if not args:
        raise TypeError("tipe_dari() butuh 1 argumen")
    obj = args[0]
    if isinstance(obj, bool): return "boolean"
    if isinstance(obj, int): return "angka"
    if isinstance(obj, float): return "angka"
    if isinstance(obj, str): return "teks"
    if isinstance(obj, list): return "daftar"
    if isinstance(obj, dict): return "kamus"
    if obj is None: return "nil"
    return "objek"

def builtins_panjang(*args):
    if not args:
        raise TypeError("panjang() butuh 1 argumen")
    try:
        return len(args[0])
    except TypeError:
        return 0

# Helper functions alias for bootstrapping (so stdlib/core.fox can wrap them)
def builtins_tambah(*args):
    # args[0].append(args[1])
    if len(args) < 2: raise TypeError("tambah butuh list dan item")
    args[0].append(args[1])
    return None

def builtins_gabung(*args):
    # args[1].join(args[0]) basically
    if len(args) < 2: raise TypeError("gabung butuh list dan separator")
    lst = args[0]
    sep = args[1]
    return sep.join([str(x) for x in lst])

def builtins_float(*args):
    return float(args[0])

def builtins_int(*args):
    return int(args[0])

def builtins_str(*args):
    return str(args[0])

def builtins_salin_kamus(*args):
    if not args: return {}
    if isinstance(args[0], dict):
        return args[0].copy()
    return args[0]

# Map Morph names to Python functions
CORE_BUILTINS = {
    "tulis": builtins_tulis,
    "cetak": builtins_cetak,
    "masukan": builtins_masukan,
    "tipe": builtins_tipe,
    "panjang": builtins_panjang,

    # Hidden builtins for bootstrap shim
    "_panjang_builtin": builtins_panjang,
    "_tambah_builtin": builtins_tambah,
    "_gabung_builtin": builtins_gabung,
    "_float_builtin": builtins_float,
    "_int_builtin": builtins_int,
    "_str_builtin": builtins_str,
    "_tipe_objek_builtin": builtins_tipe,
    "_salin_kamus_builtin": builtins_salin_kamus
}
