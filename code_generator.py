# ==================== code_generator.py ====================
# Target Code Generator - FIXED VERSION v5
# Supports: C code and x86-64 Assembly

class CodeGenerator:
    """Generates C code or x86 Assembly from Three-Address Code IR"""
    
    def __init__(self, target='c'):
        self.target = target
        self.output = []
        self.string_literals = {}
        self.var_types = {}
        self._pending_params = []
    
    def generate(self, instructions, string_literals=None, var_types=None, function_params=None):
        """Generate target code from IR instructions"""
        self.string_literals = string_literals or {}
        self.var_types = var_types or {}
        self._pending_params = []
        self.output = []
        
        if self.target == 'c':
            return self._generate_c(instructions)
        elif self.target == 'x86':
            return self._generate_x86(instructions)
        else:
            raise ValueError(f"Unknown target: {self.target}")
    
    # =========================================================
    #                    C CODE GENERATION
    # =========================================================
    
    def _generate_c(self, instructions):
        """Generate C code from IR"""
        
        # Header
        self._emit("/* Generated C Code */")
        self._emit("#include <stdio.h>")
        self._emit("#include <stdlib.h>")
        self._emit("")
        
        # Split instructions by function
        functions = self._split_by_function(instructions)
        
        # Generate each function
        for func_name, func_instructions in functions.items():
            self._generate_c_function(func_name, func_instructions)
        
        return "\n".join(self.output)
    
    def _split_by_function(self, instructions):
        """Split instructions into separate functions"""
        functions = {}
        current_func = None
        current_instructions = []
        
        for instr in instructions:
            if instr.op == 'FUNC_BEGIN':
                current_func = instr.arg1
                current_instructions = []
            elif instr.op == 'FUNC_END':
                if current_func:
                    functions[current_func] = current_instructions
                current_func = None
            else:
                if current_func:
                    current_instructions.append(instr)
        
        return functions
    
    def _generate_c_function(self, func_name, instructions):
        """Generate C code for a single function"""
        
        # Collect all declarations
        params = []
        local_vars = []
        local_var_names = set()
        temps = set()
        
        for instr in instructions:
            if instr.op == 'PARAM_DECLARE':
                params.append((instr.result, instr.arg1))
            elif instr.op == 'DECLARE':
                if instr.result not in local_var_names:
                    local_vars.append((instr.result, instr.arg1))
                    local_var_names.add(instr.result)
            else:
                # Track temporaries
                for operand in [instr.result, instr.arg1, instr.arg2]:
                    if operand and str(operand).startswith('t'):
                        temp_str = str(operand)
                        if len(temp_str) > 1 and temp_str[1:].isdigit():
                            temps.add(operand)
        
        # Remove temps that match local variable or parameter names
        temps = temps - local_var_names
        param_names = {p[0] for p in params}
        temps = temps - param_names
        
        # Build function signature
        if params:
            param_str = ", ".join([f"{ptype} {pname}" for pname, ptype in params])
            self._emit(f"int {func_name}({param_str}) {{")
        else:
            self._emit(f"int {func_name}() {{")
        
        # Declare local variables
        for var_name, var_type in local_vars:
            self._emit(f"    {var_type} {var_name};")
        
        # Declare temporaries
        if temps:
            temps_sorted = sorted(temps, key=lambda x: int(str(x)[1:]) if str(x)[1:].isdigit() else 0)
            self._emit(f"    int {', '.join(temps_sorted)};")
        
        if local_vars or temps:
            self._emit("")
        
        # Generate code
        for instr in instructions:
            if instr.op in ['DECLARE', 'PARAM_DECLARE']:
                continue
            
            line = self._generate_c_instruction(instr)
            if line:
                if instr.op == 'LABEL':
                    self._emit(line)
                else:
                    self._emit("    " + line)
        
        self._emit("}")
        self._emit("")
    
    def _generate_c_instruction(self, instr):
        """Generate C code for a single IR instruction"""
        
        if instr.op == 'LABEL':
            return f"{instr.arg1}:;"
        
        elif instr.op == 'ASSIGN':
            value = instr.arg1
            if str(value).startswith('STR'):
                value = self.string_literals.get(value, '""')
            return f"{instr.result} = {value};"
        
        elif instr.op == 'ADD':
            return f"{instr.result} = {instr.arg1} + {instr.arg2};"
        
        elif instr.op == 'SUB':
            return f"{instr.result} = {instr.arg1} - {instr.arg2};"
        
        elif instr.op == 'MUL':
            return f"{instr.result} = {instr.arg1} * {instr.arg2};"
        
        elif instr.op == 'DIV':
            return f"{instr.result} = {instr.arg1} / {instr.arg2};"
        
        elif instr.op == 'MOD':
            return f"{instr.result} = {instr.arg1} % {instr.arg2};"
        
        elif instr.op == 'EQ':
            return f"{instr.result} = ({instr.arg1} == {instr.arg2});"
        
        elif instr.op == 'NE':
            return f"{instr.result} = ({instr.arg1} != {instr.arg2});"
        
        elif instr.op == 'LT':
            return f"{instr.result} = ({instr.arg1} < {instr.arg2});"
        
        elif instr.op == 'GT':
            return f"{instr.result} = ({instr.arg1} > {instr.arg2});"
        
        elif instr.op == 'LE':
            return f"{instr.result} = ({instr.arg1} <= {instr.arg2});"
        
        elif instr.op == 'GE':
            return f"{instr.result} = ({instr.arg1} >= {instr.arg2});"
        
        elif instr.op == 'AND':
            return f"{instr.result} = ({instr.arg1} && {instr.arg2});"
        
        elif instr.op == 'OR':
            return f"{instr.result} = ({instr.arg1} || {instr.arg2});"
        
        elif instr.op == 'NOT':
            return f"{instr.result} = !{instr.arg1};"
        
        elif instr.op == 'IF_FALSE':
            return f"if (!{instr.arg1}) goto {instr.result};"
        
        elif instr.op == 'IF_TRUE':
            return f"if ({instr.arg1}) goto {instr.result};"
        
        elif instr.op == 'GOTO':
            return f"goto {instr.arg1};"
        
        elif instr.op == 'PARAM':
            self._pending_params.append(instr.arg1)
            return None
        
        elif instr.op == 'CALL':
            params = self._pending_params.copy()
            self._pending_params = []
            
            formatted_params = []
            for p in params:
                if str(p).startswith('STR'):
                    val = self.string_literals.get(p, '""')
                    formatted_params.append(val)
                else:
                    formatted_params.append(str(p))
            
            args_str = ", ".join(formatted_params)
            
            if instr.result:
                return f"{instr.result} = {instr.arg1}({args_str});"
            return f"{instr.arg1}({args_str});"
        
        elif instr.op == 'RETURN':
            if instr.arg1:
                return f"return {instr.arg1};"
            return "return 0;"
        
        return None
    
    # =========================================================
    #                 x86-64 ASSEMBLY GENERATION
    # =========================================================
    
    def _generate_x86(self, instructions):
        """Generate x86-64 assembly from IR"""
        self.output = []
        self.variables = {}
        self.stack_offset = 0
        
        # Header
        self._emit("; Generated x86-64 Assembly (NASM syntax)")
        self._emit("; Compile: nasm -f elf64 output.asm -o output.o")
        self._emit("; Link: gcc output.o -o output -no-pie")
        self._emit("")
        self._emit("bits 64")
        self._emit("default rel")
        self._emit("")
        
        # External declarations
        self._emit("extern printf")
        self._emit("extern scanf")
        self._emit("extern exit")
        self._emit("")
        
        # Data section
        self._emit("section .data")
        self._emit('    fmt_int: db "%d", 10, 0')
        self._emit('    fmt_str: db "%s", 10, 0')
        
        # String literals
        for label, value in self.string_literals.items():
            clean_value = str(value).strip('"').replace('\\n', '", 10, "')
            self._emit(f'    {label}: db "{clean_value}", 0')
        
        self._emit("")
        
        # BSS section
        self._emit("section .bss")
        
        # Collect all variables
        all_vars = set()
        for instr in instructions:
            if instr.op in ['DECLARE', 'PARAM_DECLARE']:
                all_vars.add(instr.result)
            if instr.result and not str(instr.result).startswith(('t', 'L', 'STR', 'FUNC', 'END')):
                all_vars.add(instr.result)
        
        for var in all_vars:
            if var and not str(var).startswith(('L', 'ELSE', 'ENDIF', 'WHILE', 'FOR')):
                self._emit(f"    {var}: resq 1")
        
        self._emit("")
        
        # Text section
        self._emit("section .text")
        self._emit("global main")
        self._emit("")
        
        # Generate code for each instruction
        for instr in instructions:
            self._generate_x86_instruction(instr)
        
        return "\n".join(self.output)
    
    def _generate_x86_instruction(self, instr):
        """Generate x86 assembly for a single IR instruction"""
        
        if instr.op == 'FUNC_BEGIN':
            self._emit(f"{instr.arg1}:")
            self._emit("    push rbp")
            self._emit("    mov rbp, rsp")
            self._emit("    sub rsp, 256")  # Reserve stack space
            self.stack_offset = 0
        
        elif instr.op == 'FUNC_END':
            self._emit("    mov rsp, rbp")
            self._emit("    pop rbp")
            self._emit("    ret")
            self._emit("")
        
        elif instr.op == 'LABEL':
            self._emit(f"{instr.arg1}:")
        
        elif instr.op in ['DECLARE', 'PARAM_DECLARE']:
            # Variable declarations handled in BSS section
            pass
        
        elif instr.op == 'ASSIGN':
            src = self._get_x86_operand(instr.arg1)
            dst = self._get_x86_operand(instr.result, is_dest=True)
            self._emit(f"    mov rax, {src}")
            self._emit(f"    mov {dst}, rax")
        
        elif instr.op == 'ADD':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    add rax, {self._get_x86_operand(instr.arg2)}")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'SUB':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    sub rax, {self._get_x86_operand(instr.arg2)}")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'MUL':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    imul rax, {self._get_x86_operand(instr.arg2)}")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'DIV':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit("    cqo")
            self._emit(f"    mov rbx, {self._get_x86_operand(instr.arg2)}")
            self._emit("    idiv rbx")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'MOD':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit("    cqo")
            self._emit(f"    mov rbx, {self._get_x86_operand(instr.arg2)}")
            self._emit("    idiv rbx")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rdx")
        
        elif instr.op in ['EQ', 'NE', 'LT', 'GT', 'LE', 'GE']:
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    cmp rax, {self._get_x86_operand(instr.arg2)}")
            
            cond_map = {
                'EQ': 'sete', 'NE': 'setne',
                'LT': 'setl', 'GT': 'setg',
                'LE': 'setle', 'GE': 'setge'
            }
            self._emit(f"    {cond_map[instr.op]} al")
            self._emit("    movzx rax, al")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'AND':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    and rax, {self._get_x86_operand(instr.arg2)}")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'OR':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit(f"    or rax, {self._get_x86_operand(instr.arg2)}")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'NOT':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit("    test rax, rax")
            self._emit("    sete al")
            self._emit("    movzx rax, al")
            self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'IF_FALSE':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit("    test rax, rax")
            self._emit(f"    jz {instr.result}")
        
        elif instr.op == 'IF_TRUE':
            self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            self._emit("    test rax, rax")
            self._emit(f"    jnz {instr.result}")
        
        elif instr.op == 'GOTO':
            self._emit(f"    jmp {instr.arg1}")
        
        elif instr.op == 'PARAM':
            self._pending_params.append(instr.arg1)
        
        elif instr.op == 'CALL':
            # x86-64 calling convention: rdi, rsi, rdx, rcx, r8, r9
            param_regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
            params = self._pending_params.copy()
            self._pending_params = []
            
            # Set up parameters
            for i, param in enumerate(params):
                if i < len(param_regs):
                    if str(param).startswith('STR'):
                        self._emit(f"    lea {param_regs[i]}, [{param}]")
                    else:
                        self._emit(f"    mov {param_regs[i]}, {self._get_x86_operand(param)}")
            
            # Call function
            self._emit(f"    xor rax, rax")  # Clear rax for variadic functions
            self._emit(f"    call {instr.arg1}")
            
            # Store result
            if instr.result:
                self._emit(f"    mov {self._get_x86_operand(instr.result, True)}, rax")
        
        elif instr.op == 'RETURN':
            if instr.arg1:
                self._emit(f"    mov rax, {self._get_x86_operand(instr.arg1)}")
            else:
                self._emit("    xor rax, rax")
            self._emit("    mov rsp, rbp")
            self._emit("    pop rbp")
            self._emit("    ret")
    
    def _get_x86_operand(self, operand, is_dest=False):
        """Convert IR operand to x86 operand"""
        if operand is None:
            return "0"
        
        operand_str = str(operand)
        
        # Numeric constant
        try:
            float(operand_str)
            return operand_str
        except ValueError:
            pass
        
        # String literal reference
        if operand_str.startswith('STR'):
            return operand_str
        
        # Temporary or variable - use memory
        if operand_str.startswith('t'):
            # Temporaries on stack
            if operand_str not in self.variables:
                self.stack_offset += 8
                self.variables[operand_str] = self.stack_offset
            return f"qword [rbp-{self.variables[operand_str]}]"
        else:
            # Named variables in BSS
            return f"qword [{operand_str}]"
    
    def _emit(self, line):
        """Add a line to output"""
        self.output.append(line)


if __name__ == "__main__":
    print("✅ Code Generator module loaded successfully!")