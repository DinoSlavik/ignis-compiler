# 8. Properties
Properties are a fundamental concept in Ignis that define the characteristics and behavior of various language entities, such as variables, functions, literals, etc. This system allows for flexible control over aspects of the code, most notably its mutability.

_Note: The full implementation of the Properties system is planned for future development phases of the compiler._

## What are Properties?
Properties are essentially keyword modifiers that are applied to entities. Currently, the following properties are defined:

- **Type (`int`, `char`, etc.)**: A mandatory property for variables and functions that defines the data type. It has a fixed position: right before the name (for variables and functions) or the entity (for literals).

- **Mutability (mut and immut)**:

  - `mut`: Makes a variable mutable (its value can be changed).

  - `immut`: The default property. Makes a variable immutable. This keyword is usually omitted.

In the future, the plan is to expand this system so that properties can be applied to a wider range of entities, including user-defined types.

## Dynamic Property Modification
One of the unique features of Ignis is the ability to temporarily change a variable's properties on the fly using the special syntax `(<property>) <variable>;`.

This construct acts as a toggle, enabling or disabling a specific property for the variable within its scope. This is particularly useful when you need to grant modification permission only for a specific operation.

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

**Important**: Not all properties will be dynamically modifiable. For example, changing the type of a variable after its creation will not be possible.

## (DEV) Possible Future Properties
Future updates are considering the introduction of a feature to create numeric variables of arbitrary numeral systems using a special property `nsys<base>`, where `<base>` is the number representing the number of digits (written without angle brackets, e.g., `nsys10` for decimal).

By default, the decimal system is used, and the use of others is situational and niche.

Potential losses in the context of number representation are almost non-existent, especially when it comes to displaying numbers with higher-order bases.

Potential compile-time performance costs depend mainly on the checker and, given its desired overall complexity, should amount to a tenth or even less of the total time.