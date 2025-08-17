import subprocess
import argparse
import sys
import os
from pathlib import Path

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator


def compile_source(source_code, file_path):
    """
    Runs the source code through all stages of the compiler.
    """
    # 1. Lexer now knows the file path
    lexer = Lexer(source_code, file_path)

    # 2. Parser now gets the full source code to build context for errors
    parser = Parser(lexer, source_code)
    ast = parser.parse()

    # 3. Code Generation
    generator = CodeGenerator()
    assembly_code = generator.generate(ast)

    return assembly_code


def main():
    # --- Argument Parsing Setup ---
    arg_parser = argparse.ArgumentParser(
        prog="ignis",
        description="The Ignis language compiler.",
        epilog="Have fun building the future!"
    )

    arg_parser.add_argument(
        'input_file',
        type=str,
        help='The Ignis source file to compile (e.g., ../examples/test.ign)'
    )
    arg_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Specify the output file name. Defaults to the input file name without extension.'
    )
    arg_parser.add_argument(
        '-S',
        action='store_true',
        help='Stop after the compilation stage; do not assemble. (Generates a .asm file)'
    )
    arg_parser.add_argument(
        '-c',
        action='store_true',
        help='Stop after the assembling stage; do not link. (Generates a .o file)'
    )
    arg_parser.add_argument(
        '-k', '--keep-files',
        action='store_true',
        help='Keep intermediate files (.asm, .o) after compilation.'
    )

    args = arg_parser.parse_args()

    # --- File Handling ---
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found at '{input_path}'")
        sys.exit(1)

    if args.output:
        output_base_path = Path(args.output).resolve()
    else:
        output_base_path = input_path.resolve().with_suffix('')

    build_dir = output_base_path.parent / '.build'
    build_dir.mkdir(exist_ok=True)

    asm_file_path = build_dir / (output_base_path.name + '.asm')
    obj_file_path = build_dir / (output_base_path.name + '.o')
    executable_path = output_base_path

    # --- Compilation Pipeline ---
    print(f"--- Compiling {input_path} ---")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        assembly_code = compile_source(source_code, str(input_path))

        with open(asm_file_path, 'w') as f:
            f.write(assembly_code)
        print(f"  [+] Assembly code saved to {asm_file_path}")

        if args.S:
            print("\n--- Compilation stopped after assembly generation (-S) ---")
            sys.exit(0)

        print("--- Assembling with NASM ---")
        subprocess.run(['nasm', '-f', 'elf64', '-o', obj_file_path, asm_file_path], check=True)
        print(f"  [+] Object file saved to {obj_file_path}")

        if args.c:
            print("\n--- Compilation stopped after assembling (-c) ---")
            sys.exit(0)

        print("--- Linking with LD ---")
        subprocess.run(['ld', '-o', executable_path, obj_file_path], check=True)
        print(f"  [+] Executable file saved to {executable_path}")

        print(f"\n--- Compilation successful! ---\nRun './{executable_path.name}' to see the result.")

    except FileNotFoundError:
        print("\nError: 'nasm' or 'ld' not found. Please ensure they are in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during an external command: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during compilation:\n{e}")
        sys.exit(1)
    finally:
        if not args.keep_files and not args.S and not args.c:
            print("--- Cleaning up intermediate files ---")
            try:
                if asm_file_path.exists():
                    asm_file_path.unlink()
                if obj_file_path.exists():
                    obj_file_path.unlink()
                if build_dir.exists() and not any(build_dir.iterdir()):
                    build_dir.rmdir()
                print("  [+] Cleanup successful.")
            except OSError as e:
                print(f"  [!] Warning: Could not clean up all intermediate files: {e}")


if __name__ == '__main__':
    main()
