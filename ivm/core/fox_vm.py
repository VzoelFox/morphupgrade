from ivm.vms.standard_vm import StandardVM
from ivm.core.structs import CodeObject

class FoxVM:
    """
    Coordinator for the Fox VM Ecosystem.
    Currently directs execution to the Standard VM.
    """
    def __init__(self):
        self.standard_vm = StandardVM()
        # Future: hot_vm, cold_vm, ipc here

    def run(self, code_or_instructions):
        """
        Loads and runs the instructions using the Standard VM.
        Inputs can be a list of instructions (for backward compatibility)
        or a CodeObject (the new standard).
        """
        if isinstance(code_or_instructions, CodeObject):
            # Unwrap instructions if needed, or better, pass CodeObject to load
            # But StandardVM.load expects instructions list and wraps them.
            # Let's adjust StandardVM to accept CodeObject or List.
            # For now, we extract instructions if it's a CodeObject.
            # WAIT: StandardVM.load creates a <main> frame.
            # If we pass a CodeObject (module), we should use it directly.
            self.standard_vm.load(code_or_instructions)
        else:
            # Legacy list of instructions
            self.standard_vm.load(code_or_instructions)

        self.standard_vm.run()
