import time
import sys

def builtins_waktu(args):
    return time.time()

def builtins_keluar(args):
    code = args[0] if args else 0
    sys.exit(code)

SYSTEM_BUILTINS = {
    "waktu": builtins_waktu,
    "keluar": builtins_keluar,
}
