# Update Patch 9: Functions & Data Structures (WIP)

**Status:** In Progress
**Date:** 12/12/2025

## Deficiencies of Patch 8 (Identified)
Although Patch 8 introduced Arithmetic, Logic, Bitwise, and basic Control Flow, it lacks the essential components for general-purpose programming:
1.  **Call Stack Missing:** The VM runs a single flat code object. `RET` exits the VM. No `CALL` opcode support.
2.  **No Local Scope:** Variables are stored globally. Functions cannot have private variables or arguments.
3.  **Missing Data Ops:** While the deserializer supports Lists/Dicts, runtime operations (`BUILD_LIST`, `LOAD_INDEX`) are missing.
4.  **No Closures:** `MAKE_FUNCTION` and `LOAD_CLOSURE` are unimplemented.

## Goals for Patch 9
1.  **Implement Call Frames:** Refactor `VM` to use a stack of `CallFrame`s.
2.  **Function Support:** Implement `CALL` (47), `RET` (48), and `MAKE_FUNCTION` (68).
3.  **Data Structures:** Implement `BUILD_LIST` (27), `BUILD_DICT` (28), `LOAD_INDEX` (29), `STORE_INDEX` (30).
