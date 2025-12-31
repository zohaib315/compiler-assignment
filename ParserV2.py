# ==================== ParserV2.py ====================


# =============================================================
#                          AST Nodes
# =============================================================
class ASTNode:
    def __init__(self, line=None, col=None):
        self.line = line
        self.col = col


class Program(ASTNode):
    def __init__(self, statements):  # FIXED: was 'statement'
        super().__init__()
        self.statements = statements  # FIXED: consistent naming

    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


class Number(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class Identifier(ASTNode):
    def __init__(self, name, line=None, col=None):
        super().__init__(line, col)
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


class StringLiteral(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"String({self.value})"


class BinaryOp(ASTNode):
    def __init__(self, operator, left, right, line=None, col=None):
        super().__init__(line, col)
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp('{self.operator}', {self.left}, {self.right})"


class VarDeclaration(ASTNode):
    def __init__(self, var_type, identifier, value=None, line=None, col=None):
        super().__init__(line, col)
        self.var_type = var_type
        self.identifier = identifier  # String name
        self.value = value  # Optional initializer

    def __repr__(self):
        return f"VarDeclaration(type='{self.var_type}', id='{self.identifier}', value={self.value})"


class Assignment(ASTNode):
    def __init__(self, identifier, value, line=None, col=None):
        super().__init__(line, col)
        self.identifier = identifier  # String name
        self.value = value

    def __repr__(self):
        return f"Assignment('{self.identifier}' = {self.value})"


class CompoundAssignment(ASTNode):
    def __init__(self, identifier, operator, value, line=None, col=None):
        super().__init__(line, col)
        self.identifier = identifier
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"CompoundAssignment('{self.identifier}' {self.operator} {self.value})"


class ComparisonOp(ASTNode):
    def __init__(self, operator, left, right, line=None, col=None):
        super().__init__(line, col)
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"ComparisonOp('{self.operator}', {self.left}, {self.right})"


class LogicalOp(ASTNode):
    def __init__(self, operator, left, right=None, line=None, col=None):
        super().__init__(line, col)
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        if self.right:
            return f"LogicalOp('{self.operator}', {self.left}, {self.right})"
        return f"LogicalOp('{self.operator}', {self.left})"


class Block(ASTNode):
    def __init__(self, statements, line=None, col=None):
        super().__init__(line, col)
        self.statements = statements

    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block=None, line=None, col=None):
        super().__init__(line, col)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self):
        return f"IfStatement(condition={self.condition})"


class WhileStatement(ASTNode):
    def __init__(self, condition, body, line=None, col=None):
        super().__init__(line, col)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement(condition={self.condition})"


class ForStatement(ASTNode):
    def __init__(self, init, condition, update, body, line=None, col=None):
        super().__init__(line, col)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"ForStatement()"


class BreakStatement(ASTNode):
    def __repr__(self):
        return "BreakStatement()"


class ContinueStatement(ASTNode):
    def __repr__(self):
        return "ContinueStatement()"


class Parameter(ASTNode):
    def __init__(self, param_type, name, line=None, col=None):
        super().__init__(line, col)
        self.param_type = param_type
        self.name = name

    def __repr__(self):
        return f"Parameter({self.param_type} {self.name})"


class FunctionDeclaration(ASTNode):
    def __init__(self, return_type, name, parameters, body, line=None, col=None):
        super().__init__(line, col)
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return f"FunctionDeclaration({self.return_type} {self.name})"


class FunctionCall(ASTNode):
    def __init__(self, name, arguments, line=None, col=None):
        super().__init__(line, col)
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall({self.name})"


class ReturnStatement(ASTNode):
    def __init__(self, value=None, line=None, col=None):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"ReturnStatement({self.value})"


