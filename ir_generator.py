# ==================== ir_generator.py ====================
# Intermediate Representation (IR) Generator - FIXED VERSION v3

class IRInstruction:
    """Represents a single IR instruction"""
    
    def __init__(self, op, arg1=None, arg2=None, result=None, label=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        self.label = label
    
    def __repr__(self):
        if self.op == 'LABEL':
            return f"{self.arg1}:"
        elif self.op == 'GOTO':
            return f"    GOTO {self.arg1}"
        elif self.op == 'IF_FALSE':
            return f"    IF_FALSE {self.arg1} GOTO {self.result}"
        elif self.op == 'IF_TRUE':
            return f"    IF_TRUE {self.arg1} GOTO {self.result}"
        elif self.op == 'ASSIGN':
            return f"    {self.result} = {self.arg1}"
        elif self.op == 'DECLARE':
            return f"    DECLARE {self.arg1} {self.result}"
        elif self.op == 'PARAM_DECLARE':
            return f"    PARAM_DECLARE {self.arg1} {self.result}"
        elif self.op == 'PARAM':
            return f"    PARAM {self.arg1}"
        elif self.op == 'CALL':
            if self.result:
                return f"    {self.result} = CALL {self.arg1}, {self.arg2}"
            return f"    CALL {self.arg1}, {self.arg2}"
        elif self.op == 'RETURN':
            if self.arg1:
                return f"    RETURN {self.arg1}"
            return f"    RETURN"
        elif self.op == 'FUNC_BEGIN':
            return f"\n{self.arg1}:"
        elif self.op == 'FUNC_END':
            return f"    END_FUNC {self.arg1}"
        elif self.op in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']:
            op_symbol = {
                'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/', 'MOD': '%'
            }[self.op]
            return f"    {self.result} = {self.arg1} {op_symbol} {self.arg2}"
        elif self.op in ['EQ', 'NE', 'LT', 'GT', 'LE', 'GE']:
            op_symbol = {
                'EQ': '==', 'NE': '!=', 'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>='
            }[self.op]
            return f"    {self.result} = {self.arg1} {op_symbol} {self.arg2}"
        elif self.op in ['AND', 'OR']:
            op_symbol = {'AND': '&&', 'OR': '||'}[self.op]
            return f"    {self.result} = {self.arg1} {op_symbol} {self.arg2}"
        elif self.op == 'NOT':
            return f"    {self.result} = !{self.arg1}"
        else:
            return f"    {self.op} {self.arg1} {self.arg2} -> {self.result}"


class IRGenerator:
    """Generates Three-Address Code (TAC) from AST - FIXED VERSION v3"""
    
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function = None
        self.string_literals = {}
        self.string_counter = 0
        self.var_types = {}
        
        self.loop_start_stack = []
        self.loop_end_stack = []
    
    def generate(self, ast):
        """Generate IR from AST"""
        self.visit(ast)
        return self.instructions
    
    def emit(self, op, arg1=None, arg2=None, result=None, label=None):
        """Emit a single IR instruction"""
        instr = IRInstruction(op, arg1, arg2, result, label)
        self.instructions.append(instr)
        return instr
    
    def new_temp(self):
        """Generate a new temporary variable"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self, prefix="L"):
        """Generate a new label"""
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"
    
    def new_string_label(self):
        """Generate a new string literal label"""
        self.string_counter += 1
        return f"STR{self.string_counter}"
    
    def visit(self, node):
        """Dispatch to appropriate visitor"""
        if node is None:
            return None
        
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Fallback visitor"""
        if hasattr(node, '__dict__'):
            for value in vars(node).values():
                if isinstance(value, list):
                    for item in value:
                        self.visit(item)
                elif hasattr(value, '__dict__'):
                    self.visit(value)
        return None
    
    def visit_Program(self, node):
        """Visit program"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDeclaration(self, node):
        """Generate IR for function declaration"""
        self.current_function = node.name
        
        # Reset temp counter for each function
        self.temp_counter = 0
        
        self.emit('FUNC_BEGIN', node.name)
        
        # Emit PARAM_DECLARE for parameters (not DECLARE)
        for param in node.parameters:
            self.var_types[param.name] = param.param_type
            self.emit('PARAM_DECLARE', param.param_type, result=param.name)
        
        # Generate IR for function body
        if node.body:
            for stmt in node.body.statements:
                self.visit(stmt)
        
        # Ensure function ends with return
        if not self.instructions or self.instructions[-1].op != 'RETURN':
            if node.return_type == 'void':
                self.emit('RETURN')
            else:
                self.emit('RETURN', '0')
        
        self.emit('FUNC_END', node.name)
        self.current_function = None
    
    def visit_Block(self, node):
        """Visit block of statements"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_VarDeclaration(self, node):
        """Generate IR for variable declaration"""
        var_name = node.identifier
        var_type = node.var_type
        
        self.var_types[var_name] = var_type
        
        # Local variables use DECLARE (not PARAM_DECLARE)
        self.emit('DECLARE', var_type, result=var_name)
        
        if node.value:
            value = self.visit(node.value)
            self.emit('ASSIGN', value, result=var_name)
        else:
            if var_type == 'float':
                self.emit('ASSIGN', '0.0', result=var_name)
            else:
                self.emit('ASSIGN', '0', result=var_name)
    
    def visit_Assignment(self, node):
        """Generate IR for assignment"""
        value = self.visit(node.value)
        self.emit('ASSIGN', value, result=node.identifier)
        return node.identifier
    
    def visit_CompoundAssignment(self, node):
        """Generate IR for compound assignment"""
        value = self.visit(node.value)
        
        op_map = {
            '+=': 'ADD',
            '-=': 'SUB',
            '*=': 'MUL',
            '/=': 'DIV'
        }
        
        op = op_map.get(node.operator, 'ADD')
        temp = self.new_temp()
        
        self.emit(op, node.identifier, value, temp)
        self.emit('ASSIGN', temp, result=node.identifier)
        
        return node.identifier
    
    def visit_BinaryOp(self, node):
        """Generate IR for binary operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '%': 'MOD'
        }
        
        op = op_map.get(node.operator, 'ADD')
        result = self.new_temp()
        
        self.emit(op, left, right, result)
        return result
    
    def visit_ComparisonOp(self, node):
        """Generate IR for comparison operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op_map = {
            '==': 'EQ',
            '!=': 'NE',
            '<': 'LT',
            '>': 'GT',
            '<=': 'LE',
            '>=': 'GE'
        }
        
        op = op_map.get(node.operator, 'EQ')
        result = self.new_temp()
        
        self.emit(op, left, right, result)
        return result
    
    def visit_LogicalOp(self, node):
        """Generate IR for logical operation"""
        if node.operator == '!':
            operand = self.visit(node.left)
            result = self.new_temp()
            self.emit('NOT', operand, result=result)
            return result
        
        left = self.visit(node.left)
        right = self.visit(node.right) if node.right else None
        
        op_map = {'&&': 'AND', '||': 'OR'}
        op = op_map.get(node.operator, 'AND')
        result = self.new_temp()
        
        self.emit(op, left, right, result)
        return result
    
    def visit_IfStatement(self, node):
        """Generate IR for if statement"""
        cond = self.visit(node.condition)
        
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")
        
        if node.else_block:
            self.emit('IF_FALSE', cond, result=else_label)
            self.visit(node.then_block)
            self.emit('GOTO', end_label)
            self.emit('LABEL', else_label)
            self.visit(node.else_block)
            self.emit('LABEL', end_label)
        else:
            self.emit('IF_FALSE', cond, result=end_label)
            self.visit(node.then_block)
            self.emit('LABEL', end_label)
    
    def visit_WhileStatement(self, node):
        """Generate IR for while loop"""
        start_label = self.new_label("WHILE_START")
        end_label = self.new_label("WHILE_END")
        
        self.loop_start_stack.append(start_label)
        self.loop_end_stack.append(end_label)
        
        self.emit('LABEL', start_label)
        cond = self.visit(node.condition)
        self.emit('IF_FALSE', cond, result=end_label)
        self.visit(node.body)
        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)
        
        self.loop_start_stack.pop()
        self.loop_end_stack.pop()
    
    def visit_ForStatement(self, node):
        """Generate IR for for loop"""
        start_label = self.new_label("FOR_START")
        update_label = self.new_label("FOR_UPDATE")
        end_label = self.new_label("FOR_END")
        
        self.loop_start_stack.append(update_label)
        self.loop_end_stack.append(end_label)
        
        if node.init:
            self.visit(node.init)
        
        self.emit('LABEL', start_label)
        
        if node.condition:
            cond = self.visit(node.condition)
            self.emit('IF_FALSE', cond, result=end_label)
        
        self.visit(node.body)
        
        self.emit('LABEL', update_label)
        if node.update:
            self.visit(node.update)
        
        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)
        
        self.loop_start_stack.pop()
        self.loop_end_stack.pop()
    
    def visit_BreakStatement(self, node):
        """Generate IR for break"""
        if self.loop_end_stack:
            self.emit('GOTO', self.loop_end_stack[-1])
    
    def visit_ContinueStatement(self, node):
        """Generate IR for continue"""
        if self.loop_start_stack:
            self.emit('GOTO', self.loop_start_stack[-1])
    
    def visit_ReturnStatement(self, node):
        """Generate IR for return statement"""
        if node.value:
            value = self.visit(node.value)
            self.emit('RETURN', value)
        else:
            self.emit('RETURN')
    
    def visit_FunctionCall(self, node):
        """Generate IR for function call"""
        args = []
        for arg in node.arguments:
            arg_val = self.visit(arg)
            args.append(arg_val)
        
        for arg in args:
            self.emit('PARAM', arg)
        
        result = self.new_temp()
        self.emit('CALL', node.name, len(args), result)
        
        return result
    
    def visit_Number(self, node):
        """Return number value"""
        return str(node.value)
    
    def visit_StringLiteral(self, node):
        """Handle string literal"""
        label = self.new_string_label()
        self.string_literals[label] = node.value
        return label
    
    def visit_Identifier(self, node):
        """Return identifier name"""
        return node.name
    
    def get_ir_code(self):
        """Get IR as formatted string"""
        lines = ["=" * 60, "THREE-ADDRESS CODE (TAC)", "=" * 60]
        for instr in self.instructions:
            lines.append(str(instr))
        lines.append("=" * 60)
        
        if self.string_literals:
            lines.append("\nSTRING LITERALS:")
            for label, value in self.string_literals.items():
                lines.append(f"  {label}: {value}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    print("✅ IR Generator module loaded successfully!")