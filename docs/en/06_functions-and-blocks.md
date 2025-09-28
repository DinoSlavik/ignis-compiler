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

