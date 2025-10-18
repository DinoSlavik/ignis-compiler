# 00. Development Roadmap

This document describes the current state and future directions for the Ignis programming language and its compiler. The plan is divided into phases, each representing a significant step in expanding the language's features and stability.

## ✅ Phase 1: The Basics & MVP (Completed)

**Goal**: To create a Minimum Viable Product (MVP) capable of compiling the basic syntax of the language.

**Key Achievements**:
- Implemented compilation to C++.
- Basic types: `int`, `char`.
- Variables (`mut`/`immut`) and constants (`const`).
- Core operators: arithmetic, comparison, logical, bitwise.
- Basic control flow constructs: `if`/`else`, C-style `for`, `while`, `loop`.
- Support for structs (`struct`) and pointers (`ptr`, `addr`, `deref`).
- Expression-oriented blocks (`{...}`) and `if` statements.

**Also noteworthy**:
- Temporarily deferred direct compilation to ASM for simplicity.

## Phase 2: Self-Hosting

**Main Goal**: To enhance the language to the point where the Ignis compiler can be rewritten in Ignis itself.

Type System
- **Classes (`class`)**: A full-featured implementation of OOP:
  - Access modifiers: `public`, `private`, `protected`.
  - Methods with explicit `self` and separate implementation (`genimpl`, `impl Method in Class`).
  - Constructors (`new`) and destructors (`__del__`).
  - Static methods.
- **Traits (`trait`)**: Implementation of a behavior-as-contracts mechanism for polymorphism.
- **Collections**: Basic implementation of `tuple`, `array`, and `list` types.
- **Strings (`string`)**: Introduction of a dedicated type for working with text.

Memory Management
- **"The Warden and Keys"**: A complete implementation of the runtime system to prevent dangling pointers.
- Integration with the object lifecycle (calls to `new` and `__del__`).

Syntax and Features
- **`foreach` and `forin` loops**: Implementation of powerful loops for iterating over collections.
- **Generators (`yield`)**: A mechanism for creating lazy sequences.
- **Overloading**: Full support for function overloading by argument types and names.
- **Properties**: Basic implementation of bits<N> and `default`.

## Phase 3: Low-Level Control and Safety

**Main Goal**: To transition to direct assembly code generation and introduce a modern error-handling system.
- **ASM Code Generator**: A fully functional backend that generates assembly code (x86-64) as the primary compilation target.
- **Error System**: "Errors as types" system (similar to `Result<T, E>`).
- **`bool` Type**: Introduction of a boolean type to improve type safety.
- **Numeric Type Expansion**: Addition of `float`, `uint`, `nint`, and their derivatives.

## Phases 4-5: Expanding Unique Features

Main Goal: To implement complex and unique features that will define the character of the language.
- **Arbitrary Bit Width**: Full support for `bits<N>` for any `N`, including a software implementation of arithmetic for "long" numbers.
- **Numeral Systems (`nsys<base>`)**: The ability to work with numbers in different numeral systems.
- **Static Class Fields**.
- **Deepening the Properties System**: Adding `encoding`, `final`, and other properties.
- **A basic package manager and module system**.

## Phases 6-7: Ecosystem and the Future

**Main Goal**: To develop the ecosystem around the language and explore complex architectural concepts.
- **Modular Standard Library**: Splitting the standard library into independent, pluggable modules.
- **Concurrency and Asynchrony**: Language-integrated tools for multi-threaded programming.
- **Macros and Metaprogramming**.
- **Support for other architectures** (e.g., `ARM`).
- **Exploration of ternary logic** and the tern type.
- _If it exists by then, support for "Trysvit" technology_.