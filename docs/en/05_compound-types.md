# 5. Compound Data Types: Structs and Pointers
Ignis provides two primary tools for creating your own complex data types: structs and classes. They allow you to group data and logic, while pointers provide flexible memory management for working with them.

## Structs

Structs are a simple and efficient way to group several variables (fields) into a single logical type. The main purpose of structs is to store data. They do not contain any associated logic (methods).

### Declaring and Using a Struct

A struct is declared using the struct keyword, followed by the type name and a block of fields. 
Fields are accessed using the `.` (dot) operator.

```Ignis

struct Point {
    int x;
    int y;
}

// Create a mutable variable of type Point
mut Point p;

// Assign values to its fields
p.x = 10;
p.y = 20;

print(p.x); // Prints 10
```

It's important to note that structs in Ignis are value types. This means that when you assign one struct variable to another, a full copy of the data is created.

## Classes

Unlike structs, classes allow you to encapsulate—combine into a single entity—both data (fields) and the logic to process that data (methods). They are the primary building block for object-oriented programming (OOP) in Ignis.

### Declaration

The syntax for declaring a class is similar to that of a struct but uses the class keyword and can include access modifiers (public, private).

```Ignis

// Preliminary syntax
class Player {
    public:
        ptr Vector2D position;
        char id;

    private:
        int health;
}
```

Note: A detailed description of class syntax, methods, inheritance, and other OOP concepts will be provided in the corresponding documentation section.

## Pointers (`ptr`)

Pointers are variables that store the memory address of another variable. They are a key tool for working efficiently with both structs and classes, allowing you to avoid the expensive copying of large objects.

The key operators for working with pointers are:

- `ptr`: Used to declare a pointer type (e.g., `ptr int` is a pointer to an `int`).

- `addr`: A unary operator that returns the memory address of a variable.

- `deref`: A unary operator that allows you to get or set the value that the pointer points to (dereferencing).

```Ignis

mut int x = 10;
mut ptr int p = addr x; // 'p' stores the address of 'x'
deref p = 42;           // Change the value of 'x' through the pointer
print(x);               // Prints 42
```

### Pointers and Field Access

Ignis simplifies working with pointers to structs and classes. The `.` (dot) operator works for both the objects themselves and pointers to them. The compiler automatically understands when to dereference the pointer.

```Ignis

// This function accepts a pointer to a Point
void move_point(ptr Point target, int dx) {
    // No need to write 'deref(target).x' or 'target->x'
    target.x = target.x + dx;
}
```

// TODO: When declaring the structure at the end, you probably need to add ‘`;`’. Although, on the other hand, without the semicolon, everything looks much cleaner.
