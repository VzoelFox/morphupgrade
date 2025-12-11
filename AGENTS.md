# Morph: Internal Knowledge Base for Agents

**Last Updated:** 2025 (Jules)
**Status:** Greenfield (Self-Hosting Phase)

This document serves as the primary context source for AI Agents working on the Morph codebase. It distills architectural knowledge, known weaknesses, and development guidelines to ensure consistency and prevent regression.

## 1. Architecture Overview

Morph is a self-hosting language ecosystem. The architecture is split into three layers:

### A. The Host Layer (`ivm/`)
*   **Role:** Bootstrapping.
*   **Runtime:** Python 3.
*   **Components:** `ivm.main` (CLI runner), `ivm.vms` (Host VM wrapper).
*   **Note:** This layer exists to run the Self-Hosted Compiler (`greenfield/kompiler`) until the Native VM (`greenfield/fox_vm`) is fully mature and capable of running the compiler itself efficiently.

### B. The Greenfield Layer (`greenfield/`)
*   **Role:** The actual language implementation (Source of Truth).
*   **Components:**
    *   `kompiler/`: The self-hosted compiler. Transforms `.fox` source -> AST -> `.mvm` Bytecode.
    *   `fox_vm/`: The Native VM written in Morph. It executes `.mvm` bytecode.
    *   `morph_vm/`: The **Native VM** (Rust). Implements Loader and Basic Runtime (Stack Machine).
    *   `cotc/`: **Core of the Core** (Standard Library).
        *   `stdlib/`: High-level modules (`teks`, `core`, `kripto`).
        *   `railwush/`: **ARCHIVED** to `TODO/railwush_concept/`.

### C. The Artifacts (`Artefak/`)
*   **Role:** Documentation and specifications.
*   **Rule:** These files are the "Spec". If code behaves differently, either the code is buggy or the spec is outdated. Always check `Artefak/Laporan_Kesiapan.md` for current feature parity status.

---

## 2. Critical Weaknesses & Fragilities

Be extremely cautious when touching these areas.

### 💀 Implicit Globals & Scope Analysis (`greenfield/kompiler/analisis.fox`)
*   **Description:** The scope analyzer assumes any variable not found in the local stack is a Global or Universal (Builtin).
*   **Risk:** Typographical errors in variable usage (e.g., `count` vs `conut`) are NOT caught at compile time. They become runtime `LOAD_VAR` errors.
*   **Rule:** Double-check variable names manually.

### 💀 The "Jodohkan" Scope Trap
*   **Description:** Variables introduced in `jodohkan` (Pattern Matching) patterns might not be correctly registered in `defs` by the scope analyzer (missing `kunjungi_Jodohkan`).
*   **Risk:** Using a variable defined inside a match pattern within a closure (nested function) might fail to capture it as a "Cell Var", causing runtime errors.
*   **Mitigation:** Avoid capturing match variables in closures. Copy them to a distinct local variable first if needed.

### 💀 Native VM Interop (`greenfield/fox_vm/prosesor.fox`)
*   **Description:** The VM uses `ProxyHostGlobals` and complex `_ops_call` logic to bridge Morph objects and Python Host objects.
*   **Risk:** "Method not found" or "AttributeError" when mixing Morph types and Python types.
*   **Rule:** If extending the VM, ensure you handle both Native Morph Objects (Dicts/Structs) and Host Proxies.

### 💀 Error Handling "Panic" & Swallowed Errors
*   **Description:**
    1.  The Native VM handles unhandled exceptions by printing "Panic" and clearing the stack.
    2.  The Host Runner (`ivm/main.py`) has a `try-except` block that catches exceptions but silences the stack trace (prints nothing or just exit status 1).
*   **Risk:** No stack trace, hard to debug.
*   **Tip:** If `ivm` exits with status 1 and no output, it's likely a runtime crash (or import error) in the Morph code.

### 💀 Railwush Side-Effects & Token Consumption
*   **Description:** The Railwush module (`greenfield/cotc/railwush/cryptex.fox`) implements a "1 Profile 1 Token" policy.
*   **Status:** **ARCHIVED**.
*   **Change:** To prevent CI/CD failures due to "dirty git status", the entire Railwush module has been moved to `TODO/railwush_concept/`.
*   **Replacement:** Use `greenfield/cotc/stdlib/kripto.fox` for stateless crypto operations.

---

## 3. Usage & Workflow

### How to Build & Run
Do not use `python morph.py` directly. Use the bootstrap runner.

**1. Run a Morph Script (Source):**
```bash
python3 -m ivm.main path/to/script.fox
```

**2. Compile to Bytecode (.mvm):**
```bash
# Uses the self-hosted compiler to build a binary
python3 -m ivm.main greenfield/morph.fox build path/to/script.fox
```

**3. Run Bytecode:**
```bash
# VM automatically detects .mvm extension
python3 -m ivm.main greenfield/morph.fox run path/to/script.fox.mvm
```

### Railwush & .mnet Files
*   **Role:** Railwush manages user profiles stored as `.mnet` files.
*   **Format:** `SHA256(token).mnet`. Content is XOR-encrypted JSON encoded in Base64.
*   **Checksum:** `checksum.dat` maintains the account counter.
*   **Warning:** Be careful where you run scripts that invoke `cryptex.buat_token_baru()`. It writes to disk immediately.

### Testing
*   **Legacy Tests:** `tests/` folder has been archived to `archived_morph/legacy_tests/`. `run_ivm_tests.py` is archived.
*   **New Runner:** `python3 -m ivm.main greenfield/uji_semua.fox`.
*   **Method:** The runner uses the Self-Hosted Compiler to build and run tests found in `greenfield/examples/`.

### Universal Scope (New in Patch 2)
*   **Hierarchy:** `Universal (Builtins)` -> `Global (User)` -> `Local (Function)`.
*   **Behavior:** Builtins like `tulis`, `panjang` are effectively globals. User globals can shadow them. Local variables can shadow both.
*   **Compiler:** `analisis.fox` handles the resolution.

### Syscalls Architecture (New in Patch 5)
*   **Concept:** To reduce direct dependency on Python (`pinjam`), all system interactions (I/O, OS, Time) must go through `greenfield/cotc/sys/syscalls.fox`.
*   **Role:** `syscalls.fox` acts as the *only* allowed bridge to Host VM system functions.
*   **Future:** This layer will be replaced by Native Traps when migrating to a C/Rust VM.
*   **Rule:** Do not use `pinjam "os"` or `pinjam "builtins"` in standard library code (except in `syscalls.fox` itself). Import from `syscalls` instead.

---

## 4. Coding Standards

*   **Language:** Indonesian (`fungsi`, `jika`, `biar`, `tulis`).
*   **Indentation:** 4 Spaces.
*   **File Extension:** `.fox`.
*   **Imports:**
    *   Use `ambil_semua "path/file.fox" sebagai Alias` for namespaces.
    *   Use `dari "path/file.fox" ambil_sebagian a, b` for specific imports.
    *   **Circular Imports:** Avoid them at all costs. The import system is naive.

---

## 5. Directory "Do Not Touch" List
*   `transisi/`: Old bootstrap code. Do not edit unless fixing a bootstrap crasher.
*   `archived_morph/`: Read-only history.

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.9 (Greenfield Patch 9 - WIP)
tanggal  : 12/12/2025
