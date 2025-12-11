# Update Patch 9: Functions & Data Structures (Stable Foundation)

**Status:** Completed (Foundation Layer)
**Date:** 12/12/2025

## Deficiencies of Patch 8 (Identified & Fixed)
1.  **Call Stack Missing:** Fixed. VM now uses `Vec<CallFrame>`.
2.  **No Local Scope:** Fixed. Functions have private `locals`. Global variables are accessible via `STORE_VAR` (Root Scope).
3.  **Missing Data Ops:** Fixed. `BUILD_LIST`, `BUILD_DICT`, `LOAD_INDEX`, `STORE_INDEX` are fully implemented.
    *   **Refactor:** `Constant` enum now uses `Rc<RefCell<>>` for Lists and Dicts, enabling mutability (`list[0] = 1`).
4.  **No Closures:** Deferred to Patch 10. `MAKE_FUNCTION` creates simple functions.

## Delivered Features (Patch 9)
1.  **Function Support:** `CALL` (47) and `RET` (48) working with arguments and return values.
2.  **Data Structures:** Full support for Mutable Lists and Dictionaries.
3.  **Built-ins:** Injected `tulis` (print) and `teks` (str) into VM Globals for basic I/O without Standard Library.
4.  **RPC Safety:** Added `target/` to `.gitignore`.

## Next Steps (Patch 10)
1.  **Closures:** Implement `LOAD_CLOSURE`, `LOAD_DEREF`, `STORE_DEREF`.
2.  **Self-Hosting:** Verify Compiler runs on Rust VM (Requires Closures).
