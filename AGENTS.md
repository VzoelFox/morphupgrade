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
    *   `cotc/`: **Core of the Core** (Standard Library).
        *   `stdlib/`: High-level modules (`teks`, `core`).
        *   `railwush/`: Network & Profile stack (Pure Morph replacement for old `netbase`).

### C. The Artifacts (`Artefak/`)
*   **Role:** Documentation and specifications.
*   **Rule:** These files are the "Spec". If code behaves differently, either the code is buggy or the spec is outdated. Always check `Artefak/Laporan_Kesiapan.md` for current feature parity status.

---

## 2. Critical Weaknesses & Fragilities

Be extremely cautious when touching these areas.

### 💀 Dispatcher Hell (`greenfield/kompiler/utama.fox`)
*   **Description:** The compiler uses a massive `if-else` chain to dispatch AST visitors based on string types.
*   **Risk:** O(N) performance and high risk of typos.
*   **Rule:** If you add a new AST node, you **must** add it to `_kunjungi` in `utama.fox` AND `analisis.fox`. Failing to do so results in silent failures or "Node belum didukung" logs without crashing, leading to corrupt bytecode.

### 💀 Implicit Globals & Scope Analysis (`greenfield/kompiler/analisis.fox`)
*   **Description:** The scope analyzer assumes any variable not found in the local stack is a Global.
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

### 💀 Railwush Relative Path Trap (`greenfield/cotc/railwush/cryptex.fox`)
*   **Description:** Railwush uses a relative path `railwush/checksum.dat` for token counters.
*   **Risk:**
    *   If executed from the repo root, it creates a `railwush/` directory in the root (polluting the repo).
    *   If executed from a different directory, it might fail to find the existing checksum in `greenfield/cotc/railwush/checksum.dat`, causing token collision or resets.
*   **CI/CD Impact:** Tests running from root will generate untracked files (`railwush/` or new `.mnet` files), causing "Dirty Repo" checks to fail in CI.

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
*   **Legacy Tests:** `run_ivm_tests.py` and `tests/` are largely deprecated/unstable.
*   **Recommended:** Create self-contained test scripts in `greenfield/examples/` or `greenfield/cotc/.../tes_*.fox` and run them using the CLI.

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
versi        : 0.1.0 (Greenfield Stabil)
tanggal  : 10/12/2025
