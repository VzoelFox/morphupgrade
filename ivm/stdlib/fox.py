import asyncio
import logging

# Upaya untuk mengimpor fox_engine, tetapi jangan gagal jika tidak ada.
# Ini memungkinkan IVM untuk digunakan dalam konteks di mana fox_engine (dan dependensinya seperti aiohttp)
# tidak diinstal, misalnya, untuk alat analisis statis.
try:
    from fox_engine import api as fox_api
    from fox_engine.monitor_sumber_daya import MonitorSumberDaya
    from fox_engine.batas_adaptif import BatasAdaptif
    FOX_ENGINE_AVAILABLE = True
except ImportError:
    FOX_ENGINE_AVAILABLE = False
    fox_api = None # Pastikan variabel ada

from ivm.vms import standard_vm  # Untuk mengakses get_current_vm

# Helper to run async functions from sync VM
def _run_sync(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.run(coro)
    else:
        return asyncio.run(coro)

def _execute_morph_function(code_obj, args):
    """
    Executes a Morph CodeObject using the current running VM instance.
    """
    vm = standard_vm.get_current_vm()
    if vm is None:
        raise RuntimeError("Fox API dipanggil di luar konteks StandardVM yang sedang berjalan.")
    return vm.call_function_sync(code_obj, args)

def _create_fox_builtin(api_func_name):
    def builtin_wrapper(*args):
        if not FOX_ENGINE_AVAILABLE:
            raise RuntimeError("Fungsi Fox Engine tidak tersedia. Pastikan fox_engine dan dependensinya terinstal.")

        if len(args) < 2:
            raise TypeError(f"Fungsi fox.{api_func_name} butuh minimal nama dan fungsi")

        nama = args[0]
        func = args[1]
        extra_args = args[2:]

        async def _wrapper(*a, **kw):
            all_args = list(a) + list(kw.values())
            if callable(func):
                return func(*all_args) # Unpack args for python callables
            else:
                return _execute_morph_function(func, all_args)

        # Menggunakan getattr untuk memanggil fungsi API yang sebenarnya dari modul fox_api
        api_func = getattr(fox_api, api_func_name)
        return _run_sync(api_func(nama, _wrapper, *extra_args))
    return builtin_wrapper

def _fox_cek_sumber_daya():
    """
    Wrapper untuk MonitorSumberDaya.cek_kesehatan_sistem()
    Mengembalikan dict: {'persen_memori': float, 'persen_cpu': float}
    """
    if FOX_ENGINE_AVAILABLE:
        # Kita buat instance baru setiap kali panggil untuk stateless check sederhana
        # Di produksi, ini harusnya singleton yang dikelola VM
        monitor = MonitorSumberDaya(BatasAdaptif())
        return monitor.cek_kesehatan_sistem()
    else:
        return {'persen_memori': 0.0, 'persen_cpu': 0.0, 'status': 'mock'}

# Inisialisasi FOX_BUILTINS
FOX_BUILTINS = {}

# Hanya mengisi built-in jika fox_engine tersedia
if FOX_ENGINE_AVAILABLE:
    FOX_BUILTINS = {
        "fox_simple": _create_fox_builtin('sfox'),
        "fox_mini": _create_fox_builtin('mfox'),
        "fox_thunder": _create_fox_builtin('tfox'),
        "fox_water": _create_fox_builtin('wfox'),
        "fox_auto": _create_fox_builtin('fox'),
        "_fox_cek_sumber_daya": _fox_cek_sumber_daya,
    }
else:
    # Mungkin log pesan bahwa fitur ini dinonaktifkan
    logging.getLogger(__name__).info("fox_engine tidak ditemukan, built-in terkait dinonaktifkan.")
    # Fallback mock untuk _fox_cek_sumber_daya agar kode Morph tidak crash
    FOX_BUILTINS["_fox_cek_sumber_daya"] = _fox_cek_sumber_daya
