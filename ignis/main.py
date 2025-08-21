import subprocess
import argparse
import sys
import traceback
from pathlib import Path

from lexer import Lexer
from parser import Parser
from checker import Checker
from codegen import CodeGenerator
from error import ErrorReporter


def compile_source(source_code, file_path, reporter):
    # 1. Lexer
    lexer = Lexer(source_code, reporter)
    # 2. Parser
    parser = Parser(lexer, reporter)
    ast = parser.parse()
    if reporter.had_error: return None
    # 2.5. Checker
    checker = Checker(reporter)
    checker.check(ast)
    if reporter.had_error: return None
    # 3. Code Generation
    generator = CodeGenerator(reporter)
    assembly_code = generator.generate(ast)
    return assembly_code


def main():
    arg_parser = argparse.ArgumentParser(prog="ignis", description="The Ignis language compiler.",
                                         epilog="Have fun building the future!")
    arg_parser.add_argument('input_file', type=str, help='The Ignis source file to compile')
    arg_parser.add_argument('-o', '--output', type=str, help='Specify the output file name')
    arg_parser.add_argument('-S', action='store_true', help='Stop after assembly generation')
    arg_parser.add_argument('-c', action='store_true', help='Stop after object file generation')
    arg_parser.add_argument('-k', '--keep-files', action='store_true', help='Keep intermediate files')
    args = arg_parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists(): print(f"Error: Input file not found at '{input_path}'"); sys.exit(1)

    if args.output:
        output_base_path = Path(args.output).resolve()
    else:
        output_base_path = input_path.resolve().with_suffix('')

    build_dir = output_base_path.parent / '.build' / output_base_path.stem
    build_dir.mkdir(exist_ok=True, parents=True)
    asm_file_path = build_dir / (output_base_path.name + '.asm')
    obj_file_path = build_dir / (output_base_path.name + '.o')
    executable_path = output_base_path

    print(f"--- Compiling {input_path} ---")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        reporter = ErrorReporter(str(input_path), source_code.split('\n'))
        assembly_code = compile_source(source_code, str(input_path), reporter)
        if reporter.had_error: sys.exit(1)

        with open(asm_file_path, 'w') as f:
            f.write(assembly_code)
        print(f"  [+] Assembly code saved to {asm_file_path}")
        if args.S: print("\n--- Compilation stopped after assembly generation (-S) ---"); sys.exit(0)

        print("--- Assembling with NASM ---")
        subprocess.run(['nasm', '-f', 'elf64', '-o', obj_file_path, asm_file_path], check=True)
        print(f"  [+] Object file saved to {obj_file_path}")
        if args.c: print("\n--- Compilation stopped after assembling (-c) ---"); sys.exit(0)

        print("--- Linking with LD ---")
        subprocess.run(['ld', '-o', executable_path, obj_file_path], check=True)
        print(f"  [+] Executable file saved to {executable_path}")
        print(f"\n--- Compilation successful! ---\nRun './{executable_path.name}' to see the result.")
    except FileNotFoundError:
        print("\nError: 'nasm' or 'ld' not found."); sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during an external command: {e}"); sys.exit(1)
    except Exception as e:
        if "Compiler error:" in str(e):
            print(f"\n{e}")
        else:
            # If it's an unexpected Python error, print the full traceback.
            print("\n--- An unexpected internal compiler error occurred ---")
            traceback.print_exc()
            print("------------------------------------------------------")
        sys.exit(1)
    finally:
        if not args.keep_files and not args.S and not args.c:
            print("--- Cleaning up intermediate files ---")
            try:
                if asm_file_path.exists(): asm_file_path.unlink()
                if obj_file_path.exists(): obj_file_path.unlink()
                if build_dir.exists() and not any(build_dir.iterdir()): build_dir.rmdir()
                print("  [+] Cleanup successful.")
            except OSError as e:
                print(f"  [!] Warning: Could not clean up all intermediate files: {e}")


if __name__ == '__main__':
    main()
