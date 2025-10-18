# 8. Properties

Properties are a fundamental concept in Ignis that define the characteristics and behavior of various language entities, such as variables, functions, literals, etc. This system allows for flexible control over aspects of the code, particularly its mutability, bit width, and representation.

_Note: The full implementation of the Properties system is planned for future development phases of the compiler._

## What are Properties?

Properties are, in essence, keyword modifiers that are applied to entities. They precede the type or the entity itself.

### Defined and Basic Properties

-   **Type (`int`, `char`, etc.)**: A mandatory property for variables and functions that defines the data type. It has a fixed position: right before the name (for variables and functions) or the entity (for literals).

-   **Mutability (`mut` and `immut`)**:
    -   `mut`: Makes a variable mutable (its value can be changed).
    -   `immut`: The default property. Makes a variable immutable. This keyword is usually omitted.

### Planned Properties

-   **Bit Width (`bits<N>`)**:
    -   Applies to numeric types (`int`, `float`, etc.) to define their size in bits.
    -   **Example**: `bits32 int a;`

-   **Encoding (`utf8`, `ascii`, etc.)**:
    -   Applies to the `char` type (and, by extension, to `string`) to specify how its numeric code should be interpreted.
    -   **Example**: `utf8 char c = 'я';`

-   **Numeral System (`nsys<base>`)**:
    -   Applies to numeric types to specify the numeral system in which to store and process values. For systems with a base > 10, literals are written in backticks.
    -   **Example**: `nsys16 int hex_val = 'FF';`
- Default Behavior (`default`):

    - Applies to functions and methods.

    - Instructs the compiler on which of several overloaded versions of a function to use if a call is ambiguous and does not contain named arguments.

    - Example: `default int my_func(int x, int y) { ... }`

### Dynamic Property Modification

One of the unique features of Ignis is the ability to temporarily change a variable's properties on the fly using the special syntax `(<property>) <variable>;`.

This construct acts as a toggle, enabling or disabling a specific property for the variable within its scope. This is particularly useful for mutability.

```Ignis

// 'a' is created as immutable (immut)
int a = 10;

// Temporarily enable the 'mut' property for 'a'
(mut) a;

// Now we can modify 'a'
while (a > 5) {
    a = a - 1;
}

// Disable the 'mut' property, reverting 'a' to its 'immut' state
(immut) a;

// Attempting to modify 'a' here would result in a compile-time error
// a = 10; // Error: attempt to modify an immutable variable
```

**Important**: Not all properties will be dynamically modifiable. For example, changing the **type**, or  **bit width** of a variable after its creation will not be possible.

