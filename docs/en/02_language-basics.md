# 2. Language Basics
In this section, we will cover the basic building blocks of the Ignis language: comments, variables, constants, and basic data types.

## Comments
Ignis supports two kinds of comments, similar to C++ or C#:

Single-line comments start with `//` and extend to the end of the line.

Multi-line comments start with `/*` and end with `*/`. They can span multiple lines.

```Ignis

// This is a single-line comment

/*
  And this is
  a multi-line one.
*/
int main() {
    return 0;
}
```
## Variables
Variables in Ignis are immutable by default. This means that once a value is assigned, it cannot be changed.

```Ignis

int a = 10;
a = 20; // Compile error! 'a' is not mutable.
```
To create a variable whose value can be changed, use the `mut` keyword.

### Mutable Variables
The `mut` keyword makes a variable mutable.

```Ignis

// 'result' can be changed throughout its lifetime
mut int result = 100;
result = result + 42; // This is fine
print(result);
```
## Constants
Constants are declared using the `const` keyword. Their value is set at compile-time and can never be changed.

```Ignis

const int VERSION = 1;

int main() {
    // VERSION = 2; // Compile error!
    return 0;
}
```
## Basic Data Types
Ignis currently supports two fundamental data types.

- `int`: A 64-bit signed integer (`int64_t` when compiling to C++).

- `char`: An 8-bit character (corresponds to `char` in C++).

```Ignis

int year = 2025;
char initial = 'I';
```
The language also supports string literals, which are interpreted as pointers to a null-terminated array of characters (`ptr char`).