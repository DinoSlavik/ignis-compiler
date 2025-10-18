# 12. Iterators and Generators

For efficient processing of data sequences, especially very large or infinite ones, Ignis provides two powerful mechanisms: generators and the iteration protocol. They allow for the implementation of "lazy" computations, where each subsequent element of a sequence is generated only when it is actually needed.

## The Problem: "Eager" Collections

Traditional collections, such as arrays, store all their elements in memory at once. This is simple and convenient for small amounts of data. However, if we need a sequence of a million Fibonacci numbers, storing it all in memory is inefficient or even impossible.

## Generators: On-the-Fly Value Factories

The easiest way to create a "lazy" sequence in Ignis is to write a **generator function**. This is a special function that can "pause" its execution and "yield" a value to the caller, then resume its work from the same spot.

### The yield Keyword

Instead of `return`, generators use the `yield` keyword.
- `yield <value>`: Pauses the function's execution, returns the `<value>` to the caller (e.g., a `foreach` loop), and saves its current state.
- On the next call, the generator resumes execution from the line following the `yield`. When there are no more `yield` statements in the generator, the sequence is considered complete.

#### Example: Fibonacci Number Generator

Instead of storing a million numbers in an array, we can write a generator that calculates them "on the fly" without using extra memory.

```Ignis

// This function is a generator because it uses 'yield'.
// It returns a special generator object.
ptr Generator fibonacci(int limit) {
    mut int a = 0;
    mut int b = 1;

    while (a < limit) {
        yield a; // 1. Yield the current value and "sleep"
        mut int temp = a;
        a = b;
        b = temp + b;
    }
}
```

## Iteration Protocol and Loops

For an object to be iterable in a loop, it must support the corresponding protocol, implemented via dunder methods.

### The `foreach` loop and `__next__`

The simple `foreach` loop is designed for sequential iteration over elements. It works with any object that has a `__next__` method. Generator functions automatically return such an object.

Under the hood, the `foreach` loop simply calls `__next__()` repeatedly until the generator finishes its work.

```Ignis

int main() {
    // The foreach loop works with the generator, getting values one by one
    foreach (num, fibonacci(100)) {
        print(num); // Prints: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
    }
    return 0;
}
```

### The `forin` loop and `__idx__`

The more complex `forin` loop is designed for iteration with index control. It works with collections that support element access by index via the `__idx__` dunder method and `__len__` to determine the size.

```Ignis

// This loop will work with arrays and other indexed collections
forin (mut int i = 0; my_array; item; i = i + 1) {
    // ... loop body ...
}
```

// QUES: An alternative approach to iteration could be based on traits rather than dunder methods. For example, an Iterable trait with a next() method could be defined. Any class or generator that implements this trait could be used in loops. This would make the iteration system more formalized and extensible, but might require more complex types, such as `Option<T>`, to signify the end of a sequence. This idea is worth considering for future versions of the language.