# =============================================================
#                       AST Printer
# =============================================================
def print_ast(node, indent=0, prefix=""):
    indent_str = "  " * indent

    if node is None:
        print(f"{indent_str}{prefix}None")
        return

    if isinstance(node, Program):
        print(f"{indent_str}{prefix}Program")
        for i, stmt in enumerate(node.statements):
            print_ast(stmt, indent + 1, f"[{i}]: ")

    elif isinstance(node, FunctionDeclaration):
        print(f"{indent_str}{prefix}FunctionDeclaration({node.return_type} {node.name})")
        print(f"{indent_str}  params: {node.parameters}")
        print_ast(node.body, indent + 1, "body: ")

    elif isinstance(node, Block):
        print(f"{indent_str}{prefix}Block")
        for i, stmt in enumerate(node.statements):
            print_ast(stmt, indent + 1, f"[{i}]: ")

    elif isinstance(node, VarDeclaration):
        print(f"{indent_str}{prefix}VarDeclaration({node.var_type} {node.identifier})")
        if node.value:
            print_ast(node.value, indent + 1, "value: ")

    elif isinstance(node, Assignment):
        print(f"{indent_str}{prefix}Assignment({node.identifier})")
        print_ast(node.value, indent + 1, "value: ")

    elif isinstance(node, CompoundAssignment):
        print(f"{indent_str}{prefix}CompoundAssignment({node.identifier} {node.operator})")
        print_ast(node.value, indent + 1, "value: ")

    elif isinstance(node, IfStatement):
        print(f"{indent_str}{prefix}IfStatement")
        print_ast(node.condition, indent + 1, "condition: ")
        print_ast(node.then_block, indent + 1, "then: ")
        if node.else_block:
            print_ast(node.else_block, indent + 1, "else: ")

    elif isinstance(node, WhileStatement):
        print(f"{indent_str}{prefix}WhileStatement")
        print_ast(node.condition, indent + 1, "condition: ")
        print_ast(node.body, indent + 1, "body: ")

    elif isinstance(node, ForStatement):
        print(f"{indent_str}{prefix}ForStatement")
        print_ast(node.init, indent + 1, "init: ")
        print_ast(node.condition, indent + 1, "condition: ")
        print_ast(node.update, indent + 1, "update: ")
        print_ast(node.body, indent + 1, "body: ")

    elif isinstance(node, FunctionCall):
        print(f"{indent_str}{prefix}FunctionCall({node.name})")
        for i, arg in enumerate(node.arguments):
            print_ast(arg, indent + 1, f"arg[{i}]: ")

    elif isinstance(node, ReturnStatement):
        print(f"{indent_str}{prefix}ReturnStatement")
        if node.value:
            print_ast(node.value, indent + 1, "value: ")

    elif isinstance(node, BinaryOp):
        print(f"{indent_str}{prefix}BinaryOp({node.operator})")
        print_ast(node.left, indent + 1, "left: ")
        print_ast(node.right, indent + 1, "right: ")

    elif isinstance(node, ComparisonOp):
        print(f"{indent_str}{prefix}ComparisonOp({node.operator})")
        print_ast(node.left, indent + 1, "left: ")
        print_ast(node.right, indent + 1, "right: ")

    elif isinstance(node, LogicalOp):
        print(f"{indent_str}{prefix}LogicalOp({node.operator})")
        print_ast(node.left, indent + 1, "left: ")
        if node.right:
            print_ast(node.right, indent + 1, "right: ")

    elif isinstance(node, (Number, StringLiteral)):
        print(f"{indent_str}{prefix}{node.__class__.__name__}({node.value})")

    elif isinstance(node, Identifier):
        print(f"{indent_str}{prefix}Identifier({node.name})")

    elif isinstance(node, (BreakStatement, ContinueStatement)):
        print(f"{indent_str}{prefix}{node.__class__.__name__}")

    else:
        print(f"{indent_str}{prefix}{node}")


# =============================================================
#                     Symbol Table (Parser)
# =============================================================
class Symbol:
    def __init__(self, name, symbol_type, value=None, is_function=False, params=None):
        self.name = name
        self.type = symbol_type
        self.value = value
        self.is_function = is_function
        self.params = params or []
        self.is_variadic = False

    def __repr__(self):
        if self.is_function:
            return f"Function({self.type})"
        return f"Variable({self.type})"


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self._add_stdlib()

    def _add_stdlib(self):
        stdlib = [
            ('printf', 'int', True),
            ('scanf', 'int', True),
            ('malloc', 'void*', False),
            ('free', 'void', False),
        ]
        for name, ret_type, variadic in stdlib:
            sym = Symbol(name, ret_type, is_function=True)
            sym.is_variadic = variadic
            self.symbols[name] = sym

    def declare(self, name, symbol_type, value=None, is_function=False, params=None):
        if name in self.symbols:
            return False
        self.symbols[name] = Symbol(name, symbol_type, value, is_function, params)
        return True

    def lookup(self, name):
        return self.symbols.get(name)

    def exists(self, name):
        return name in self.symbols


