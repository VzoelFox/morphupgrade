# Update Patch 8: Rust VM Arithmetic & Logic

**Status:** Completed
**Date:** 12/12/2025

## Changes
1.  **Rust VM (Native):**
    *   Implemented Arithmetic Opcodes: ADD, SUB, MUL, DIV, MOD.
    *   Implemented Logic Opcodes: EQ, NEQ, GT, LT, GTE, LTE, AND, OR, NOT.
    *   Implemented Control Flow: JMP, JMP_IF_TRUE, JMP_IF_FALSE.
    *   Implemented Bitwise Opcodes: BIT_AND, BIT_OR, BIT_XOR, BIT_NOT, LSHIFT, RSHIFT.
    *   Implemented Variable Opcodes: LOAD_VAR, STORE_VAR.
2.  **Repository Cleanup:**
    *   Removed `greenfield/morph_vm/target` artifact.
    *   Updated `.gitignore` to strictly exclude Rust build artifacts.
3.  **Parity:**
    *   Synced `IO_MKDIR` opcode in `greenfield/cotc/bytecode/opkode.fox`.

## Verification
*   Tests passing on Host VM.
*   Rust VM compiles and runs basic arithmetic tests.
