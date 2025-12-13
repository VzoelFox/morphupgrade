# Morph: Internal Knowledge Base for Agents

**Last Updated:** 2025 (Jules)
**Status:** Greenfield (Pivot Phase) - Patch 18 (Micro LLVM Strategy)

This document serves as the primary context source for AI Agents working on the Morph codebase. It distills architectural knowledge, known weaknesses, and development guidelines to ensure consistency and prevent regression.

## 1. Architecture Overview (NEW: Patch 18)

Morph is transitioning to a "Morph as Kernel" architecture.

### A. The Controller (`greenfield/kompiler`)
*   **Role:** The "Brain" (Orchestrator).
*   **Component:** Self-Hosted Compiler written in Morph.
*   **Goal:** Compile itself and control the lower layers.

### B. The Driver Layer (Micro LLVM / C++)
*   **Role:** Bootstrapping Hardware & Low-Level Execution.
*   **Status:** In Planning (Concept Phase).
*   **Concept:** A thin executable (C++/Rust/LLVM) that loads the Morph Kernel and exposes hardware primitives (CPU, RAM, GPU) to it.

### C. The Temporary Host (`ivm/`)
*   **Role:** Current Training Wheels.
*   **Runtime:** Python 3.
*   **Usage:** Used to develop and test the Self-Hosted Compiler until it is robust enough to run on the Micro Driver.

### D. The Artifacts (`Artefak/`)
*   **Role:** Documentation and specifications.
*   **Rule:** Always check `Artefak/Catatan_Self_Host.md` for the latest strategic direction.

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

### 💀 Host VM Scope Bug in Catch Blocks
*   **Description:** In the Host VM (`ivm`), global variables (including imported modules) might become inaccessible inside `tangkap` (catch) blocks.
*   **Mitigation:** Always capture necessary globals into local variables *before* entering a `coba` block.
    ```fox
    biar sys = sys_raw
    coba ... tangkap e ... sys.do_something() ... akhir
    ```

---

## 3. Usage & Workflow

### How to Build & Run
Do not use `python morph.py` directly. Use the bootstrap runner.

**1. Run a Morph Script (Source):**
```bash
python3 -m ivm.main path/to/script.fox
```

**2. Compile to Bytecode (.mvm) (Experimental):**
```bash
# Uses the self-hosted compiler to build a binary
python3 -m ivm.main greenfield/morph.fox build path/to/script.fox
```

**3. Run Bytecode:**
```bash
# VM automatically detects .mvm extension
python3 -m ivm.main greenfield/morph.fox run path/to/script.fox.mvm
```

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
*   `archived_morph/`: Read-only history. This now includes the old `morph_vm` (Rust VM).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.18 (Greenfield Patch 18 - Micro LLVM Pivot)
tanggal  : 12/12/2025
