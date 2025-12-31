# ==================== semantic.py ====================
# Compatible Semantic Analyzer for ParserV2.py AST

class SemanticError(Exception):
    pass


class SemanticSymbolTable:
    """Scoped symbol table for semantic analysis"""
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, var_type):
        if name in self.scopes[-1]:
            return False
        self.scopes[-1][name] = var_type
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    """
    Semantic analyzer compatible with ParserV2.py AST nodes
    """
    def __init__(self):
        self.symbol_table = SemanticSymbolTable()
        self.errors = []
        self.current_function_return_type = None
        
        # Add standard library functions
        self._add_stdlib()

    def _add_stdlib(self):
        """Add standard library functions"""
        self.symbol_table.declare('printf', 'function:int')
        self.symbol_table.declare('scanf', 'function:int')

    def analyze(self, ast):
        """Entry point for semantic analysis"""
        self.visit(ast)
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return True

    def visit(self, node):
        """Dispatch to appropriate visitor method"""
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Fallback for nodes without specific handlers"""
        if hasattr(node, '__dict__'):
            for value in vars(node).values():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__dict__'):
                            self.visit(item)
                elif hasattr(value, '__dict__'):
                    self.visit(value)
        return None

    # =================== Node Visitors ===================
    
    def visit_Program(self, node):
        """Visit program root - FIXED: uses node.statements"""
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Block(self, node):
        """Visit block with new scope"""
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_VarDeclaration(self, node):
        """Visit variable declaration - FIXED: uses node.identifier"""
        name = node.identifier  # String, not Token
        var_type = node.var_type

        if not self.symbol_table.declare(name, var_type):
            self.errors.append(
                f"Semantic Error at {node.line}:{node.col}: Variable '{name}' already declared"
            )

        if node.value:  # FIXED: was node.initializer
            init_type = self.visit(node.value)
            if init_type and init_type != var_type:
                # Allow int to float conversion
                if not (var_type == 'float' and init_type == 'int'):
                    self.errors.append(
                        f"Type Error at {node.line}:{node.col}: Cannot assign {init_type} to {var_type}"
                    )

    def visit_Assignment(self, node):
        """Visit assignment - FIXED: uses node.identifier"""
        name = node.identifier  # String, not Token
        var_type = self.symbol_table.lookup(name)

        if var_type is None:
            self.errors.append(
                f"Semantic Error at {node.line}:{node.col}: Variable '{name}' not declared"
            )
            return None

        value_type = self.visit(node.value)
        if value_type and value_type != var_type:
            if not (var_type == 'float' and value_type == 'int'):
                self.errors.append(
                    f"Type Error at {node.line}:{node.col}: Cannot assign {value_type} to {var_type}"
                )

        return var_type

    def visit_CompoundAssignment(self, node):
        """Visit compound assignment (+=, -=, etc.)"""
        name = node.identifier
        var_type = self.symbol_table.lookup(name)

        if var_type is None:
            self.errors.append(
                f"Semantic Error at {node.line}:{node.col}: Variable '{name}' not declared"
            )
            return None

        value_type = self.visit(node.value)
        
        # Check numeric type for arithmetic operations
        if var_type not in ['int', 'float']:
            self.errors.append(
                f"Type Error at {node.line}:{node.col}: Cannot use '{node.operator}' on type {var_type}"
            )

        return var_type

    def visit_Identifier(self, node):
        """Visit identifier (variable reference) - FIXED: replaces visit_Variable"""
        name = node.name
        var_type = self.symbol_table.lookup(name)

        if var_type is None:
            self.errors.append(
                f"Semantic Error at {node.line}:{node.col}: Variable '{name}' used before declaration"
            )
            return None

        # Handle function references
        if isinstance(var_type, str) and var_type.startswith('function:'):
            return var_type.split(':')[1]
        
        return var_type

    def visit_Number(self, node):
        """Visit number literal - FIXED: replaces visit_Literal"""
        value = node.value
        if isinstance(value, str):
            if '.' in value:
                return 'float'
            return 'int'
        if isinstance(value, float):
            return 'float'
        return 'int'

    def visit_StringLiteral(self, node):
        """Visit string literal"""
        return 'string'

    def visit_BinaryOp(self, node):
        """Visit binary operation - FIXED: replaces visit_BinaryExpr"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type is None or right_type is None:
            return None

        # Type compatibility check
        if left_type != right_type:
            # Allow int/float mixed arithmetic
            if {left_type, right_type} == {'int', 'float'}:
                return 'float'
            self.errors.append(
                f"Type Error at {node.line}:{node.col}: Incompatible types {left_type} and {right_type}"
            )
            return None

        # Check valid operations
        if node.operator in ['+', '-', '*', '/', '%']:
            if left_type not in ['int', 'float']:
                self.errors.append(
                    f"Type Error at {node.line}:{node.col}: Invalid operation '{node.operator}' on type {left_type}"
                )
                return None

        return left_type

    def visit_ComparisonOp(self, node):
        """Visit comparison operation"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type is None or right_type is None:
            return 'int'  # Boolean represented as int

        # Allow numeric comparisons
        if left_type != right_type:
            if {left_type, right_type} != {'int', 'float'}:
                self.errors.append(
                    f"Type Error at {node.line}:{node.col}: Cannot compare {left_type} with {right_type}"
                )

        return 'int'  # Comparison returns int (0 or 1)

    def visit_LogicalOp(self, node):
        """Visit logical operation"""
        self.visit(node.left)
        if node.right:
            self.visit(node.right)
        return 'int'  # Boolean as int

    def visit_IfStatement(self, node):
        """Visit if statement"""
        self.visit(node.condition)
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_WhileStatement(self, node):
        """Visit while loop"""
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ForStatement(self, node):
        """Visit for loop"""
        self.symbol_table.enter_scope()
        if node.init:
            self.visit(node.init)
        if node.condition:
            self.visit(node.condition)
        if node.update:
            self.visit(node.update)
        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_FunctionDeclaration(self, node):
        """Visit function declaration"""
        # Declare function in current scope
        func_type = f"function:{node.return_type}"
        self.symbol_table.declare(node.name, func_type)

        # Enter function scope
        self.symbol_table.enter_scope()
        self.current_function_return_type = node.return_type

        # Declare parameters
        for param in node.parameters:
            self.symbol_table.declare(param.name, param.param_type)

        # Visit body
        if node.body:
            # Visit statements directly, don't create new scope (body is already Block)
            for stmt in node.body.statements:
                self.visit(stmt)

        self.current_function_return_type = None
        self.symbol_table.exit_scope()

    def visit_FunctionCall(self, node):
        """Visit function call"""
        func_type = self.symbol_table.lookup(node.name)
        
        if func_type is None:
            self.errors.append(
                f"Semantic Error at {node.line}:{node.col}: Undefined function '{node.name}'"
            )
            return None

        # Visit arguments
        for arg in node.arguments:
            self.visit(arg)

        # Extract return type
        if isinstance(func_type, str) and func_type.startswith('function:'):
            return func_type.split(':')[1]
        
        return 'int'  # Default

    def visit_ReturnStatement(self, node):
        """Visit return statement"""
        if node.value:
            return_type = self.visit(node.value)
            if self.current_function_return_type:
                if return_type and return_type != self.current_function_return_type:
                    if not (self.current_function_return_type == 'float' and return_type == 'int'):
                        self.errors.append(
                            f"Type Error at {node.line}:{node.col}: Return type mismatch"
                        )

    def visit_BreakStatement(self, node):
        pass

    def visit_ContinueStatement(self, node):
        pass

    def visit_Parameter(self, node):
        pass


# Test
if __name__ == "__main__":
    print("Semantic Analyzer module loaded successfully!")