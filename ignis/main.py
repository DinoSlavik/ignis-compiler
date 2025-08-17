from lexer import Lexer, TokenType

def main():
    # Path to the example source file
    file_path = '../examples/text.ign'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find the file at {file_path}")
        print("Please create the 'examples/test.ign' file.")
        return

    lexer = Lexer(source_code)

    print("--- Starting Lexical Analysis ---")
    token = lexer.get_next_token()
    while token.type != TokenType.EOF:
        print(token)
        token = lexer.get_next_token()
    print(token) # Print the EOF token as well
    print("--- Lexical Analysis Finished ---")

if __name__ == '__main__':
    main()