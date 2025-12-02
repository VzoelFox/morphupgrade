# ivm/stdlib/loader.py
import sys
from ivm.vm_context import get_current_vm
from ivm.core.deserializer import deserialize_code_object
from ivm.core.structs import Frame, CodeObject, MorphFunction

def jalan_biner(data: bytes):
    """
    Executes Morph binary data within the current VM context.
    Acts like a synchronous function call.
    """
    vm = get_current_vm()
    if not vm:
        raise RuntimeError("Loader FFI called without active VM.")

    # Validate Header
    if len(data) < 16 or data[:10] != b"VZOEL FOXS":
         # Fallback: maybe raw code object payload?
         # Or treat as error
         raise ValueError("Invalid Morph Binary Format.")

    payload = data[16:]
    code_obj = deserialize_code_object(payload, filename="<binary_run>")

    # Prepare execution
    module_globals = {}

    from ivm.stdlib.core import CORE_BUILTINS
    from ivm.stdlib.file_io import FILE_IO_BUILTINS
    from ivm.stdlib.sistem import SYSTEM_BUILTINS
    from ivm.stdlib.fox import FOX_BUILTINS

    module_globals.update(CORE_BUILTINS)
    module_globals.update(FILE_IO_BUILTINS)
    module_globals.update(SYSTEM_BUILTINS)
    module_globals.update(FOX_BUILTINS)

    # Inject argumen_sistem
    if "argumen_sistem" in vm.globals:
        module_globals["argumen_sistem"] = vm.globals["argumen_sistem"]

    # Save current state
    saved_globals = vm.globals
    saved_handlers = list(vm.current_frame.exception_handlers) if vm.call_stack else []

    # Save running state
    previous_running = vm.running

    vm.globals = module_globals
    vm.running = True

    try:
        # Push Frame
        frame = Frame(code=code_obj, globals=module_globals)
        vm.call_stack.append(frame)

        # Execute Synchronously (Sub-loop)
        start_depth = len(vm.call_stack)
        while len(vm.call_stack) >= start_depth and vm.running:
            if vm.instruction_count >= vm.max_instructions:
                raise RuntimeError("Instruction limit exceeded")

            curr = vm.current_frame
            # Check EOF
            if curr.pc >= len(curr.code.instructions):
                vm._return_from_frame(None)
                continue

            instr = curr.code.instructions[curr.pc]
            curr.pc += 1

            try:
                vm.execute(instr)
            except Exception as e:
                # Wrap error
                err = {
                    "pesan": str(e),
                    "jenis": "ErrorRuntime",
                    "sumber": "<binary>"
                }
                vm._handle_exception(err)

            vm.instruction_count += 1

        # Module body executed. Check for 'utama' function.
        if "utama" in module_globals:
            utama = module_globals["utama"]

            # Run utama()
            vm.call_function_internal(utama, [])

            # Ensure running is True (in case module body execution turned it off somehow)
            vm.running = True

            # Run sub-loop for utama
            start_depth = len(vm.call_stack)

            while len(vm.call_stack) >= start_depth and vm.running:
                if vm.instruction_count >= vm.max_instructions:
                    raise RuntimeError("Instruction limit exceeded")

                curr = vm.current_frame

                if curr.pc >= len(curr.code.instructions):
                    vm._return_from_frame(None)
                    continue

                instr = curr.code.instructions[curr.pc]
                curr.pc += 1
                try:
                    vm.execute(instr)
                except Exception as e:
                     err = {
                        "pesan": str(e),
                        "jenis": "ErrorRuntime",
                        "sumber": "<binary:utama>"
                    }
                     vm._handle_exception(err)

                vm.instruction_count += 1

        # Execution finished.
        if vm.call_stack:
             caller_frame = vm.call_stack[-1]
             if "utama" in module_globals:
                 if caller_frame.stack:
                     caller_frame.stack.pop()

    finally:
        vm.globals = saved_globals
        vm.running = previous_running
        if vm.call_stack:
            vm.current_frame.exception_handlers = saved_handlers

    return None
