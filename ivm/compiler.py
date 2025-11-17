# ivm/compiler.py
from typing import List, Any, Tuple
from .opcodes import OpCode
from .structs import CodeObject

class Compiler:
    def __init__(self):
        self.code_obj = CodeObject(name="<utama>")

    def compile(self, program: List[Tuple[OpCode, Any]]):
        """
        Mengkompilasi program sederhana yang direpresentasikan sebagai daftar tuple.
        Format Tuple: (OPCODE, argumen) atau (OPCODE, )
        """
        for instruction in program:
            opcode = instruction[0]
            self.code_obj.instructions.append(opcode)

            if len(instruction) > 1:
                arg = instruction[1]
                # Argumen bisa berupa nilai langsung (untuk konstanta) atau nama (untuk global)
                # Kita perlu mengubahnya menjadi indeks di dalam `constants pool`.
                if opcode in (OpCode.LOAD_CONST, OpCode.LOAD_GLOBAL):
                    arg_index = self._add_constant(arg)
                    self.code_obj.instructions.append(arg_index)
                else:
                    self.code_obj.instructions.append(arg)

        return self.code_obj

    def _add_constant(self, value: Any) -> int:
        """Menambahkan konstanta ke pool dan mengembalikan indeksnya."""
        if value not in self.code_obj.constants:
            self.code_obj.constants.append(value)
        return self.code_obj.constants.index(value)
