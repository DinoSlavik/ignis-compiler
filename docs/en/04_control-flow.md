# 4. Control Flow
Ignis provides flexible tools for controlling the execution flow of your program, including conditional constructs and various loops.

## Conditional Constructs if-elif-else
A key feature of Ignis is that the `if` construct can be used both as a statement to perform actions and as an expression that returns a value.

### Using if as an Expression
When used as an expression, `if` always returns a value. The code block corresponding to the condition that evaluates to true will return the value of its last expression.

```Ignis

int a = 10;
int b = 20;

// 'if' is used to determine the value of the 'max_val' variable
int max_val = if (a > b) {
    a // 'a' is returned
} else {
    b // 'b' is returned
};

print(max_val); // Prints 20
```

The `if` construct can include `elif` (`else if`) to check multiple conditions sequentially.

```Ignis

int score = 85;
int grade = if (score >= 90) {
    5
} elif (score >= 80) {
    4
} else {
    3
};
print(grade); // Prints 4
```

### Using if as a Statement
When the return value of an `if` construct is not assigned to a variable, it works like a traditional statement, simply executing the code within the appropriate block.

```Ignis

mut int a = 25;
if (a > 20) {
    print(a); // if is used to perform an action, the return value is ignored
}
```

### Ternary-like Expression
Ignis also supports a more compact syntax for simple conditions, similar to the ternary operator in other languages.

```Ignis

int score = 85;
// Syntax: <value_if_true> if <condition> else <value_if_false>
int is_passing = 1 if score >= 60 else 0;
print(is_passing); // Prints 1
```

Note: Ideologically, this is just syntactic sugar for the standard conditional expression.

## Loops
The language provides three types of loops for different scenarios.

### The for loop
Ignis uses a C-style syntax for the `for` loop, which consists of an initializer, a condition, and an increment.

```Ignis

// A loop from 0 to 4 inclusive
for (mut int i = 0; i < 5; i = i + 1) {
    print(i);
}
```

### The while loop
The `while` loop executes a block of code as long as its condition remains true.

```Ignis

mut int i = 0;
while (i < 5) {
    print(i);
    i = i + 1;
}
```

### The loop statement
The `loop` statement creates an infinite loop. Exiting such a loop is typically done using the `break` keyword.

```Ignis

mut int i = 0;
loop {
    i = i + 1;
    print(i);
    if (i >= 5) {
        break; // Exit the loop
    }
}
```

### Loop Control: break and continue
- `break`: Immediately terminates the execution of the current loop (`for`, `while`, `loop`).

- `continue`: Skips the rest of the current iteration and proceeds to the next one.

// QUES: Should we add a separate forin loop for iterating over array elements? Something like "forin (\<iterator\>, \<incrementor\>, \<object to iterate\>, \<optional limit (or maybe rules?) for iterator\>) {}" instead of a "for item in array" construct?