# ivm/error_utils.py
import sys
from .structs import Frame

def format_error(error: Exception, vm_stack: list[Frame]) -> str:
    """Memformat error runtime VM menjadi string yang mudah dibaca."""
    lines = ["Kesalahan Runtime:", ""]

    for frame in reversed(vm_stack):
        offset = frame.ip - 1
        line = frame.code.line_map.get(offset, "baris tidak diketahui")
        lines.append(f"  -> File \"<unknown>\", baris {line}, di {frame.function_name}")

    error_type = type(error).__name__
    if hasattr(error, 'pesan'):
        error_message = error.pesan
    else:
        error_message = str(error)

    lines.append(f"{error_type}: {error_message}")
    return "\n".join(lines)
