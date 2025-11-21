from enum import Enum, auto

class Op(Enum):
    # === Stack Operations (Standard VM Core) ===
    PUSH_CONST = auto()  # (PUSH_CONST, value) -> Push constant to stack
    POP = auto()         # (POP,) -> Discard top of stack
    DUP = auto()         # (DUP,) -> Duplicate top of stack

    # Arithmetic (Stack-based)
    ADD = auto()         # (ADD,) -> Pop 2, push sum
    SUB = auto()         # (SUB,)
    MUL = auto()         # (MUL,)
    DIV = auto()         # (DIV,)
    MOD = auto()         # (MOD,)

    # Logic (Stack-based)
    EQ = auto()          # (EQ,) -> Pop 2, push (a == b)
    NEQ = auto()         # (NEQ,)
    GT = auto()          # (GT,)
    LT = auto()          # (LT,)
    GTE = auto()         # (GTE,)
    LTE = auto()         # (LTE,)
    NOT = auto()         # (NOT,)

    # === Register Operations (Optimization / Hot Path) ===
    # Registers are temporary slots, distinct from named variables
    LOAD_REG = auto()    # (LOAD_REG, reg_idx, value) -> regs[idx] = value
    MOVE_REG = auto()    # (MOVE_REG, dest_idx, src_idx)
    ADD_REG = auto()     # (ADD_REG, dest, src1, src2) -> regs[dest] = regs[src1] + regs[src2]

    # === Hybrid Bridge ===
    PUSH_FROM_REG = auto() # (PUSH_FROM_REG, reg_idx) -> Push regs[idx] to stack
    POP_TO_REG = auto()    # (POP_TO_REG, reg_idx)    -> Pop stack to regs[idx]

    # === Variable / Memory Access ===
    LOAD_VAR = auto()    # (LOAD_VAR, name) -> Push global variable value
    STORE_VAR = auto()   # (STORE_VAR, name) -> Pop value, store in global variable
    LOAD_LOCAL = auto()  # (LOAD_LOCAL, name) -> Push local variable value (Function scope)
    STORE_LOCAL = auto() # (STORE_LOCAL, name) -> Pop value, store in local variable (Function scope)

    # === Data Structures ===
    BUILD_LIST = auto()  # (BUILD_LIST, count) -> Pop N items, Push List
    BUILD_DICT = auto()  # (BUILD_DICT, count) -> Pop 2*N items, Push Dict
    LOAD_INDEX = auto()  # (LOAD_INDEX,) -> Pop index, Pop target, Push target[index]
    STORE_INDEX = auto() # (STORE_INDEX,) -> Pop value, Pop index, Pop target, Set target[index]=value

    # === Classes & Objects ===
    BUILD_CLASS = auto() # (BUILD_CLASS,) -> Pop methods dict, Pop name, Push Class
    LOAD_ATTR = auto()   # (LOAD_ATTR, name) -> Pop obj, Push obj.name (or bound method)
    STORE_ATTR = auto()  # (STORE_ATTR, name) -> Pop value, Pop obj, Set obj.name = value

    # === Control Flow ===
    JMP = auto()         # (JMP, target_pc) -> Unconditional jump
    JMP_IF_FALSE = auto() # (JMP_IF_FALSE, target_pc) -> Pop bool, jump if False
    JMP_IF_TRUE = auto()  # (JMP_IF_TRUE, target_pc)

    # === Functions ===
    CALL = auto()        # (CALL, arg_count) -> Pop func, Pop args, Push Frame
    RET = auto()         # (RET,) -> Pop return value, Pop Frame, Push to caller

    # === System / IO ===
    PRINT = auto()       # (PRINT, count) -> Pop N args and print
    HALT = auto()        # (HALT,) -> Stop execution

    def __repr__(self):
        return self.name
