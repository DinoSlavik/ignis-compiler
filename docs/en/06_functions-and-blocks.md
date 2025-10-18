# 6. Functions and Code Blocks
Functions are the primary way to organize and reuse code in Ignis. Additionally, the language supports expression blocks, which allow for the creation of complex value-returning expressions.

## Function Declaration
Functions are declared with a return type, a name, a list of parameters in parentheses, and a function body in curly braces {}.

```Ignis

// A function that takes two integers and returns their sum
int add(int a, int b) {
    a + b // The value of this expression will be returned
}
```

The entry point for any Ignis program is the main function, which must return an int.

### Implicit Return
Similar to if, a function body is an expression. If the last statement in a function body is an expression without a trailing semicolon `;`, its value is automatically returned from the function.

```Ignis

int get_version() {
    42 // No ';', so 42 is returned from the function
}
```

### The return Keyword
To explicitly return a value from any point within a function (e.g., for an early exit), use the `return` keyword.

```Ignis

int check_score(int score) {
    if (score < 0) {
        return -1; // Early exit with an error code
    }
    // ... further logic
    score
}
```

## Function Overloading

Ignis allows defining multiple functions with the same name but different parameters. This mechanism is called **overloading**. A unique feature of the language is that overloading is possible not only by argument types but also by their **names**.

This allows for the creation of APIs that are more semantically expressive and readable.

```Ignis

// Two versions of a function to set a position
// The first accepts Cartesian coordinates
set_position(int x, int y) { ... }

// The second, with the same types but different names, accepts polar coordinates
set_position(int r, int phi) { ... }
```

### Resolving Ambiguity

If the compiler can choose a function version based on types alone, it will do so automatically. However, if an ambiguity exists (as in the example above, where both functions accept `int`, `int`), the compiler will require the programmer to explicitly specify the argument names in the call.

```Ignis

mut Point my_point;

// Ambiguous call - Compile-time error!
// my_point.set_position(10, 20);

// Explicit call with named arguments - All good
my_point.set_position(x: 10, y: 20);
my_point.set_position(r: 5, phi: 90);
```

For library authors, a `default` **property** is planned, which will allow marking one of the ambiguous versions as the default to avoid breaking user code when new overloads are added.

## Expression Blocks
Any block of code enclosed in curly braces `{}` can be used as an expression. Such a block executes all statements within it, and its result is the value of the last expression in the block (the one not followed by a semicolon).

This is an extremely powerful tool for initializing variables with complex logic.

```Ignis

int main() {
    int y = {
        mut int z = 10 + 5; // z = 15
        z = z + 20;         // z = 35
        z                   // No ';', this value is returned from the block
    };
    print(y); // Should print 35

    // Implicit return from main
    0
}
```

## Built-in Functions
Ignis provides a small set of built-in functions for basic input/output operations.

- `print(int value)`: Prints a 64-bit integer followed by a newline. 

- `putchar(char value)`: Prints a single character to the output stream. 

- `getchar()`: Reads a single character from the input stream and returns it. 

