import subprocess
from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator


def main():
    file_path = '../examples/test.ign'
    output_base_name = 'output'

    print(f"--- Compiling {file_path} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find the file at {file_path}")
        return

    # 1. Lexer
    lexer = Lexer(source_code)

    # 2. Parser
    parser = Parser(lexer)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return

    # 3. Code Generation
    generator = CodeGenerator()
    try:
        assembly_code = generator.generate(ast)
    except Exception as e:
        print(f"An error occurred during code generation: {e}")
        return

    asm_file_path = f'{output_base_name}.asm'
    with open(asm_file_path, 'w') as f:
        f.write(assembly_code)
    print(f"  [+] Assembly code saved to {asm_file_path}")

    # 4. Assembling and Linking
    obj_file_path = f'{output_base_name}.o'
    executable_path = output_base_name

    try:
        print("--- Assembling with NASM ---")
        subprocess.run(['nasm', '-f', 'elf64', '-o', obj_file_path, asm_file_path], check=True)
        print(f"  [+] Object file saved to {obj_file_path}")

        print("--- Linking with LD ---")
        subprocess.run(['ld', '-o', executable_path, obj_file_path], check=True)
        print(f"  [+] Executable file saved to {executable_path}")

        print("\n--- Compilation successful! ---")
        print(f"Run './{executable_path}' to see the result.")

    except FileNotFoundError:
        print("\nError: 'nasm' or 'ld' not found. Please ensure they are installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during assembling or linking: {e}")


if __name__ == '__main__':
    main()
