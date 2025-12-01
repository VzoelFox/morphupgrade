# ivm/core/deserializer.py
import struct
from ivm.core.structs import CodeObject
from ivm.core.opcodes import Op

class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self):
        val = self.data[self.pos]
        self.pos += 1
        return val

    def read_int(self):
        val = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_float(self):
        val = struct.unpack_from("<d", self.data, self.pos)[0]
        self.pos += 8
        return val

    def read_string(self):
        length = self.read_int()
        val = self.data[self.pos : self.pos + length].decode("utf-8")
        self.pos += length
        return val

    def read_constant(self):
        tag = self.read_byte()
        if tag == 1: return None
        elif tag == 2: return bool(self.read_byte())
        elif tag == 3: return self.read_int()
        elif tag == 4: return self.read_float()
        elif tag == 5: return self.read_string()
        elif tag == 6: # List
            count = self.read_int()
            res = []
            for _ in range(count):
                res.append(self.read_constant())
            return res
        elif tag == 7: # CodeObject
            return self.read_code_object()
        elif tag == 8: # Dict
            count = self.read_int()
            res = {}
            for _ in range(count):
                k = self.read_constant()
                v = self.read_constant()
                res[k] = v
            return res
        else:
            raise ValueError(f"Unknown type tag: {tag}")

    def read_code_object(self, filename="<binary>"):
        # Tag already consumed by read_constant if called recursively
        # If top level, called directly.
        # But wait, structure.fox _tulis_code_object writes tag 7 first.
        # So we should expect tag 7 if called from top.

        # But here logic is inside `read_code_object` payload.
        # Let's assume tag is already handled or we are reading payload.
        # Re-check structure.fox:
        # `B.tulis_buffer(buf, B.pack_byte(7))` inside _tulis_code_object.
        # So yes, tag is there.

        # Name
        name = self.read_string()

        # Arg Count
        arg_count = self.read_byte()

        # Arg Names
        arg_names = []
        for _ in range(arg_count):
            arg_names.append(self.read_string())

        # Constants Pool
        consts_count = self.read_int()
        consts = []
        for _ in range(consts_count):
            consts.append(self.read_constant())

        # Instructions
        instr_count = self.read_int()
        instructions = []
        for _ in range(instr_count):
            op_val = self.read_byte()
            # Convert int to Op enum
            try:
                op = Op(op_val)
            except ValueError:
                # Fallback or unknown op handling
                op = op_val

            # Arg is stored as constant in V1
            arg = self.read_constant()

            instructions.append((op, arg))

        return CodeObject(name=name, instructions=instructions, arg_names=arg_names, filename=filename)

def deserialize_code_object(data: bytes, filename="<binary>") -> CodeObject:
    reader = BinaryReader(data)
    # Check top level tag
    tag = reader.read_byte()
    if tag != 7:
        raise ValueError("Root object must be CodeObject (Tag 7)")

    return reader.read_code_object(filename)
