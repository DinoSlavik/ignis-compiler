from lexer import Lexer
from parser import Parser

def main():
    file_path = '../examples/test.ign'

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

    print("--- Starting Syntactic Analysis (Parsing) ---")
    try:
        ast = parser.parse()
        print(ast)
    except Exception as e:
        print(f"An error occurred: {e}")

    print("--- Syntactic Analysis Finished ---")


if __name__ == '__main__':
    main()