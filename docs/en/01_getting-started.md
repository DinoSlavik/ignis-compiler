# Getting Started with Ignis
Welcome to Ignis! This is a quick guide to help you compile and run your first program.

## 1. Prerequisites
To compile Ignis programs, you will need:

When using the C++ code generator:

- `Python 3.6+`

- `g++`

When using the assembly code generator (temporarily unavailable):

- `Python 3.6+`

- `NASM` (the assembler)

- `ld` (the linker)

**Ensure these tools are installed and available in your system's `PATH`.**

## 2. Installation and Running compiler
To get started, download the repository from GitHub. The compiler script is located at `ignis/main.py` within the downloaded repository.

## 3. Your First Program: Hello, World!
Create a file named `hello.ign` and add the following code to it:

```Ignis

// This is our first program
int main() {
    print(1337); // Print a number to the screen
    return 0;
}
```
## 4. Compiling and Running
Now, let's compile our file. Open a terminal in the project's root directory and run the following command:

```Bash

python3 ignis/main.py hello.ign -o hello
```
This command will:

Compile the `hello.ign` file.

Create an executable file named hello in the current directory.

After a successful compilation, run your program:

```Bash

./hello
```
You should see the following output in your terminal:

```
1337
```
Congratulations! You have just run your first program written in Ignis.

## 5. Compilation Targets
The Ignis compiler supports two compilation targets:

- `asm` (default): Generates NASM x86-64 Assembly code.

- `cpp`: Transpiles the code into C++.

You can specify the target using the `--target` flag:

```Bash

# Compile via C++
python3 ignis/main.py hello.ign --target cpp -o hello_cpp
```