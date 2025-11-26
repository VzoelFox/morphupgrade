# ivm/vm_context.py
# Provides a thread-safe way to get the currently executing VM instance.

_CURRENT_VM = None

def get_current_vm():
    """Returns the VM instance currently running on this thread."""
    return _CURRENT_VM

def set_current_vm(vm):
    """Sets the current VM instance. Should only be called by the VM itself."""
    global _CURRENT_VM
    _CURRENT_VM = vm
