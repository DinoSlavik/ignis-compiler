# 10. Object-Oriented Programming

Object-Oriented Programming (OOP) in Ignis is a powerful paradigm that allows combining data and the logic that processes it into a single entity called a class. Unlike structs, which are simple data aggregates, classes are the primary tool for encapsulation, inheritance, and polymorphism.

## Classes (`class`)

A class is a blueprint for creating objects. It describes a set of fields (data) and methods (functions) that belong to that object.

### Class Declaration

A class is declared using the `class` keyword. The body of the class can contain sections with access modifiers borrowed from C++:

- `public`: Fields and methods accessible from anywhere.
- `private`: Fields and methods accessible only within the class itself.
- `protected`: Fields and methods accessible within the class and its descendants (to be discussed in the topic of inheritance).

```Ignis

// Hypothetical syntax
class Player {
    public:
        char id;

    private:
        int health;
        int mana;
}
```

### Methods

Methods are functions that belong to a class and operate on its data. Their implementation in Ignis is inspired by Rust and Python.

#### Explicit self

Similar to Python, the first argument of every instance method is an explicit reference to the object itself. 
By convention, it is named `self`, but it can be any name. 
Its name is determined in the first declared method, which, by convention, 
is the constructor (`new`).

#### Method Implementation (impl)

The implementation of methods is separated from the class declaration, which, as in Rust, makes the code more organized. This is done using genimpl and impl blocks.
- `genimpl ClassName { ... }`: A block for implementing simple, non-overloaded methods.
- `impl MethodName in ClassName { ... }`: A specialized block for implementing a specific method. It is ideal for grouping all its overloaded versions.


```Ignis

class Vector2D {
    public:
        int x;
        int y;
}

// General implementation
genimpl Vector2D {
    // Constructor (initializer)
    void new(ptr Vector2D self, int start_x, int start_y) {
        self.x = start_x;
        self.y = start_y;
    }

    // --- STATIC METHOD ---
    // This method does not take 'self' because it does not operate on a specific
    // instance, but creates a new one from a template.
    ptr Vector2D zero() {
        // It uses the public constructor new()
        return new Vector2D(0, 0);
    }

    // Instance method
    int length_sqr(ptr Vector2D self) {
        return self.x * self.x + self.y * self.y;
    }
}

// Implementation of the overloaded 'add' method
impl add in Vector2D {
    // 1. Adding another vector
    void add(ptr Vector2D self, ptr Vector2D other) {
        self.x = self.x + other.x;
        self.y = self.y + other.y;
    }

    // 2. Adding a scalar value
    void add(ptr Vector2D self, int scalar) {
        self.x = self.x + scalar;
        self.y = self.y + scalar;
    }
}
```

### Object Lifecycle

Managing the creation and destruction of objects is explicit and integrated with the "Warden" system. Ignis uses special dunder methods for initializing and finalizing objects.

#### Creation and Initialization (new and ::new())

Object creation is a two-step process controlled by the new operator, which works similarly to constructors in Python:
- `new ClassName(...)`: The `new` operator commands the "Warden" to allocate memory for a new, empty object.
- `::new(...)`: Immediately after memory allocation, the special initializer method `::new()` is automatically called on this object. Its job is to populate the object's fields with initial values.

The `::new` method does not return a value. Its sole purpose is to configure `self`.

```Ignis

class Vector2D {
    public:
        int x;
        int y;
}

genimpl Vector2D {
    // Initializer method (constructor)
    void new(ptr Vector2D self, int start_x, int start_y) {
        self.x = start_x;
        self.y = start_y;
    }
}

// The 'new' operator creates the object and implicitly calls new
mut ptr Vector2D my_vector = new Vector2D(10, 20);
print(my_vector.x); // Prints 10
```

This approach combines explicit memory management (`new`) with automated initialization (`::new`), making the object creation process both controlled and convenient. The naming might be slightly confusing at first, but it is intended to blur the line between object creation and initialization for the end-user (the programmer).

#### Object Destruction (Destructors)

When an object is destroyed using the `free` operator, its destructor is automatically called before the memory is deallocated. By convention, this is the dunder method `__del__`. This gives the object an opportunity to release any resources it owns.

```Ignis

genimpl Vector2D {
    // Destructor
    void __del__(ptr Vector2D self) {
        // Cleanup logic, if needed
        print_string("Vector2D destroyed!");
    }
}

// ...
free(my_vector); // Will call __del__ before freeing the memory
```

### Dunder Methods

To integrate with the language's operators (e.g., `+`, `==`, `===`), special **dunder methods** (from "double underscore") are used, as in Python. They are always public.
- `__add__(self, other)`: for the `+` operator.
- `__eq__(self, other)`: for the `==` operator.
- `__eqt__(self, other)`: for the `===` operator.
- and others.

This allows objects to behave like built-in types.

// TODO: Protected and private methods.

// TODO: Create a complete list of dunder methods and place it here.