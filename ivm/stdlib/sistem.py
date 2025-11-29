import time
import sys

# Perbaikan tanda tangan fungsi:
# VM memanggil builtin dengan unpacking argument (*args).
# Jadi fungsi harus menerima argumen secara eksplisit atau menggunakan *args.

def builtins_waktu():
    return time.time()

def builtins_keluar(code=0):
    sys.exit(code)

SYSTEM_BUILTINS = {
    "waktu": builtins_waktu,
    "keluar": builtins_keluar,
}
