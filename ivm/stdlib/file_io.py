import os

def builtins_baca_file(args):
    if not args:
        raise TypeError("baca_file() butuh path file")
    path = args[0]
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

def builtins_tulis_file(args):
    if len(args) < 2:
        raise TypeError("tulis_file() butuh path dan konten")
    path = args[0]
    content = args[1]
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))
    return None

FILE_IO_BUILTINS = {
    "baca_file": builtins_baca_file,
    "tulis_file": builtins_tulis_file,
}