# =============================================================
#                        Token Class
# =============================================================
class Token:
    def __init__(self, token_type, lexeme, line, col):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}')"


# =============================================================
#                          Parser
# =============================================================
class Parser:
    def __init__(self, tokens):
        self.tokens = [Token(*t) if len(t) == 4 else Token(t[0], t[1], t[2], 0)
                       for t in tokens]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.symbol_table = SymbolTable()
        self.errors = []
        self.loop_depth = 0
        self.function_depth = 0

    # Token Management
    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset=1):
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else None

    def check(self, token_type, lexeme=None):
        if not self.current_token:
            return False
        if self.current_token.type != token_type:
            return False
        if lexeme and self.current_token.lexeme != lexeme:
            return False
        return True

    def match(self, token_type, lexeme=None):
        if self.check(token_type, lexeme):
            token = self.current_token
            self.advance()
            return token
        return None

    def expect(self, token_type, lexeme=None):
        token = self.match(token_type, lexeme)
        if token:
            return token
        expected = f"{token_type}" + (f":'{lexeme}'" if lexeme else "")
        actual = f"{self.current_token.type}:'{self.current_token.lexeme}'" if self.current_token else "EOF"
        self.report_error(f"Expected {expected}, got {actual}")
        return None

    def report_error(self, message):
        if self.current_token:
            error = f"Syntax Error at {self.current_token.line}:{self.current_token.col} - {message}"
        else:
            error = f"Syntax Error at EOF - {message}"
        self.errors.append(error)
        print(f"❌ {error}")

    def synchronize(self):
        sync_tokens = {'SEMICOLON', 'EOF', 'RBRACE'}
        sync_keywords = {'int', 'float', 'char', 'void', 'if', 'while', 'for', 'return'}
        
        while self.current_token:
            if self.current_token.type in sync_tokens:
                if self.current_token.type == 'SEMICOLON':
                    self.advance()
                return
            if self.current_token.type == 'KEYWORD' and self.current_token.lexeme in sync_keywords:
                return
            self.advance()

    # Main Parse Entry
    def parse(self):
        print("🔍 Starting parsing...")
        ast = self.program()
        if not self.errors:
            print("✅ Parsing completed successfully!")
        return ast

    def program(self):
        statements = []
        while self.current_token and self.current_token.type != 'EOF':
            stmt = self.declaration_or_statement()
            if stmt:
                statements.append(stmt)
            if self.errors and self.current_token and self.current_token.type != 'EOF':
                self.synchronize()
        return Program(statements)

    def declaration_or_statement(self):
        if self.check('KEYWORD'):
            keyword = self.current_token.lexeme
            if keyword in ['int', 'float', 'char', 'void']:
                next_tok = self.peek()
                next_next = self.peek(2)
                if next_tok and next_tok.type == 'IDENTIFIER' and next_next and next_next.type == 'LPAREN':
                    return self.function_declaration()
        return self.statement()

    def function_declaration(self):
        type_token = self.expect('KEYWORD')
        if not type_token:
            return None
        return_type = type_token.lexeme
        line, col = type_token.line, type_token.col

        name_token = self.expect('IDENTIFIER')
        if not name_token:
            return None
        func_name = name_token.lexeme

        if not self.expect('LPAREN'):
            return None
        parameters = self.parameter_list()
        if not self.expect('RPAREN'):
            return None

        self.symbol_table.declare(func_name, return_type, is_function=True, params=parameters)

        self.function_depth += 1
        body = self.block()
        self.function_depth -= 1

        return FunctionDeclaration(return_type, func_name, parameters, body, line, col)

    def parameter_list(self):
        params = []
        if self.check('RPAREN'):
            return params
        
        param = self.parameter()
        if param:
            params.append(param)
        
        while self.match('COMMA'):
            param = self.parameter()
            if param:
                params.append(param)
        return params

    def parameter(self):
        type_token = self.expect('KEYWORD')
        if not type_token:
            return None
        name_token = self.expect('IDENTIFIER')
        if not name_token:
            return None
        return Parameter(type_token.lexeme, name_token.lexeme, type_token.line, type_token.col)

    def statement(self):
        if self.check('KEYWORD'):
            kw = self.current_token.lexeme
            if kw in ['int', 'float', 'char']:
                return self.declaration()
            elif kw == 'if':
                return self.if_statement()
            elif kw == 'while':
                return self.while_statement()
            elif kw == 'for':
                return self.for_statement()
            elif kw == 'break':
                return self.break_statement()
            elif kw == 'continue':
                return self.continue_statement()
            elif kw == 'return':
                return self.return_statement()

        if self.check('LBRACE'):
            return self.block()

        if self.check('IDENTIFIER'):
            next_tok = self.peek()
            if next_tok and next_tok.type == 'OPERATOR':
                if next_tok.lexeme in ['+=', '-=', '*=', '/=']:
                    return self.compound_assignment()
                elif next_tok.lexeme == '=':
                    return self.assignment()

        return self.expression_statement()

    def declaration(self):
        type_token = self.expect('KEYWORD')
        if not type_token:
            return None
        var_type = type_token.lexeme
        line, col = type_token.line, type_token.col

        id_token = self.expect('IDENTIFIER')
        if not id_token:
            return None
        identifier = id_token.lexeme

        value = None
        if self.match('OPERATOR', '='):
            value = self.expression()

        self.expect('SEMICOLON')
        self.symbol_table.declare(identifier, var_type, value)

        return VarDeclaration(var_type, identifier, value, line, col)

    def assignment(self):
        id_token = self.expect('IDENTIFIER')
        if not id_token:
            return None
        identifier = id_token.lexeme
        line, col = id_token.line, id_token.col

        if not self.expect('OPERATOR', '='):
            return None
        value = self.expression()
        self.expect('SEMICOLON')

        return Assignment(identifier, value, line, col)

    def compound_assignment(self):
        id_token = self.expect('IDENTIFIER')
        if not id_token:
            return None
        identifier = id_token.lexeme
        line, col = id_token.line, id_token.col

        op_token = self.expect('OPERATOR')
        if not op_token:
            return None
        operator = op_token.lexeme

        value = self.expression()
        self.expect('SEMICOLON')

        return CompoundAssignment(identifier, operator, value, line, col)

    def if_statement(self):
        if_token = self.expect('KEYWORD', 'if')
        line, col = if_token.line, if_token.col

        self.expect('LPAREN')
        condition = self.logical_or_expression()
        self.expect('RPAREN')

        then_block = self.statement()

        else_block = None
        if self.match('KEYWORD', 'else'):
            else_block = self.statement()

        return IfStatement(condition, then_block, else_block, line, col)

    def while_statement(self):
        while_token = self.expect('KEYWORD', 'while')
        line, col = while_token.line, while_token.col

        self.expect('LPAREN')
        condition = self.logical_or_expression()
        self.expect('RPAREN')

        self.loop_depth += 1
        body = self.statement()
        self.loop_depth -= 1

        return WhileStatement(condition, body, line, col)

    def for_statement(self):
        for_token = self.expect('KEYWORD', 'for')
        line, col = for_token.line, for_token.col

        self.expect('LPAREN')

        init = None
        if not self.check('SEMICOLON'):
            if self.check('KEYWORD'):
                init = self.declaration()
            else:
                init = self.assignment()
        else:
            self.advance()

        condition = None
        if not self.check('SEMICOLON'):
            condition = self.logical_or_expression()
        self.expect('SEMICOLON')

        update = None
        if not self.check('RPAREN'):
            id_token = self.current_token
            self.advance()
            if self.check('OPERATOR') and self.current_token.lexeme in ['+=', '-=', '*=', '/=']:
                op = self.current_token.lexeme
                self.advance()
                value = self.expression()
                update = CompoundAssignment(id_token.lexeme, op, value, id_token.line, id_token.col)
            elif self.check('OPERATOR') and self.current_token.lexeme == '=':
                self.advance()
                value = self.expression()
                update = Assignment(id_token.lexeme, value, id_token.line, id_token.col)

        self.expect('RPAREN')

        self.loop_depth += 1
        body = self.statement()
        self.loop_depth -= 1

        return ForStatement(init, condition, update, body, line, col)

    def break_statement(self):
        token = self.expect('KEYWORD', 'break')
        if self.loop_depth == 0:
            self.report_error("'break' not inside loop")
        self.expect('SEMICOLON')
        return BreakStatement(token.line, token.col)

    def continue_statement(self):
        token = self.expect('KEYWORD', 'continue')
        if self.loop_depth == 0:
            self.report_error("'continue' not inside loop")
        self.expect('SEMICOLON')
        return ContinueStatement(token.line, token.col)

    def return_statement(self):
        token = self.expect('KEYWORD', 'return')
        if self.function_depth == 0:
            self.report_error("'return' not inside function")
        
        value = None
        if not self.check('SEMICOLON'):
            value = self.expression()
        self.expect('SEMICOLON')
        
        return ReturnStatement(value, token.line, token.col)

    def block(self):
        if not self.expect('LBRACE'):
            return None
        line = self.current_token.line if self.current_token else 0
        col = self.current_token.col if self.current_token else 0

        statements = []
        while self.current_token and not self.check('RBRACE') and self.current_token.type != 'EOF':
            stmt = self.statement()
            if stmt:
                statements.append(stmt)

        self.expect('RBRACE')
        return Block(statements, line, col)

    def expression_statement(self):
        expr = self.expression()
        self.expect('SEMICOLON')
        return expr

    # Expression parsing with precedence
    def logical_or_expression(self):
        left = self.logical_and_expression()
        while self.check('OPERATOR') and self.current_token.lexeme == '||':
            op = self.current_token
            self.advance()
            right = self.logical_and_expression()
            left = LogicalOp('||', left, right, op.line, op.col)
        return left

    def logical_and_expression(self):
        left = self.equality_expression()
        while self.check('OPERATOR') and self.current_token.lexeme == '&&':
            op = self.current_token
            self.advance()
            right = self.equality_expression()
            left = LogicalOp('&&', left, right, op.line, op.col)
        return left

    def equality_expression(self):
        left = self.relational_expression()
        while self.check('OPERATOR') and self.current_token.lexeme in ['==', '!=']:
            op = self.current_token
            self.advance()
            right = self.relational_expression()
            left = ComparisonOp(op.lexeme, left, right, op.line, op.col)
        return left

    def relational_expression(self):
        left = self.expression()
        while self.check('OPERATOR') and self.current_token.lexeme in ['<', '>', '<=', '>=']:
            op = self.current_token
            self.advance()
            right = self.expression()
            left = ComparisonOp(op.lexeme, left, right, op.line, op.col)
        return left

    def expression(self):
        left = self.term()
        while self.check('OPERATOR') and self.current_token.lexeme in ['+', '-']:
            op = self.current_token
            self.advance()
            right = self.term()
            left = BinaryOp(op.lexeme, left, right, op.line, op.col)
        return left

    def term(self):
        left = self.factor()
        while self.check('OPERATOR') and self.current_token.lexeme in ['*', '/', '%']:
            op = self.current_token
            self.advance()
            right = self.factor()
            left = BinaryOp(op.lexeme, left, right, op.line, op.col)
        return left

    def factor(self):
        if self.check('OPERATOR', '!'):
            op = self.current_token
            self.advance()
            expr = self.factor()
            return LogicalOp('!', expr, None, op.line, op.col)

        if self.check('INTEGER_LITERAL') or self.check('FLOAT_LITERAL'):
            token = self.current_token
            self.advance()
            return Number(token.lexeme, token.line, token.col)

        if self.check('STRING_LITERAL'):
            token = self.current_token
            self.advance()
            return StringLiteral(token.lexeme, token.line, token.col)

        if self.check('IDENTIFIER'):
            if self.peek() and self.peek().type == 'LPAREN':
                return self.function_call()
            token = self.current_token
            self.advance()
            return Identifier(token.lexeme, token.line, token.col)

        if self.check('LPAREN'):
            self.advance()
            expr = self.logical_or_expression()
            self.expect('RPAREN')
            return expr

        self.report_error(f"Unexpected token: {self.current_token}")
        self.advance()
        return None

    def function_call(self):
        name_token = self.expect('IDENTIFIER')
        func_name = name_token.lexeme
        line, col = name_token.line, name_token.col

        self.expect('LPAREN')
        arguments = self.argument_list()
        self.expect('RPAREN')

        return FunctionCall(func_name, arguments, line, col)

    def argument_list(self):
        args = []
        if self.check('RPAREN'):
            return args
        
        arg = self.expression()
        if arg:
            args.append(arg)
        
        while self.match('COMMA'):
            arg = self.expression()
            if arg:
                args.append(arg)
        return args



