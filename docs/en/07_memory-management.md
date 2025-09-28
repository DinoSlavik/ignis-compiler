# 7. Dynamic Memory Management: "The Warden and Keys"
Memory management in Ignis is built on a unique hybrid model. It combines explicit control over the object lifecycle, as seen in C++, with runtime safety guarantees inspired by Rust. The goal is to eliminate dangerous errors like dangling pointers while leaving the programmer in control of memory.

## Philosophy: The Warden and Keys
The system is based on a simple analogy:

- **The "Warden" (Runtime)**: A single entity that owns all dynamically allocated memory (the "building"). It keeps a detailed log of all objects (the "apartments") and references to them (the "keys").

- **Variables ("Keys")**: Variables that point to objects in memory are "keys". They do not own the data but merely provide access to it.

## Core Principles
### 1. Object Creation and Destruction
The programmer has full control over when to create and destroy objects in dynamic memory (the heap).

- **Creation (`new`)**: The new operator (syntax to be defined) instructs the "Warden" to allocate memory for a new object. The "Warden" creates the object and issues the first "key" to the programmer.

- **Destruction (`free`)**: The free operator instructs the "Warden" to destroy the object and invalidate all keys associated with it.

```Ignis

// Syntax is hypothetical
// 1. The "Warden" creates a Point object and gives us the key `p1`.
mut Point p1 = new Point;

// ... work with the object ...

// 2. We command the "Warden" to destroy the object.
free(p1);
```

Important: If free is not called, the memory will remain occupied until the end of the program. This can lead to memory leaks.

### 2. Variables as "Keys"
Assigning variables that point to heap objects does not copy the object. Instead, it creates a new "key" (a reference) to the very same object.

```Ignis

mut Point p1 = new Point;

// The "Warden" creates a new key `p2` that leads to the same object.
// No copy is made.
Point p2 = p1;
```

### 3. Key Types and Permissions
There are two types of "keys," which determine access rights to an object:

- **Owner Key**: The first variable to which a newly created object is assigned. This key has full read and write permissions.

- **Guest Key**: Any key created through a simple assignment (p2 = p1). By default, it has read-only permission.

A special property (e.g., permall) will be introduced to create a new key with full write permissions.

Safety Guarantees (Runtime Checks)
The "Warden" ensures safety by checking all operations on keys during program execution.

## Preventing Dangling Pointers
This is a core feature of the system. When the programmer calls `free(p1)`:

1) The "Warden" finds the object p1 points to.

2) It consults its log and finds all other keys (p2, p3...) that point to this object.

3) It invalidates all of these keys.

4) Only then does it release the memory.

Any subsequent attempt to use an invalidated key (p2) will result in a controlled runtime error (e.g., "Attempt to access by invalid reference"), rather than undefined behavior or a program crash.
