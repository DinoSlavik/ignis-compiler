# Ignis Compiler

---

[Українська версія](./README.md)

Ignis is a compiler for a statically-typed, compiled programming language being developed with a focus on safety, expressiveness, and control. The language combines the best ideas from C++, Rust, Python, and other languages, offering a unique hybrid approach to programming.

## 🌟 Philosophy and Key Features
- **Expression-Oriented**: Almost everything in Ignis is an expression that returns a value. `if` constructs and even entire code blocks `{...}` can be used to initialize variables, making the code concise and functional.
- **Safety and Explicitness**: The language is designed to avoid entire classes of errors. The planned elimination of `null`/`None` and `NaN` in favor of an "errors as types" system makes control flow more predictable.
- **Immutability by Default**: Variables are immutable unless declared with the special `mut` keyword. This significantly reduces the risk of accidental state changes.
- **Memory Control without `segfaults`**: The unique "Warden and Keys" dynamic memory management system combines manual control (`new`/`free`) with runtime checks that make "dangling pointer" errors impossible.
- **Flexible OOP System**: Classes in Ignis borrow the best from several languages: access modifiers from C++, explicit `self` and dunder methods from Python, and separate method implementation (`impl`) from Rust.
- **Powerful Function Overloading**: Functions can be overloaded not only by type but also by **argument names**, allowing for the creation of extremely readable APIs.

## 🛠️ Current Status

The project is currently in **Phase 2** of development. The main goal of this phase is to expand the language's capabilities to a level where the compiler can be rewritten in Ignis itself.

Read more about the plans in the [Development Roadmap](./docs/en/00_development_roadmap.md).

## 🚀 Getting Started

### Prerequisites
- Python 3.6+
- `g++` (for compiling via C++)

### Your First Program

Create a file `leet.ign`:
```Ignis

int main() {
    print(1337);
    return 0;
}
```

Compile and run it:
```Bash

    # Generating C++ code and compilation
    python3 ignis/main.py leet.ign --target cpp -o leet

    # Run
    ./leet
```

You should see `1337` in your terminal.

## 📚 Documentation

More detailed information about the language, its syntax, and concepts can be found in the [./docs](./docs) directory. We recommend starting there!