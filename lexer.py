# ==================== lexer.py ====================
import re
import sys

# Keywords Definition
KEYWORDS = {
    'int', 'float', 'char', 'void',
    'if', 'else', 'for', 'while',
    'return', 'break', 'continue'
}

# Token Specifications (ORDER MATTERS)
TOKEN_SPECIFICATION = [
    ('COMMENT',         r'//.*|/\*[\s\S]*?\*/'),
    ('FLOAT_LITERAL',   r'\d+\.\d+'),
    ('INTEGER_LITERAL', r'\d+'),
    ('STRING_LITERAL',  r'"([^"\\]|\\.)*"'),
    ('CHAR_LITERAL',    r"'.'"),
    ('OPERATOR',        r'\+\+|--|==|!=|<=|>=|\+=|-=|\*=|/=|&&|\|\||[+\-*/%=<>&|!]'),
    ('DELIMITER',       r'[()\[\]{};,]'),
    ('IDENTIFIER',      r'[A-Za-z_][A-Za-z0-9_]*'),
    ('NEWLINE',         r'\n'),
    ('SKIP',            r'[ \t]+'),
    ('MISMATCH',        r'.')
]

MASTER_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
TOKEN_REGEX = re.compile(MASTER_REGEX)


class Token:
    def __init__(self, token_type, lexeme, line, column):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def to_tuple(self):
        return (self.token_type, self.lexeme, self.line, self.column)

    def __repr__(self):
        return str(self.to_tuple())


class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.tokens = []
        self.symbol_table = {}
        self.errors = []

    def tokenize(self):
        with open(self.filename, 'r') as file:
            code = file.read()

        line_num = 1
        line_start = 0

        for match in TOKEN_REGEX.finditer(code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start + 1

            if kind == 'NEWLINE':
                line_num += 1
                line_start = match.end()

            elif kind in ('SKIP', 'COMMENT'):
                # Handle multi-line comments
                if kind == 'COMMENT':
                    line_num += value.count('\n')
                continue

            elif kind == 'IDENTIFIER':
                if value in KEYWORDS:
                    token_type = 'KEYWORD'
                else:
                    token_type = 'IDENTIFIER'
                    self._add_symbol(value, 'identifier')
                self.tokens.append(Token(token_type, value, line_num, column))

            elif kind in ('INTEGER_LITERAL', 'FLOAT_LITERAL',
                          'STRING_LITERAL', 'CHAR_LITERAL'):
                self._add_symbol(value, 'literal')
                self.tokens.append(Token(kind, value, line_num, column))

            elif kind == 'DELIMITER':
                delimiter_map = {
                    ';': 'SEMICOLON', '(': 'LPAREN', ')': 'RPAREN',
                    '{': 'LBRACE', '}': 'RBRACE',
                    '[': 'LBRACKET', ']': 'RBRACKET', ',': 'COMMA'
                }
                token_name = delimiter_map.get(value, 'DELIMITER')
                self.tokens.append(Token(token_name, value, line_num, column))

            elif kind == 'OPERATOR':
                self.tokens.append(Token('OPERATOR', value, line_num, column))

            elif kind == 'MISMATCH':
                error = f"Lexical Error (line {line_num}, col {column}): Invalid character '{value}'"
                self.errors.append(error)

        # EOF token
        self.tokens.append(Token('EOF', '$', line_num, column))

    def _add_symbol(self, name, category):
        if name not in self.symbol_table:
            self.symbol_table[name] = category

    def get_tokens(self):
        return [token.to_tuple() for token in self.tokens]

    def write_tokens_file(self):
        with open('tokens.txt', 'w') as f:
            for token in self.tokens:
                f.write(f"{token}\n")

    def write_symbol_table(self):
        with open('symbol_table.txt', 'w') as f:
            f.write("Name\tCategory\n")
            for name, category in self.symbol_table.items():
                f.write(f"{name}\t{category}\n")