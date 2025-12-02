# ivm/stdlib/loader.py
import sys
from ivm.vm_context import get_current_vm
from ivm.core.deserializer import deserialize_code_object
from ivm.core.structs import Frame, CodeObject, MorphFunction

def jalan_biner(data: bytes, args: list = None):
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
    if args is not None:
        module_globals["argumen_sistem"] = args
    elif "argumen_sistem" in vm.globals:
        module_globals["argumen_sistem"] = vm.globals["argumen_sistem"]

    # Save current state
    saved_globals = vm.globals
    saved_handlers = list(vm.current_frame.exception_handlers) if vm.call_stack else []

    # Save running state
    previous_running = vm.running

    vm.globals = module_globals
    vm.running = True

    final_result = None
    module_success = False

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
                module_success = True # Marked as success
                continue

            instr = curr.code.instructions[curr.pc]
            curr.pc += 1

            try:
                vm.execute(instr)
            except Exception as e:
                # Handle VM exceptions (including Panic)
                # Ensure the exception is propagated properly if it wasn't caught inside
                err = {
                    "pesan": str(e),
                    "jenis": "ErrorRuntime",
                    "sumber": "<binary>"
                }
                vm._handle_exception(err)

                # If _handle_exception raises (Panic), this try-except will catch it again?
                # No, _handle_exception raises RuntimeError.
                # We want to let that RuntimeError propagate to the caller of jalan_biner.
                # But here we are inside try...except Exception.
                # So we must re-raise.
                raise

            vm.instruction_count += 1

        # Module body executed.

        # Check success status (handle RET opcode case)
        if not module_success:
             curr_len = len(vm.call_stack)
             # If stack matches start_depth - 1 (returned to caller)
             if curr_len == start_depth - 1:
                 module_success = True

        if not module_success:
            raise RuntimeError("Binary Execution Failed (Module Body Crashed)")

        # Clean up module return value (only if successful)
        if vm.call_stack:
             caller_frame = vm.call_stack[-1]
             if caller_frame.stack:
                 caller_frame.stack.pop()

        # Check for 'utama' function.
        if "utama" in module_globals:
            utama = module_globals["utama"]

            # Run utama()
            vm.call_function_internal(utama, [])

            # Ensure running is True
            vm.running = True

            # Run sub-loop for utama
            start_depth = len(vm.call_stack)

            # Flag for utama
            utama_success = False

            while len(vm.call_stack) >= start_depth and vm.running:
                if vm.instruction_count >= vm.max_instructions:
                    raise RuntimeError("Instruction limit exceeded")

                curr = vm.current_frame

                if curr.pc >= len(curr.code.instructions):
                    vm._return_from_frame(None)
                    utama_success = True
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
                     raise

                vm.instruction_count += 1

            # Check success status for utama (handle RET opcode case)
            if not utama_success:
                 curr_len = len(vm.call_stack)
                 if curr_len == start_depth - 1:
                     utama_success = True

            if utama_success:
                # Execution of utama finished successfully.
                # Capture result.
                if vm.call_stack:
                     caller_frame = vm.call_stack[-1]
                     if caller_frame.stack:
                         final_result = caller_frame.stack.pop()
            else:
                # Utama crashed.
                raise RuntimeError("Binary Execution Failed (Utama Crashed)")

    finally:
        vm.globals = saved_globals
        vm.running = previous_running
        if vm.call_stack:
            vm.current_frame.exception_handlers = saved_handlers

    return final_result
