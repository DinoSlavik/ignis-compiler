# 3. Operators
Ignis provides a rich set of operators for arithmetic, logical, and bitwise operations, as well as for comparing values.

## Arithmetic Operators
These are the basic operators for mathematical calculations.

- `+` : Addition
- `-` : Subtraction
- `*` : Multiplication
- `/` : Division

```Ignis

int res_add = 20 + 10; // result = 30
int res_sub = 20 - 10; // result = 10
int res_mul = 20 * 10; // result = 200
int res_div = 20 / 10; // result = 2
```

_Note: The behavior of division by zero (`0`) is currently undefined and may result in a runtime error._

// TODO: Define the behavior for division by zero. Should it cause a panic, or return 0? inf, when added, will likely be available for all types that support it, including -inf for types that support negative values.

## Comparison Operators
Used to compare two values. The result is `1` (true) or `0` (false).

- `==` : Equal
- `!=` : Not Equal
- `<` : Less than
- `<=` : Less than or equal to
- `>` : Greater than
- `>=` : Greater than or equal to

```Ignis

print(20 == 10); // Prints 0
print(20 != 10); // Prints 1
print(20 < 10);  // Prints 0
print(10 <= 10); // Prints 1
print(20 > 10);  // Prints 1
print(15 >= 15); // Prints 1
```

## Logical Operators
These operators treat any non-zero number as "true" and `0` as "false". The result of a logical operation is always 1 or 0.

- `and` : Logical AND
- `or` : Logical OR
- `not` : Logical NOT (0 -> 1, non-zero -> 0)
- `xor` : Exclusive OR
- `nand`, `nor`, `xnor`: The inverted versions of their respective operators.
- `nnot`: Boolean Coercion. Converts any non-zero value to `1`, and `0` to `0`.

```Ignis

// Standard logical operators
print(1 and 0); // Prints 0
print(1 or 0);  // Prints 1
print(not 0);   // Prints 1
print(1 xor 1); // Prints 0

// Inverted logical operators
print(1 nand 0); // Prints 1
print(1 nor 1);  // Prints 0
print(1 xnor 1); // Prints 1

// The nnot operator
print(nnot 123); // Prints 1
print(nnot -123); // Prints 1
print(nnot 0);   // Prints 0
```

_Note: nnot was initially a joke, but has been repurposed into a useful feature for casting any value to a strict boolean (`1` or `0`)._

## Bitwise Operators
These operators perform manipulations at the level of individual bits of a number.

- `band` : Bitwise AND
- `bor` : Bitwise OR
- `bnot` : Bitwise NOT (inversion)
- `bxor` : Bitwise Exclusive OR
- `nband`, `nbor`, `nbxor`: The inverted versions.
- `nbnot`: Bitwise double negation (does not change the value).

```Ignis

// For simplicity, let's imagine we are working with 4-bit positive numbers.
// In practice, an 'int' is a 64-bit signed number.
// 5 is 0101, 3 is 0011

// Standard bitwise operators
print(5 band 3);  // Prints 1 (0001)
print(5 bor 3);   // Prints 7 (0111)
print(bnot 3);    // Prints 12 (1100)
print(5 bxor 3);  // Prints 6 (0110)

// Inverted bitwise operators
print(5 nband 3); // Prints 14 (1110)
print(5 nbor 3);  // Prints 8 (1000)
print(nbnot 3);   // Prints 3 (0011)
print(5 nbxor 3); // Prints 9 (1001)
```

_Note: nbnot is the bitwise analogue to nnot, with a similar history, but currently without happy end._

## Special Operators
- `=` : Assignment.
- `===` : Type Comparison. This is a compile-time operator that returns 1 if the types of the operands are identical, and 0 otherwise.

```Ignis

int a = 10;
// 'a' and the literal '20' both have the type 'int'
int result = a === 20;
print(result); // Prints 1

char b = 'Q';
// However, 'b' has the type 'char', which is different from 'a' ('int')
print(b === a); // Prints 0
```

// QUES: There's a nuance here. char is, de-facto, a special subtype of int. This raises a logical question: how should the === operator react to subtypes when compared with their parent types? Perhaps it performs a strict check, and we could add another operator, similar to Python's isinstance, which would check for type compatibility (i.e., is this type a subtype of another)? So, in this case, === would return 0 for 'char' === 'int', but a hypothetical is operator would return 1. This also brings up the question of how fair it is to design built-in types this way. For example, what would a string be, which is both a list and a list of char? Would it simultaneously be a list, a character, and an integer through this operator's logic? This needs to be decided. Also, the behavior of all these operators should be explicitly overridable, and I think I had some ideas on how to do that.

// TODO: Create an operator precedence table.
