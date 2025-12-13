# Morph: Internal Knowledge Base for Agents

**Last Updated:** 2025 (Jules)
**Status:** Greenfield (Self-Hosting Phase) - Pivot to LLVM Strategy

This document serves as the primary context source for AI Agents working on the Morph codebase. It distills architectural knowledge, known weaknesses, and development guidelines to ensure consistency and prevent regression.

## 1. Architecture Overview

Morph is a self-hosting language ecosystem. The architecture is split into three layers:

### A. The Host Layer (`ivm/`)
*   **Role:** Bootstrapping & Primary Runtime (for now).
*   **Runtime:** Python 3.
*   **Components:** `ivm.main` (CLI runner), `ivm.vms` (Host VM wrapper).
*   **Note:** This layer exists to run the Self-Hosted Compiler (`greenfield/kompiler`) and serve as the reference implementation until the LLVM backend is ready.

### B. The Greenfield Layer (`greenfield/`)
*   **Role:** The actual language implementation (Source of Truth).
*   **Components:**
    *   `kompiler/`: The self-hosted compiler. Transforms `.fox` source -> AST -> `.mvm` Bytecode.
    *   `fox_vm/`: The Native VM written in Morph. It executes `.mvm` bytecode.
    *   `cotc/`: **Core of the Core** (Standard Library).
        *   `stdlib/`: High-level modules (`teks`, `core`, `kripto`).
        *   `jaringan/`: Networking stack (TCP, HTTP, WS).
        *   `lonewolf/`: Automated crash handling and recovery system.
        *   `pinjam/`: FFI wrappers for Host libraries (`psutil`, `trio`, `ssl`).
        *   `sys/`: System wrappers. `syscalls.fox` delegates to `_backend`.
        *   `railwush/`: **ARCHIVED** to `TODO/railwush_concept/`.

### C. The Artifacts (`Artefak/`)
*   **Role:** Documentation and specifications.
*   **Rule:** These files are the "Spec". If code behaves differently, either the code is buggy or the spec is outdated. Always check `Artefak/Laporan_Kesiapan.md` for current feature parity status.

### D. Archived Components
*   `morph_vm/` (Rust): **ARCHIVED** to `archived_morph/rust_vm_patch16_deprecated/`. The project has pivoted to generating LLVM IR directly from FoxVM rather than maintaining a custom Rust VM.

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

### 💀 Bytecode & Opcode Alignment
*   **Description:** Opcode values are strictly defined in `greenfield/cotc/bytecode/opkode.fox`.
*   **Critical:** There is a distinction between Logical Operators (15: NOT, 16: AND, 17: OR) and Bitwise Operators (69: BIT_AND, 70: BIT_OR, etc.). Mixing them up causes subtle calculation errors (e.g., producing 255 instead of 64).
*   **Rule:** Always verify opcode numbers against `opkode.fox` when implementing VMs.

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

**(Deprecated) Run with Rust VM:**
The Rust VM has been archived. Use the Python Host or wait for the LLVM backend implementation.

### Native Bytes Support
*   **Module:** `greenfield/cotc/bytes.fox` (Refactored in Patch 16).
*   **Backend:** Uses `sys_bytes_dari_list`, `sys_bytes_ke_list`, `sys_bytes_decode`, `sys_list_append`, `sys_list_pop`, `sys_str_join` from `_backend`.
*   **Types:** Host VM supports `Constant::Bytes`. Operations: `ADD`, `LOAD_INDEX`, `SLICE`, `LEN`, `IO_WRITE`.

### LoneWolf & Dumpbox
*   **Role:** Automated crash handling.
*   **Behavior:** If a process crashes, `vmdumpbox` saves the state to a `.z` file. `LoneWolf` can be used to wrap critical tasks (`lindungi`) and automatically retry them if the failure is transient (I/O).
*   **Files:** `greenfield/cotc/lonewolf/`, `greenfield/cotc/pairing/catch/`.

### Networking
*   **Module:** `greenfield/cotc/jaringan/`.
*   **Protocols:** TCP (`tcp.fox`), HTTP (`http.fox`), WebSocket (`websocket.fox`).
*   **Security:** SSL/TLS is supported via `pinjam/ssl.fox`.

### Syscalls & Bridge Architecture
*   **FoxVM Bridge (`greenfield/fox_vm/bridge_fox.fox`):** The new IPC/Handler layer. It wraps raw syscalls with Type Validation and centralized Error Handling.
*   **Role:** All high-level modules should use `bridge_fox` or `_backend` (for low-level bytes) instead of calling `syscalls.fox` directly if possible (though `bytes.fox` calls `_backend` directly).
*   **Rule:** Prefer `bridge_fox` for safety.

### Class Initialization
*   **Behavior:** When `CALL`ing a Class to instantiate it, the VM checks for an `inisiasi` method.
*   **Logic:** If found, `inisiasi(instance, args...)` is called. The VM ensures the `instance` is returned to the stack after initialization completes.

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
versi        : 0.1.17 (Greenfield - LLVM Pivot)
tanggal  : 12/12/2025
