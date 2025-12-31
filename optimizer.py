# ==================== optimizer.py ====================
# Code Optimizer - FIXED VERSION

from ir_generator import IRInstruction


class Optimizer:
    """
    Performs optimization passes on Three-Address Code
    FIXED: Don't evaluate comparisons involving variables at compile time
    """
    
    def __init__(self, optimization_level=2):
        self.level = optimization_level
        self.constants = {}
        self.stats = {
            'constant_folding': 0,
            'constant_propagation': 0,
            'dead_code_eliminated': 0,
            'strength_reduction': 0,
        }
    
    def optimize(self, instructions):
        """Main optimization entry point"""
        if self.level == 0:
            return instructions
        
        optimized = instructions.copy()
        
        # Reset
        self.constants = {}
        
        # Run optimization passes
        if self.level >= 1:
            optimized = self._constant_folding(optimized)
            optimized = self._dead_code_elimination(optimized)
        
        if self.level >= 2:
            optimized = self._strength_reduction(optimized)
        
        return optimized
    
    def _constant_folding(self, instructions):
        """
        Evaluate constant expressions at compile time
        FIXED: Only fold when BOTH operands are literal constants
        """
        result = []
        
        for instr in instructions:
            # Only fold arithmetic operations with TWO LITERAL constants
            if instr.op in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']:
                arg1_val = self._get_literal_value(instr.arg1)
                arg2_val = self._get_literal_value(instr.arg2)
                
                # Only fold if BOTH are literals (not variables)
                if arg1_val is not None and arg2_val is not None:
                    try:
                        if instr.op == 'ADD':
                            value = arg1_val + arg2_val
                        elif instr.op == 'SUB':
                            value = arg1_val - arg2_val
                        elif instr.op == 'MUL':
                            value = arg1_val * arg2_val
                        elif instr.op == 'DIV':
                            if arg2_val != 0:
                                value = arg1_val // arg2_val if isinstance(arg1_val, int) else arg1_val / arg2_val
                            else:
                                result.append(instr)
                                continue
                        elif instr.op == 'MOD':
                            if arg2_val != 0:
                                value = arg1_val % arg2_val
                            else:
                                result.append(instr)
                                continue
                        
                        # Replace with assignment
                        if isinstance(value, float) and value.is_integer():
                            value = int(value)
                        new_instr = IRInstruction('ASSIGN', str(value), result=instr.result)
                        result.append(new_instr)
                        self.constants[instr.result] = value
                        self.stats['constant_folding'] += 1
                        continue
                    except:
                        pass
            
            # Track constant assignments
            elif instr.op == 'ASSIGN':
                val = self._get_literal_value(instr.arg1)
                if val is not None:
                    self.constants[instr.result] = val
            
            # DO NOT fold comparisons - they should be evaluated at runtime
            # This fixes the "if (!1)" problem
            
            result.append(instr)
        
        return result
    
    def _dead_code_elimination(self, instructions):
        """Remove unused temporaries"""
        # Find all used variables
        used_vars = set()
        
        for instr in instructions:
            if instr.op in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE', 'AND', 'OR']:
                if instr.arg1 and not self._is_literal(instr.arg1):
                    used_vars.add(instr.arg1)
                if instr.arg2 and not self._is_literal(instr.arg2):
                    used_vars.add(instr.arg2)
            elif instr.op == 'ASSIGN':
                if instr.arg1 and not self._is_literal(instr.arg1):
                    used_vars.add(instr.arg1)
            elif instr.op in ['IF_FALSE', 'IF_TRUE']:
                if instr.arg1 and not self._is_literal(instr.arg1):
                    used_vars.add(instr.arg1)
            elif instr.op == 'RETURN':
                if instr.arg1 and not self._is_literal(instr.arg1):
                    used_vars.add(instr.arg1)
            elif instr.op == 'PARAM':
                if instr.arg1 and not self._is_literal(instr.arg1):
                    used_vars.add(instr.arg1)
        
        # Keep instructions that are used or have side effects
        result = []
        for instr in instructions:
            keep = True
            
            # Remove assignments to unused temporaries only
            if instr.op == 'ASSIGN' and instr.result:
                if instr.result.startswith('t') and instr.result not in used_vars:
                    keep = False
                    self.stats['dead_code_eliminated'] += 1
            
            if keep:
                result.append(instr)
        
        return result
    
    def _strength_reduction(self, instructions):
        """Replace expensive operations with cheaper ones"""
        result = []
        
        for instr in instructions:
            if instr.op == 'MUL':
                val = self._get_literal_value(instr.arg2)
                if val is not None:
                    if val == 0:
                        new_instr = IRInstruction('ASSIGN', '0', result=instr.result)
                        result.append(new_instr)
                        self.stats['strength_reduction'] += 1
                        continue
                    elif val == 1:
                        new_instr = IRInstruction('ASSIGN', instr.arg1, result=instr.result)
                        result.append(new_instr)
                        self.stats['strength_reduction'] += 1
                        continue
                    elif val == 2:
                        new_instr = IRInstruction('ADD', instr.arg1, instr.arg1, instr.result)
                        result.append(new_instr)
                        self.stats['strength_reduction'] += 1
                        continue
            
            elif instr.op == 'ADD':
                if self._get_literal_value(instr.arg2) == 0:
                    new_instr = IRInstruction('ASSIGN', instr.arg1, result=instr.result)
                    result.append(new_instr)
                    self.stats['strength_reduction'] += 1
                    continue
                elif self._get_literal_value(instr.arg1) == 0:
                    new_instr = IRInstruction('ASSIGN', instr.arg2, result=instr.result)
                    result.append(new_instr)
                    self.stats['strength_reduction'] += 1
                    continue
            
            result.append(instr)
        
        return result
    
    def _get_literal_value(self, val):
        """Get numeric value only if it's a LITERAL (not a variable)"""
        if val is None:
            return None
        
        val_str = str(val)
        
        # If it starts with a letter, it's a variable - don't treat as constant
        if val_str and val_str[0].isalpha():
            return None
        
        # Try to parse as number
        try:
            if '.' in val_str:
                return float(val_str)
            return int(val_str)
        except (ValueError, TypeError):
            return None
    
    def _is_literal(self, val):
        """Check if value is a literal constant"""
        return self._get_literal_value(val) is not None
    
    def get_stats(self):
        return self.stats
    
    def print_stats(self):
        print("\n" + "=" * 50)
        print("OPTIMIZATION STATISTICS")
        print("=" * 50)
        total = sum(self.stats.values())
        for name, count in self.stats.items():
            if count > 0:
                print(f"  {name.replace('_', ' ').title()}: {count}")
        print(f"  {'─' * 30}")
        print(f"  Total Optimizations: {total}")
        print("=" * 50)


# Test
if __name__ == "__main__":
    print("✅ Optimizer module loaded successfully!")