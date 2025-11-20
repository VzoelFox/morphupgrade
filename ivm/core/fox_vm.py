from ivm.vms.standard_vm import StandardVM

class FoxVM:
    """
    Coordinator for the Fox VM Ecosystem.
    Currently directs execution to the Standard VM.
    """
    def __init__(self):
        self.standard_vm = StandardVM()
        # Future: hot_vm, cold_vm, ipc here

    def run(self, instructions):
        """
        Loads and runs the instructions using the Standard VM.
        In the future, this method will decide which VM to use based on the platform/profile.
        """
        self.standard_vm.load(instructions)
        self.standard_vm.run()
