# MORPH Type Coercion Specification

## 1. Current Behavior (Problems)
- Boolean `truthy`/`falsy` values are not consistently applied in arithmetic operations versus boolean contexts. For example, `benar + 1` might be an error while `jika benar maka ...` is valid.
- The addition operator (`+`) is not defined for mixed `String` and `Number` types, leading to a `KesalahanTipe`.

## 2. Proposed Rules

### Arithmetic Operations (+, -, *, /, %, ^)
- **Number + Number**: Returns `Number`.
- **String + String**: Returns `String` (concatenation).
- **NEW: Number + String**: Throws a `KesalahanTipe`. Explicit casting will be required. This promotes code clarity and prevents unexpected behavior (e.g., `5 + "10"` resulting in `"510"`).
- **Other operators (-, *, /, %, ^)**: Will strictly operate on `Number` types. Any non-number operand will result in a `KesalahanTipe`.

### Boolean Context (`jika`, `selama`)
The following values are considered "falsy":
- `salah`
- `nil`
- `0` and `0.0`
- `""` (empty string)
- `[]` (empty list)
- `{}` (empty dictionary)

All other values are considered "truthy".

### Comparison Operators (==, !=, <, <=, >, >=)
- **Equality (==, !=)**: Will perform strict equality checks. No type coercion will be applied.
  - **NEW:** `0 == salah` will evaluate to `salah` because they are different types.
  - `1 == benar` will evaluate to `salah`.
  - `" " == salah` will evaluate to `salah`.
- **Relational (<, <=, >, >=)**: Will strictly operate on `Number` types. Comparing non-numbers will result in a `KesalahanTipe`.

## 3. Migration Plan
To help users adapt to these stricter rules, the following built-in functions will be introduced:
- `ke_angka(nilai)`: Converts a value to a `Number`. Can handle `String`, `Boolean` (`benar` -> 1, `salah` -> 0).
- `ke_teks(nilai)`: Converts a value to a `String`.
- `ke_boolean(nilai)`: Converts a value based on the truthiness rules defined above.

Error messages will be updated to be more helpful. For example, a `KesalahanTipe` on `5 + "10"` will suggest using `ke_teks(5) + "10"`.

## 4. Breaking Changes
- Any existing code that relies on implicit coercion between numbers and other types in arithmetic operations (if any were to be allowed) will break.
- Equality checks like `0 == salah` will change behavior from potentially `benar` to `salah`.
