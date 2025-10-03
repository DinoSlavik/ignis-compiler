# 9. Built-in Types

The Ignis type system provides a set of fundamental types for working with various kinds of data. A unique feature of numeric types is that their bit width (size in bits) is defined through the properties system, making it flexible and extensible.

**Current types**: `int` (as `bits64 int`), `char`.

**Planned types**: `string`, `float`, `ufloat`, `nfloat`, `bool`, `tern`, `uint`, `nint`, types for collections (`tuple`, `array`, `list`).

## Numeric Types and the Bit Width Property
Instead of a set of fixed-size types (like `int32`, `int64`, etc.), Ignis uses a combination of a **type** and a **bit width property**.

- **Type** (`int`, `float`, `uint`...): Defines the category and behavior of the number (signed, unsigned, floating-point).
- **Property `bits<N>`**: Defines the type's size (bit width) in bits. For example: `bits32`, `bits8`, `bits24`.

```Ignis

// Creating a 32-bit signed integer variable
bits32 int a = 10;

// A classic type without a property uses the default size (64 bits)
int b = 20; // equivalent to 'bits64 int b = 20;'
```

This approach allows for the creation of numeric types of any bit width, 
including standard (`64`, `32`, `16`, `8`, `4`, `2`) and non-standard (`24`, `48`) sizes.

### General Principles
- **Infinity (`infinity`)**: Each numeric type is planned to have its own representation of infinity.
- **Arithmetic**:
  - `number / 0` -> `infinity`
  - `number / infinity` -> `0`
- **Indeterminacy (NaN)**: The Ignis language **does not have a `NaN` value**. 
  Mathematically indeterminate operations (like `0/0` or `infinity - infinity`) 
  do not return a special value but instead generate a **runtime error** (e.g., `MathError::IndeterminateOperation`) that can be handled. 
  This makes the code safer and more explicit.

### Base Numeric Types
- **`int` (Signed Integers)**:
  - `bits64 int` (default): from `-2^63` to `2^63 - 1`.
- **`uint` (Unsigned Integers)**:
  - `bits64 uint` (default): from `0` to `2^64 - 1`.
- **`nint` (Natural Integers)**:
  - `bits64 nint` (default): from `1` to `2^64 - 1`.
  - It is an alias for `uint` with an additional check for non-zero values.
- **`float`, `ufloat`, `nfloat` (Floating-Point Numbers)**: Similar to integers, with a default bit width of `bits64`.

### Special Numeric Types
- **`char` (Character)**: Stores the numeric code of a character. 
  A property for encoding is planned: `utf8 char c`.
- **`bool` (Boolean)**: Stores `true` (`1`) or `false` (`0`). 
  Ideologically, it is an alias for `bits1 uint`. 
  Planned for phase 3 to enhance type safety.
- **`tern` (Ternary)**: An analogue of 'bool' for ternary logic.
  Planned for when support for ternary architectures is added.

## Collection Types
- `tuple`: A collection of **fixed** size with elements of the **same** type.
- `array`: A collection of **variable** size with elements of the **same** type.
- `list`: A collection of **variable** size with elements of **different** types.

## The 'string' Type
Is considered an independent, "base" type for working with text.

## (DEV) Handling Absence of Value: Errors as Types
In Ignis (planned for phase 3), there will be no `null` or `None`. The absence of a value will be handled through an **error-as-types system**:
- **Errors are types**: There will be a base `Error` type from which categories (`MathError`, `IOError`) and specific errors will inherit.
- **Functions return something like `Result<T, E>`**: A special container type that holds either a successful result `Ok(T)` or an error `Err(E)`.
- **Custom errors**: Programmers will be able to create their own errors, including their hierarchies.

## (DEV) Future Directions and Ideas
- **Modular Standard Library**: In the long term (phase 6+), the plan is to split the standard library into independent modules. This will allow users to include only the necessary functionality in their projects.
- **Complex Numbers**: As part of the modular math library, support for complex numbers will be added for scientific and engineering calculations.