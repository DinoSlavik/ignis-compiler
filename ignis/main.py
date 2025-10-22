import subprocess
import argparse
import sys
import traceback
from pathlib import Path

from lexer import Lexer
from parser import Parser
from checker import Checker
from error import ErrorReporter


# ### MODIFIED ###: Умовний імпорт кодогенераторів
# Ми будемо імпортувати потрібний клас залежно від аргументів

def compile_source(source_code, file_path, reporter, target):
    # 1. Lexer
    lexer = Lexer(source_code, reporter)
    # 2. Parser
    parser = Parser(lexer, reporter)
    ast = parser.parse()
    if reporter.had_error: return None
    # 2.5. Checker
    checker = Checker(reporter)
    checker.check(ast)
    # if reporter.had_error: return None

    # ### MODIFIED ###: Вибір кодогенератора
    # 3. Code Generation
    if target == 'asm':
        from codegen import CodeGenerator
        generator = CodeGenerator(reporter)
    elif target == 'cpp':
        from codegen_cpp import CodeGeneratorCpp
        generator = CodeGeneratorCpp(reporter)
    else:
        # Ця помилка не повинна ніколи виникнути, якщо argparse налаштовано правильно
        print(f"Error: Unknown compilation target '{target}'")
        sys.exit(1)

    generated_code = generator.generate(ast)
    return generated_code


def main():
    arg_parser = argparse.ArgumentParser(prog="ignis", description="The Ignis language compiler.",
                                         epilog="Have fun building the future!")
    arg_parser.add_argument('input_file', type=str, help='The Ignis source file to compile')
    arg_parser.add_argument('-o', '--output', type=str, help='Specify the output file name')
    arg_parser.add_argument('--target', type=str, choices=['asm', 'cpp'], default='asm',
                            help="Specify the compilation target: 'asm' (default) or 'cpp'")
    arg_parser.add_argument('-S', action='store_true', help="Stop after assembly generation (only for 'asm' target)")
    arg_parser.add_argument('-c', action='store_true', help="Stop after object file generation (only for 'asm' target)")
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

    # ### NEW ###: Визначаємо шляхи до файлів рантайму
    # Припускаємо, що рантайм-файли лежать в тій же директорії, що і компілятор
    script_dir = Path(__file__).parent.resolve()
    runtime_cpp_path = script_dir / 'cpp_runtime' / 'ignis_runtime.cpp'
    if args.target == 'cpp' and not runtime_cpp_path.exists():
        print(f"Error: Runtime file not found at '{runtime_cpp_path}'")
        sys.exit(1)

    # ### MODIFIED ###: Назви проміжних файлів тепер залежать від цілі
    if args.target == 'asm':
        intermediate_ext = '.asm'
        object_ext = '.o'
    else:  # cpp
        intermediate_ext = '.cpp'
        object_ext = '.o'  # g++ також створює .o файли

    intermediate_file_path = build_dir / (output_base_path.name + intermediate_ext)
    obj_file_path = build_dir / (output_base_path.name + object_ext)
    executable_path = output_base_path

    print(f"--- Compiling {input_path} (Target: {args.target.upper()}) ---")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        reporter = ErrorReporter(str(input_path), source_code.split('\n'))
        generated_code = compile_source(source_code, str(input_path), reporter, args.target)
        if reporter.had_error:
            print(f"\nCompilation failed due to previous errors.", file=sys.stderr)
            sys.exit(1)

        with open(intermediate_file_path, 'w') as f:
            f.write(generated_code)
        print(f"  [+] Intermediate code saved to {intermediate_file_path}")

        # ### MODIFIED ###: Розділяємо логіку збірки для ASM та CPP
        if args.target == 'asm':
            # Старий процес збірки через nasm та ld
            if args.S: print("\n--- Compilation stopped after assembly generation (-S) ---"); sys.exit(0)

            print("--- Assembling with NASM ---")
            subprocess.run(['nasm', '-f', 'elf64', '-o', obj_file_path, intermediate_file_path], check=True)
            print(f"  [+] Object file saved to {obj_file_path}")
            if args.c: print("\n--- Compilation stopped after assembling (-c) ---"); sys.exit(0)

            print("--- Linking with LD ---")
            subprocess.run(['ld', '-o', executable_path, obj_file_path], check=True)
            print(f"  [+] Executable file saved to {executable_path}")


        elif args.target == 'cpp':
            print("--- Compiling with g++ ---")

            runtime_dir = script_dir / 'cpp_runtime'
            runtime_cpp_path = runtime_dir / 'ignis_runtime.cpp'

            if not runtime_cpp_path.exists():
                print(f"Error: Runtime file not found at '{runtime_cpp_path}'")
                sys.exit(1)

            include_path_arg = f"-I{runtime_dir}"

            compile_command = [
                'g++',
                '-std=c++17',
                include_path_arg,  # Тепер це правильний аргумент, наприклад: "-I/path/to/ignis/cpp_runtime"
                '-o', str(executable_path),
                str(intermediate_file_path),
                str(runtime_cpp_path)
            ]
            subprocess.run(compile_command, check=True)

            print(f"  [+] Executable file saved to {executable_path}")

        print(f"\n--- Compilation successful! ---\nRun './{executable_path.name}' to see the result.")

    except FileNotFoundError:
        # ### MODIFIED ###: Повідомлення про помилку тепер більш загальне
        print(f"\nError: A required build tool was not found (e.g., nasm, ld, g++).");
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during an external command: {e}");
        sys.exit(1)
    except Exception as e:
        if "Compiler error:" in str(e):
            print(f"\n{e}")
        else:
            print("\n--- An unexpected internal compiler error occurred ---")
            traceback.print_exc()
            print("------------------------------------------------------")
        sys.exit(1)
    finally:
        if not args.keep_files:
            print("--- Cleaning up intermediate files ---")
            try:
                # ### MODIFIED ###: Прибираємо проміжні файли залежно від цілі
                if intermediate_file_path.exists(): intermediate_file_path.unlink()
                # Для С++ об'єктний файл не створюється окремо, тому його не видаляємо
                if args.target == 'asm' and obj_file_path.exists(): obj_file_path.unlink()
                if build_dir.exists() and not any(build_dir.iterdir()): build_dir.rmdir()
                print("  [+] Cleanup successful.")
            except OSError as e:
                print(f"  [!] Warning: Could not clean up all intermediate files: {e}")


if __name__ == '__main__':
    main()