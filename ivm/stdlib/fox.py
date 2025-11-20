import asyncio
from fox_engine import api as fox_api
from ivm.vms import standard_vm  # To access get_current_vm

# Helper to run async functions from sync VM
def _run_sync(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If we are inside an async test runner, create a task and wait?
        # No, we are in sync code (VM.run).
        # This is tricky. For the prototype, we just raise error if loop is running
        # BUT user might be running via pytest-asyncio.
        # Let's try using a new thread if loop is running? Too complex.
        # For now, fail fast.
        # Actually, in test_fox_api.py we run pytest, which MIGHT capture loop.
        # StandardVM is synchronous.
        # asyncio.run() creates a NEW loop.
        return asyncio.run(coro)
    else:
        return asyncio.run(coro)

def _execute_morph_function(code_obj, args):
    """
    Executes a Morph CodeObject using the current running VM instance.
    """
    vm = standard_vm.get_current_vm()
    if vm is None:
        raise RuntimeError("Fox API called outside of a running StandardVM context.")
    return vm.call_function_sync(code_obj, args)

def builtins_fox_simple(args):
    if len(args) < 2:
        raise TypeError("fox.simple() butuh minimal nama dan fungsi")
    nama = args[0]
    func = args[1]
    extra_args = args[2:]

    async def _wrapper(*a, **kw):
        # Merge args
        all_args = list(a) + list(kw.values())

        if callable(func): # Python Callable (e.g. builtins)
            return func(all_args)
        else: # Morph CodeObject
            return _execute_morph_function(func, all_args)

    return _run_sync(fox_api.sfox(nama, _wrapper, *extra_args))

def builtins_fox_mini(args):
    if len(args) < 2:
        raise TypeError("fox.mini() butuh minimal nama dan fungsi")
    nama = args[0]
    func = args[1]
    extra_args = args[2:]

    async def _wrapper(*a, **kw):
        all_args = list(a) + list(kw.values())
        if callable(func):
            return func(all_args)
        else:
            return _execute_morph_function(func, all_args)

    return _run_sync(fox_api.mfox(nama, _wrapper, *extra_args))

def builtins_fox_thunder(args):
    if len(args) < 2:
        raise TypeError("fox.thunder() butuh minimal nama dan fungsi")
    nama = args[0]
    func = args[1]
    extra_args = args[2:]

    async def _wrapper(*a, **kw):
        all_args = list(a) + list(kw.values())
        if callable(func):
            return func(all_args)
        else:
            return _execute_morph_function(func, all_args)

    return _run_sync(fox_api.tfox(nama, _wrapper, *extra_args))

def builtins_fox_water(args):
    if len(args) < 2:
        raise TypeError("fox.water() butuh minimal nama dan fungsi")
    nama = args[0]
    func = args[1]
    extra_args = args[2:]

    async def _wrapper(*a, **kw):
        all_args = list(a) + list(kw.values())
        if callable(func):
            return func(all_args)
        else:
            return _execute_morph_function(func, all_args)

    return _run_sync(fox_api.wfox(nama, _wrapper, *extra_args))

def builtins_fox_auto(args):
    if len(args) < 2:
        raise TypeError("fox.auto() butuh minimal nama dan fungsi")
    nama = args[0]
    func = args[1]
    extra_args = args[2:]

    async def _wrapper(*a, **kw):
        all_args = list(a) + list(kw.values())
        if callable(func):
            return func(all_args)
        else:
            return _execute_morph_function(func, all_args)

    return _run_sync(fox_api.fox(nama, _wrapper, *extra_args))

FOX_BUILTINS = {
    "fox_simple": builtins_fox_simple,
    "fox_mini": builtins_fox_mini,
    "fox_thunder": builtins_fox_thunder,
    "fox_water": builtins_fox_water,
    "fox_auto": builtins_fox_auto,
}
