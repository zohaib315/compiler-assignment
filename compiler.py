# ==================== compiler.py ====================
# Complete Mini-C Compiler
# Integrates: Lexer → Parser → Semantic → IR → Optimizer → CodeGen

import sys
import subprocess
import os
from lexer import Lexer
from ParserV2 import Parser, print_ast
from semantic import SemanticAnalyzer, SemanticError
from ir_generator import IRGenerator
from optimizer import Optimizer
from code_generator import CodeGenerator


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                     MINI-C COMPILER v2.0                        ║
║                                                                  ║
║  Phases: Lexer → Parser → Semantic → IR → Optimizer → CodeGen   ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def compile_and_run_c(c_file, base_name):
    """Compile C code with GCC and execute it"""
    print("\n" + "=" * 70)
    print("PHASE 7: COMPILATION & EXECUTION (GCC)")
    print("=" * 70)
    
    # Determine executable name based on OS
    if os.name == 'nt':  # Windows
        exe_file = f"{base_name}.exe"
    else:  # Linux/Mac
        exe_file = f"{base_name}"
    
    # Compile with GCC
    print(f"Compiling {c_file} with GCC...")
    compile_cmd = ['gcc', c_file, '-o', exe_file]
    
    try:
        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"GCC Compilation failed!")
            print(f"\nGCC Errors:")
            print(result.stderr)
            return False
        
        print(f"Compilation successful: {exe_file}")
        
        # Execute the compiled program
        print(f"\n{'─' * 70}")
        print("PROGRAM OUTPUT:")
        print('─' * 70)
        
        if os.name == 'nt':  # Windows
            exec_cmd = [exe_file]
        else:  # Linux/Mac
            exec_cmd = [f'./{exe_file}']
        
        exec_result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Print program output
        if exec_result.stdout:
            print(exec_result.stdout)
        if exec_result.stderr:
            print("STDERR:", exec_result.stderr)
        
        print('─' * 70)
        print(f"Program exited with code: {exec_result.returncode}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("Execution timeout (program took too long)")
        return False
    except FileNotFoundError:
        print("GCC not found! Please install GCC:")
        print("   - Linux: sudo apt-get install gcc")
        print("   - Mac: xcode-select --install")
        print("   - Windows: Install MinGW or use WSL")
        return False
    except Exception as e:
        print(f"Error during compilation/execution: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file.mini> [options]")
        print("\nOptions:")
        print("  -O0          No optimization")
        print("  -O1          Basic optimization")
        print("  -O2          Full optimization (default)")
        print("  --target=x86 Generate x86-64 assembly (default)")
        print("  --target=c   Generate C code")
        print("  --ast        Show AST only")
        print("  --ir         Show IR only")
        print("  --all        Show all phases")
        print("  --run        Compile and run C code (only for --target=c)")
        print("  --no-run     Don't compile/run C code (default for --target=c)")
        return

    # Parse command line arguments
    source_file = sys.argv[1]
    opt_level = 2  # Default optimization level
    target = 'x86'  # Default target
    show_ast = False
    show_ir = False
    show_all = False
    auto_run = False
    
    for arg in sys.argv[2:]:
        if arg == '-O0':
            opt_level = 0
        elif arg == '-O1':
            opt_level = 1
        elif arg == '-O2':
            opt_level = 2
        elif arg == '--target=x86':
            target = 'x86'
        elif arg == '--target=c':
            target = 'c'
        elif arg == '--ast':
            show_ast = True
        elif arg == '--ir':
            show_ir = True
        elif arg == '--all':
            show_all = True
        elif arg == '--run':
            auto_run = True
        elif arg == '--no-run':
            auto_run = False

    print_banner()

    # =====================================================
    # PHASE 1: LEXICAL ANALYSIS
    # =====================================================
    print("=" * 70)
    print("PHASE 1: LEXICAL ANALYSIS")
    print("=" * 70)
    
    try:
        lexer = Lexer(source_file)
        lexer.tokenize()
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
        return
    except Exception as e:
        print(f"Lexer Error: {e}")
        return

    if lexer.errors:
        print("\nLEXICAL ERRORS:")
        for err in lexer.errors:
            print(f"   {err}")
        return
    else:
        print(f"Lexical analysis completed. ({len(lexer.get_tokens())} tokens)")

    # =====================================================
    # PHASE 2: SYNTAX ANALYSIS (PARSING)
    # =====================================================
    print("\n" + "=" * 70)
    print("PHASE 2: SYNTAX ANALYSIS (PARSING)")
    print("=" * 70)
    
    tokens = lexer.get_tokens()
    parser = Parser(tokens)
    ast = parser.parse()

    if parser.errors:
        print("\n SYNTAX ERRORS:")
        for err in parser.errors:
            print(f"   {err}")
        return
    else:
        print(f"Parsing completed successfully.")

    if show_ast or show_all:
        print("\n" + "-" * 70)
        print("ABSTRACT SYNTAX TREE:")
        print("-" * 70)
        print_ast(ast)

    # =====================================================
    # PHASE 3: SEMANTIC ANALYSIS
    # =====================================================
    print("\n" + "=" * 70)
    print("PHASE 3: SEMANTIC ANALYSIS")
    print("=" * 70)
    
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        print("Semantic analysis completed successfully.")
    except SemanticError as e:
        print(f"SEMANTIC ERRORS:{e}")
        return

    # =====================================================
    # PHASE 4: INTERMEDIATE REPRESENTATION (IR) GENERATION
    # =====================================================
    print("\n" + "=" * 70)
    print("PHASE 4: IR GENERATION (Three-Address Code)")
    print("=" * 70)
    
    ir_gen = IRGenerator()
    ir_instructions = ir_gen.generate(ast)
    
    print(f"IR generated. ({len(ir_instructions)} instructions)")
    
    if show_ir or show_all:
        print("\n" + "-" * 70)
        print("UNOPTIMIZED IR:")
        print("-" * 70)
        for instr in ir_instructions:
            print(f"   {instr}")

    # =====================================================
    # PHASE 5: CODE OPTIMIZATION
    # =====================================================
    print("\n" + "=" * 70)
    print(f"PHASE 5: CODE OPTIMIZATION (Level: O{opt_level})")
    print("=" * 70)
    
    optimizer = Optimizer(optimization_level=opt_level)
    optimized_ir = optimizer.optimize(ir_instructions)
    
    reduced = len(ir_instructions) - len(optimized_ir)
    print(f"Optimization completed. ({len(optimized_ir)} instructions, {reduced} removed)")
    
    if opt_level > 0:
        optimizer.print_stats()
    
    if show_all:
        print("\n" + "-" * 70)
        print("OPTIMIZED IR:")
        print("-" * 70)
        for instr in optimized_ir:
            print(f"   {instr}")

    # =====================================================
    # PHASE 6: TARGET CODE GENERATION
    # =====================================================
    print("\n" + "=" * 70)
    print(f"PHASE 6: CODE GENERATION (Target: {target.upper()})")
    print("=" * 70)
    
    code_gen = CodeGenerator(target=target)
    target_code = code_gen.generate(
        optimized_ir, 
        string_literals=ir_gen.string_literals,
        var_types=ir_gen.var_types
    )
    
    # Determine output file name
    base_name = source_file.rsplit('.', 1)[0]
    if target == 'x86':
        output_file = f"{base_name}.asm"
    else:
        output_file = f"{base_name}.c"
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write(target_code)
    
    print(f"Code generation completed.")
    print(f"Output written to: {output_file}")

    # =====================================================
    # PHASE 7: COMPILE AND RUN (C target only)
    # =====================================================
    if target == 'c' and auto_run:
        compile_and_run_c(output_file, base_name)

    # =====================================================
    # COMPILATION SUMMARY
    # =====================================================
    print("\n" + "=" * 70)
    print("COMPILATION SUMMARY")
    print("=" * 70)
    print(f"""
    Source File     : {source_file}
    Output File     : {output_file}
    Target          : {target.upper()}
    Optimization    : O{opt_level}
    
    Tokens          : {len(lexer.get_tokens())}
    IR Instructions : {len(ir_instructions)} → {len(optimized_ir)} (optimized)
    
    Status          : ✅ SUCCESS
    """)

    # Show generated code
    if show_all:
        print("-" * 70)
        print(f"GENERATED {target.upper()} CODE:")
        print("-" * 70)
        print(target_code)

    # Write additional output files
    lexer.write_tokens_file()
    lexer.write_symbol_table()
    
    # Write IR to file
    with open(f"{base_name}_ir.txt", 'w') as f:
        f.write("UNOPTIMIZED IR:\n")
        f.write("-" * 40 + "\n")
        for instr in ir_instructions:
            f.write(f"{instr}\n")
        f.write("\n\nOPTIMIZED IR:\n")
        f.write("-" * 40 + "\n")
        for instr in optimized_ir:
            f.write(f"{instr}\n")
    
    print(f"\n Additional files generated:")
    print(f"   - tokens.txt")
    print(f"   - symbol_table.txt")
    print(f"   - {base_name}_ir.txt")
    
    if target == 'c' and not auto_run:
        print(f"\n Tip: Use --run flag to automatically compile and execute")
        print(f"   Example: python compiler.py {source_file} --target=c --run")


if __name__ == "__main__":
    main()