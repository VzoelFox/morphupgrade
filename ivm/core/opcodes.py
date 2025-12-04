from enum import IntEnum, auto

class Op(IntEnum):
    # === Stack Operations (Standard VM Core) ===
    PUSH_CONST = 1
    POP = 2
    DUP = 3

    # Arithmetic (Stack-based)
    ADD = 4
    SUB = 5
    MUL = 6
    DIV = 7
    MOD = 8

    # Logic (Stack-based)
    EQ = 9
    NEQ = 10
    GT = 11
    LT = 12
    GTE = 13
    LTE = 14
    NOT = 15
    AND = 16
    OR = 17

    # === Register Operations (Optimization / Hot Path) ===
    # Registers are temporary slots, distinct from named variables
    LOAD_REG = 18
    MOVE_REG = 19
    ADD_REG = 20

    # === Hybrid Bridge ===
    PUSH_FROM_REG = 21
    POP_TO_REG = 22

    # === Variable / Memory Access ===
    LOAD_VAR = 23
    STORE_VAR = 24
    LOAD_LOCAL = 25
    STORE_LOCAL = 26

    # === Data Structures ===
    BUILD_LIST = 27
    BUILD_DICT = 28
    LOAD_INDEX = 29
    STORE_INDEX = 30
    UNPACK_SEQUENCE = 31
    CHECK_LEN = 32
    CHECK_LEN_MIN = 33
    SNAPSHOT = 34
    RESTORE = 35
    DISCARD_SNAPSHOT = 36

    # === Classes & Objects ===
    BUILD_CLASS = 37
    LOAD_ATTR = 38
    STORE_ATTR = 39
    LOAD_SUPER_METHOD = 58 # New
    SLICE = 59 # New: Advanced String/List Slicing
    BUILD_FUNCTION = 60 # New: Create CodeObject from Dict (Self-Hosting Bridge)
    IS_INSTANCE = 40
    IS_VARIANT = 41
    UNPACK_VARIANT = 42
    BUILD_VARIANT = 43

    # === Control Flow ===
    JMP = 44
    JMP_IF_FALSE = 45
    JMP_IF_TRUE = 46

    # === Functions ===
    CALL = 47
    RET = 48

    # === Exception Handling ===
    PUSH_TRY = 49
    POP_TRY = 50
    THROW = 51

    # === Modules ===
    IMPORT = 52
    IMPORT_NATIVE = 61 # FFI: pinjam "python_module"
    LEN = 62
    TYPE = 63

    # === System / IO ===
    PRINT = 53
    PRINT_RAW = 54
    HALT = 55

    # === Flow Control (Coroutines/Infinity) ===
    YIELD = 56
    RESUME = 57

    def __repr__(self):
        return self.name
