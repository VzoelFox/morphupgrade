# Morph: Internal Knowledge Base for Agents

**Last Updated:** 2025 (Jules)
**Status:** Greenfield (Self-Hosting Phase) - Patch 18 (Micro LLVM Strategy)

This document serves as the primary context source for AI Agents working on the Morph codebase. It distills architectural knowledge, known weaknesses, and development guidelines to ensure consistency and prevent regression.

## 1. Architecture Overview (NEW: Patch 18)

Morph is transitioning to a "Morph as Kernel" architecture.

### A. The CLI (`morph`)
*   **Role:** The primary entry point for users.
*   **Path:** `./morph` (Compiled from `greenfield/micro_llvm_driver/`).
*   **Capabilities:**
    *   **Native VM:** Can execute `.mvm` bytecode directly using C++ Runtime (no Python needed for execution!).
    *   **Compiler Shim:** Delegates to Python IVM for *compilation* (source -> bytecode) until the native VM is feature-complete.
*   **Usage:** `morph run morph make "file.fox"`

### B. The Controller (`greenfield/kompiler`)
*   **Role:** The "Brain" (Orchestrator).
*   **Component:** Self-Hosted Compiler written in Morph.
*   **Goal:** Compile itself and control the lower layers.

### C. The Driver Layer (Micro LLVM / C++)
*   **Role:** Bootstrapping Hardware & Low-Level Execution.
*   **Location:** `greenfield/micro_llvm_driver/`.
*   **Components:**
    *   `main.cpp`: CLI Argument Parser.
    *   `fox_vm.cpp`: **Native C++ Bytecode Interpreter**.

### D. The Temporary Host (`ivm/`)
*   **Role:** Current Training Wheels (Compiler Only).
*   **Runtime:** Python 3.
*   **Usage:** Used implicitly by the `morph` driver shim only to *compile* code. Execution is now Native.

---

## 2. Critical Weaknesses & Fragilities

Be extremely cautious when touching these areas.

### 💀 Implicit Globals & Scope Analysis (`greenfield/kompiler/analisis.fox`)
*   **Description:** The scope analyzer assumes any variable not found in the local stack is a Global or Universal (Builtin).
*   **Risk:** Typographical errors in variable usage (e.g., `count` vs `conut`) are NOT caught at compile time. They become runtime `LOAD_VAR` errors.
*   **Rule:** Double-check variable names manually.

### 💀 The "Jodohkan" Scope Trap
*   **Description:** Variables introduced in `jodohkan` (Pattern Matching) patterns might not be correctly registered in `defs` by the scope analyzer.
*   **Mitigation:** Avoid capturing match variables in closures. Copy them to a distinct local variable first if needed.

---

## 3. Usage & Workflow

### How to Build & Run (The New Way)

**1. Compile the Driver:**
```bash
cd greenfield/micro_llvm_driver && make
# Binary output is at repo root: ./morph
```

**2. Run Morph Code:**
```bash
./morph run morph make "path/to/script.fox"
```
*   If input is `.fox`: Auto-compiles (via Python) then runs (via C++).
*   If input is `.mvm`: Runs directly (via C++).

**3. Install Packages (Stub):**
```bash
./morph install "star spawn package.fall"
```

---

## 4. Coding Standards

*   **Language:** Indonesian (`fungsi`, `jika`, `biar`, `tulis`).
*   **Indentation:** 4 Spaces.
*   **File Extension:** `.fox`.
*   **C++ Driver:** Standard C++17, use `g++` for stability.

---

## 5. Directory "Do Not Touch" List
*   `transisi/`: Old bootstrap code. Do not edit unless fixing a bootstrap crasher.
*   `archived_morph/`: Read-only history. This now includes the old `morph_vm` (Rust VM).

---
Founder : Vzoel Fox's ( Lutpan )
Engineer : Jules AI agent
versi        : 0.1.18 (Greenfield Patch 18 - Micro LLVM Pivot)
tanggal  : 12/12/2025
