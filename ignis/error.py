class ErrorReporter:
    def __init__(self, file_path, source_lines):
        self.file_path = file_path
        self.source_lines = source_lines
        self.had_error = False
        self.had_warning = False

    def _report(self, level, code, message, token):
        if level == "Error":
            self.had_error = True
        elif level == "Warning":
            self.had_warning = True

        line_num, col_num = (token.line, token.col) if token else (1, 1)

        header = f"{code}: {message}"
        if token.type is not None:
            token_text = f"{token}"
        else:
            token_text = "NoneToken"
        location = f"--> {self.file_path}:{line_num}:{col_num}"

        snippet = ""
        start_line = max(0, line_num - 3)
        end_line = min(len(self.source_lines), line_num + 2)

        for i in range(start_line, end_line):
            line = self.source_lines[i]
            line_number_str = f"{i + 1:4} | "
            snippet += f"{line_number_str}{line}\n"
            if i + 1 == line_num:
                pointer_padding = ' ' * (len(line_number_str) + col_num - 1)
                snippet += f"{pointer_padding}^\n"

        full_message = f"{level} {header}\n{token_text}\n{location}\n\n{snippet}"

        if level == "Error":
            raise Exception(f'Compiler error:\n{full_message}')
        else:
            print(f"{full_message}\n")

    def error(self, code, message, token):
        self._report("Error", code, message, token)

    def warning(self, code, message, token):
        self._report("Warning", code, message, token)
