# Update Patch 10: Closures (The Final Link)

**Status:** Completed
**Date:** 12/12/2025

## Overview
Patch 10 implements the most complex feature of the Morph Runtime: **Closures**. This enables functions to capture variables from their surrounding scope ("upvalues") and persist them, a critical requirement for functional programming patterns and the Morph Compiler itself.

## Delivered Features
1.  **Closure Opcodes:**
    *   `LOAD_CLOSURE` (67): Loads a "Cell" from the local scope (or parent closure) onto the stack.
    *   `MAKE_FUNCTION` (68): Creates a `Function` object combining `CodeObject` and captured `Closure` cells.
    *   `LOAD_DEREF` (65) / `STORE_DEREF` (66): Accesses the value inside a captured `Cell`.
2.  **Runtime Support:**
    *   **Function Object:** Native `Function` struct holding `CodeObject` + `Closure` (List of Cells).
    *   **Enhanced Call:** `CALL` opcode now binds `free_vars` to the new frame's locals using the closure cells, effectively "flattening" scope access.
    *   **Cell Variables:** `LOAD_VAR` and `LOAD_LOCAL` now automatically dereference `Cell` objects, making the transition between "captured" and "local" seamless.
3.  **Metadata Extraction:**
    *   `BUILD_FUNCTION` was updated to extract `free_vars` and `cell_vars` lists from the compiler-generated dictionary, solving the missing metadata issue in the binary format.

## Verification
- **Test:** `greenfield/examples/uji_closure_rust.fox`
- **Result:** Successfully captures and modifies a counter variable across multiple function calls.

## Significance
With Closures implemented, the Rust Native VM now supports all core language features required to run the Self-Hosted Compiler. The next phase is **Self-Hosting Verification**.
