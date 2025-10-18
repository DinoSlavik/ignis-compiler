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

Note: Conceptually, this is just syntactic sugar for the standard conditional expression.

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

### The foreach loop

Conceptually, this is a wrapper around the for loop for iterating over collections and generators. 
This loop is currently planned to iterate strictly from the first to the last element, 
without the ability to specify an incrementor. 
This might be simplified by the potential introduction of slices.

_Not yet implemented._

It has the syntax `foreach (item(-s); collection) { [code] }`, where:
- `item(-s)` — one or more items (in the case of a collection of collections) corresponding to the current index;
- `collection` — a collection object or a suitable custom type;
- `[code]` — your code in the loop body.

Some examples:
```Ignis

// A loop that iterates over each element in a tuple
tuple int prime_numbers = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]

foreach (int num; prime_numbers) {
    print(num);
}

// Iterating over a collection, skipping all but the first, all but the last, and specific elements by index
// This is abstract code, as the creation of collection variables is not yet defined
tuple tuple int some_numbers = [[0, 1, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]] 

foreach (first, __; some_numbers) {
    print(first);
}

foreach (__, last; some_numbers) {
    print(last);
}

foreach (_, second, _; some_numbers) {
    print(second);
}
```

_Note: `_` skips a single element, while `__` skips all elements from its position until the next "selected" element (in these examples, first, second, last) or to the end if no other element is selected. If another `__` or `_` is encountered in the path of `__`, they are ignored, although this is undesirable syntax and will trigger a compiler warning._

### The forin loop

This is a more general version of the foreach loop, to which the same rules apply, except for the iteration method itself. 
For this reason, only the loop declaration is shown.

By default, the incrementor cannot implicitly go beyond the collection's size, 
but this behavior can be changed by passing a function rule.

_Not yet implemented._

It has the syntax `forin (index declaration; item(-s); collection; incremention rule) { [code] }`, where:
- `index declaration` — sets the initial index.
- `item(-s)` — one or more items corresponding to the current index.
- `collection` — a collection object or a suitable custom type.
- `incremention rule` — an expression describing the index step. Functions (that take an integer argument and return an integer) are also allowed.
- `[code]` — your code in the loop body.

Some examples:
```Ignis

// Classic and reverse iteration
forin (mut int i = 0; item1, item2; collection; i += 2) { ... }
forin (mut int i = -1; item1, item2; collection; i -= 2) { ... }
    
// Using a multi-line expression as a rule
forin (
    mut int i = 0; 
    item; collection;
    {
        if ( i % 2 == 0 ) { 2 * i }
        else { i - 3 }
    }
) { ... }
    
// Pre-declared index and using a function as a rule
int increment(int i) {
    return i + 1;
}
mut int i = 0;
    
forin (i; item; collection; increment(i)) { ... }
```

_Note: In some cases, it may be slightly slower than for and foreach, 
but for convenience and readability when iterating over collections, its use is recommended._

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