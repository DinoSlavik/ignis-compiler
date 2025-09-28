# 5. Compound Data Types: Structs and Pointers
Ignis allows you to create more complex data structures using struct and to manage memory directly using pointers.

## Structs
Structs allow you to group multiple variables (fields) into a single logical data type. They are the primary tool for creating your own custom types.

### Declaring a Struct
A struct is declared using the struct keyword, followed by the type name and a block of fields in curly braces.

```Ignis

struct Point {
    int x;
    int y;
}
```

### Creation and Usage
After declaring a struct, you can create instances (variables) of it and work with its fields using the . (dot) operator.

```Ignis

// Create a mutable variable of type Point
mut Point p;

// Assign values to its fields
p.x = 10;
p.y = 20;

print(p.x); // Prints 10
```

It is important to note that structs in Ignis are value types. This means that when you assign one struct variable to another, a full copy of the data is created.

## Pointers (ptr)
Pointers are variables that store the memory address of another variable. They allow for indirect access and modification of data.

The key operators for working with pointers are:

- `ptr`: Used to declare a pointer type (e.g., `ptr int` is a pointer to an `int`).

- `addr`: A unary operator that returns the memory address of a variable.

- `deref`: A unary operator that allows you to get or set the value that the pointer points to (dereferencing).

```Ignis

mut int x = 10;

// 'p' is a pointer that holds the address of 'x'
mut ptr int p = addr x;

// Dereference the pointer to read the value of 'x'
print(deref p); // Prints 10

// Dereference to change the value of 'x' through the pointer
deref p = 42;

print(x); // Prints 42, because 'p' pointed to 'x'
```

### Pointers and Structs
Pointers are especially useful when working with structs, as they allow you to pass references to large objects into functions, avoiding expensive copying.

Accessing Fields via a Pointer
Ignis simplifies working with pointers to structs. Unlike in C/C++, you do not need a special operator (like ->). The . (dot) operator works for both struct values and pointers to them. The compiler automatically understands when to dereference the pointer.

```Ignis

struct GameObject {
    ptr Vector2D position;
    char id;
}

// This function accepts a pointer to a GameObject
void move_game_object(ptr GameObject obj, int dx, int dy) {
    // Accessing fields through a pointer looks the same
    // as direct access. The compiler handles the '->' logic implicitly.
    obj.position.x = obj.position.x + dx;
    obj.position.y = obj.position.y + dy;
}
```

// TODO: When declaring the structure at the end, you probably need to add ‘;’. Although, on the other hand, without the semicolon, everything looks much cleaner.
