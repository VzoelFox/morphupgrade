import sys

def builtins_tulis(args):
    print(*args)
    return None

def builtins_masukan(args):
    prompt = args[0] if args else ""
    return input(str(prompt))

def builtins_tipe(args):
    if not args:
        raise TypeError("tipe_dari() butuh 1 argumen")
    obj = args[0]
    if isinstance(obj, bool): return "boolean"
    if isinstance(obj, int): return "angka" # Simplification
    if isinstance(obj, float): return "angka"
    if isinstance(obj, str): return "teks"
    if isinstance(obj, list): return "daftar"
    if isinstance(obj, dict): return "kamus"
    if obj is None: return "nil"
    return "objek"

def builtins_panjang(args):
    if not args:
        raise TypeError("panjang() butuh 1 argumen")
    try:
        return len(args[0])
    except TypeError:
        return 0

# Map Morph names to Python functions
CORE_BUILTINS = {
    "tulis": builtins_tulis,
    "masukan": builtins_masukan,
    "tipe": builtins_tipe,
    "panjang": builtins_panjang,
}
