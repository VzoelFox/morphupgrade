import sys
import copy
from ivm.vm_context import get_current_vm
from ivm.core.structs import CodeObject

def _builtin_ingat(*args):
    vm = get_current_vm()
    if not args:
        raise TypeError("ingat() butuh 1 argumen: generator.")
    gen_obj = args[0]
    if not hasattr(gen_obj, 'frame') or not hasattr(gen_obj, 'daftar_checkpoint'):
        raise TypeError("Argumen untuk ingat() harus sebuah generator.")

    frame_copy = copy.deepcopy(gen_obj.frame)
    globals_copy = copy.deepcopy(vm.globals)

    gen_obj.daftar_checkpoint.append((frame_copy, globals_copy))
    return None

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
    # Helper for debugging AST
    if hasattr(obj, "__class__") and hasattr(obj.__class__, "name"):
        return obj.__class__.name
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
    """
    Menyalin dictionary secara shallow. Digunakan untuk backtracking logika.
    """
    if not args: return {}
    if isinstance(args[0], dict):
        return args[0].copy()
    return args[0]

def builtins_buat_code_object(*args):
    # args: [nama, instruksi, daftar_argumen]
    if len(args) < 2:
        raise TypeError("_buat_code_object butuh nama dan instruksi")

    nama = args[0]
    instruksi = args[1]
    arg_names = args[2] if len(args) > 2 else []

    # Convert Morph list of instructions (which might be list of lists) to Tuple[int, Any]
    # Morph: [[OP, ARG], [OP, ARG]]
    # Python: [(OP, ARG), (OP, ARG)]

    cleaned_instr = []
    for instr in instruksi:
        # Assuming instr is [op, arg]
        # We need to ensure types are correct?
        # Op should be int. Arg can be anything.
        if isinstance(instr, list):
            op = instr[0]
            arg = instr[1] if len(instr) > 1 else None
            cleaned_instr.append((op, arg))
        else:
            raise TypeError("Instruksi harus berupa list [op, arg]")

    # Clean arg_names (Token to string if necessary, but compiler should pass strings)
    cleaned_args = []
    for a in arg_names:
        cleaned_args.append(str(a))

    return CodeObject(name=nama, instructions=cleaned_instr, arg_names=cleaned_args)

# Map Morph names to Python functions
CORE_BUILTINS = {
    "tulis": builtins_tulis,
    "cetak": builtins_cetak,
    "masukan": builtins_masukan,
    "tipe": builtins_tipe,
    "panjang": builtins_panjang,
    "ingat": _builtin_ingat,

    # Hidden builtins for bootstrap shim
    "_panjang_builtin": builtins_panjang,
    "_tambah_builtin": builtins_tambah,
    "_gabung_builtin": builtins_gabung,
    "_float_builtin": builtins_float,
    "_int_builtin": builtins_int,
    "_str_builtin": builtins_str,
    "_tipe_objek_builtin": builtins_tipe,
    "_salin_kamus_builtin": builtins_salin_kamus,
    "_buat_code_object": builtins_buat_code_object
}
