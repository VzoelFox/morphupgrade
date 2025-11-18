# ivm/opcodes.py
from enum import IntEnum

class OpCode(IntEnum):
    # === Stack Manipulation ===
    LOAD_CONST = 1      # Push constant from constants pool
    LOAD_FAST = 2       # Push local variable
    STORE_FAST = 3      # Pop to local variable
    LOAD_GLOBAL = 4     # Push global variable
    STORE_GLOBAL = 5    # Pop to global variable
    POP_TOP = 6         # Discard top of stack
    DUP_TOP = 7         # Duplicate top of stack

    # === Arithmetic ===
    ADD = 10            # a + b
    SUBTRACT = 11       # a - b
    MULTIPLY = 12       # a * b
    DIVIDE = 13         # a / b
    MODULO = 14         # a % b
    POWER = 15          # a ^ b
    NEGATE = 16         # -a

    # === Comparison ===
    EQUAL = 20          # a == b
    NOT_EQUAL = 21      # a != b
    LESS_THAN = 22      # a < b
    LESS_EQUAL = 23     # a <= b
    GREATER_THAN = 24   # a > b
    GREATER_EQUAL = 25  # a >= b

    # === Logical ===
    AND = 30            # a dan b
    OR = 31             # a atau b
    NOT = 32            # tidak a

    # === Control Flow ===
    JUMP = 40           # Unconditional jump to an address
    JUMP_IF_FALSE = 41  # Jump if top of stack is false
    JUMP_IF_TRUE = 42   # Jump if top of stack is true

    # === Function Calls ===
    CALL_FUNCTION = 50  # Call a function with N args
    RETURN_VALUE = 51   # Return from function
    BUILD_FUNCTION = 52 # Create a function object from a CodeObject

    # === Data Structures ===
    BUILD_LIST = 60     # Create list from N items on stack
    BUILD_DICT = 61     # Create dict from 2N items on stack
    LOAD_INDEX = 62     # list[index]
    STORE_INDEX = 63    # list[index] = value

    # === Objects / Classes ===
    LOAD_ATTR = 70      # obj.attr
    STORE_ATTR = 71     # obj.attr = value
    BUILD_CLASS = 72    # Create a class object
    LOAD_SUPER_METHOD = 73 # Load a method from a superclass

    # === Pattern Matching (for future use) ===
    MATCH_VARIANT = 80
    MATCH_LIST = 81

    # === Modules ===
    IMPORT_MODULE = 85
    EXPORT_VALUE = 86

    # === Built-in Replacements (temporary) ===
    PRINT = 90          # Built-in print
    INPUT = 91          # Built-in input
