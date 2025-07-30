#!/usr/bin/env python3
"""
Chi Programming Language Command Line Interface

Provides the main CLI for the Chi programming language.

Author: Duncan Masiye
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from . import __version__, __author__
from .interpreter import Interpreter
from . import translator


def get_examples_directory() -> Path:
    """Get the path to the examples directory."""
    # Get the package directory
    package_dir = Path(__file__).parent
    examples_dir = package_dir / "examples" / "chi_files"
    
    # If not found, try relative to package
    if not examples_dir.exists():
        examples_dir = package_dir.parent / "examples" / "chi_files"
    
    return examples_dir


def list_available_examples() -> dict:
    """Get a list of available example files organized by category."""
    examples_dir = get_examples_directory()
    
    if not examples_dir.exists():
        return {}
    
    # Categorized examples
    categories = {
        "Basic Examples": [
            "hello_world.chi",
            "simple_data_types.chi",
            "simple_math.chi", 
            "type_constructors.chi",
            "operators_demo.chi"
        ],
        "Data Structures": [
            "simple_lists.chi",
            "list_operations_demo.chi",
            "dictionary_operations_demo.chi",
            "string_methods_demo.chi"
        ],
        "Control Flow": [
            "control_structures_demo.chi"
        ],
        "Functions": [
            "functions_demo.chi",
            "builtin_functions_demo.chi"
        ],
        "Advanced Features": [
            "exception_handling_demo.chi",
            "file_operations_demo.chi"
        ],
        "Real-World Applications": [
            "real_world_app_demo.chi"
        ]
    }
    
    # Filter to only include files that actually exist
    available_examples = {}
    for category, files in categories.items():
        existing_files = []
        for file in files:
            if (examples_dir / file).exists():
                existing_files.append(file)
        if existing_files:
            available_examples[category] = existing_files
    
    return available_examples


def print_available_examples():
    """Print the list of available examples."""
    examples = list_available_examples()
    
    if not examples:
        print("No examples found.")
        return
    
    print("Available Chi Examples:")
    print("=" * 40)
    
    for category, files in examples.items():
        print(f"\n{category}:")
        for file in files:
            # Remove .chi extension for display
            name = file.replace('.chi', '')
            print(f"  • {name}")
    
    print(f"\nUsage: chi run --example <example_name>")
    print(f"Example: chi run --example hello_world")


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="chi",
        description="Chi Programming Language - A Chichewa-inspired programming language",
        epilog=f"Author: {__author__} | Version: {__version__}"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Chi {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a Chi program file")
    run_parser.add_argument("file", nargs='?', help="Chi file to execute")
    run_parser.add_argument("--verbose", "-V", action="store_true", help="Enable verbose output")
    run_parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    run_parser.add_argument("--example", "-e", metavar="EXAMPLE_NAME", help="Run a built-in example")
    run_parser.add_argument("--list-examples", action="store_true", help="List available examples")
    run_parser.add_argument("--see", "-s", metavar="EXAMPLE_NAME", help="Show contents of an example file")
    
    # Exec command
    exec_parser = subparsers.add_parser("exec", help="Execute Chi code directly")
    exec_parser.add_argument("code", help="Chi code to execute")
    exec_parser.add_argument("--verbose", "-V", action="store_true", help="Enable verbose output")
    exec_parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate between Chi and Python")
    translate_parser.add_argument("input", help="Input file or code string")
    translate_parser.add_argument("--from", "-f", dest="source_lang", 
                                choices=["chi", "python"], default="chi",
                                help="Source language (default: chi)")
    translate_parser.add_argument("--to", "-t", dest="target_lang",
                                choices=["chi", "python"], default="python", 
                                help="Target language (default: python)")
    translate_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    translate_parser.add_argument("--no-imports", action="store_true", 
                                help="Don't include imports (Chi to Python only)")
    
    # REPL command
    repl_parser = subparsers.add_parser("repl", help="Start interactive Chi REPL")
    repl_parser.add_argument("--verbose", "-V", action="store_true", help="Enable verbose output")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show Chi language information")
    info_parser.add_argument("--translators", action="store_true", help="Show translator information")
    
    return parser


def run_file_command(args) -> int:
    """Execute the run file command."""
    
    # Handle --list-examples
    if args.list_examples:
        print_available_examples()
        return 0
    
    # Handle --see
    if args.see:
        examples_dir = get_examples_directory()
        example_file = args.see
        
        # Add .chi extension if not present
        if not example_file.endswith('.chi'):
            example_file += '.chi'
        
        file_path = examples_dir / example_file
        
        if not file_path.exists():
            print(f"Error: Example '{args.see}' not found.", file=sys.stderr)
            print("Use 'chi run --list-examples' to see available examples.", file=sys.stderr)
            return 1
        
        # Display the file contents
        print(f"=== {args.see} ===")
        print(f"File: {file_path}")
        print("=" * 50)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    # Handle --example
    if args.example:
        examples_dir = get_examples_directory()
        example_file = args.example
        
        # Add .chi extension if not present
        if not example_file.endswith('.chi'):
            example_file += '.chi'
        
        file_path = examples_dir / example_file
        
        if not file_path.exists():
            print(f"Error: Example '{args.example}' not found.", file=sys.stderr)
            print("Use 'chi run --list-examples' to see available examples.", file=sys.stderr)
            return 1
            
        if args.verbose:
            print(f"Running example: {args.example}")
    
    # Handle regular file
    elif args.file:
        file_path = Path(args.file)
        
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            return 1
        
        if not file_path.suffix.lower() in ['.chi', '.txt']:
            print(f"Warning: File '{args.file}' doesn't have a .chi extension.", file=sys.stderr)
    
    else:
        print("Error: Must specify either a file or use --example flag.", file=sys.stderr)
        print("Use 'chi run --help' for usage information.", file=sys.stderr)
        return 1
    
    try:
        from .interpreter import Interpreter
        from .lexer import tokenize
        from .parser import Parser
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if args.verbose:
            print(f"Executing Chi file: {file_path}")
        
        # Tokenize, parse, and interpret
        tokens = tokenize(code)
        if args.debug:
            print(f"Tokens: {tokens}")
        
        parser = Parser(tokens)
        ast = parser.parse()
        if args.debug:
            print(f"AST: {ast}")
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        return 0
    except Exception as e:
        print(f"Error executing file: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def exec_code_command(args) -> int:
    """Execute the exec code command."""
    try:
        from .interpreter import Interpreter
        from .lexer import tokenize
        from .parser import Parser
        
        if args.verbose:
            print(f"Executing Chi code: {args.code[:50]}{'...' if len(args.code) > 50 else ''}")
        
        # Tokenize, parse, and interpret
        tokens = tokenize(args.code)
        if args.debug:
            print(f"Tokens: {tokens}")
        
        parser = Parser(tokens)
        ast = parser.parse()
        if args.debug:
            print(f"AST: {ast}")
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        return 0
    except Exception as e:
        print(f"Error executing code: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def translate_command(args) -> int:
    """Execute the translate command."""
    try:
        # Determine if input is a file or code string
        input_path = Path(args.input)
        
        if args.source_lang == "chi" and args.target_lang == "python":
            # Use the working translate_file method for files, or process code strings directly
            if input_path.exists():
                # It's a file - use the working translate_file method
                from .chi_to_py_final import ChiToPythonTranslator
                chi_translator = ChiToPythonTranslator()
                
                if args.output:
                    # Translate to specified output file
                    success = chi_translator.translate_file(str(input_path), args.output)
                    if success:
                        print(f"Translation saved to: {args.output}")
                        return 0
                    else:
                        print("Translation failed", file=sys.stderr)
                        return 1
                else:
                    # Translate to stdout by creating temp file then reading it
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
                        success = chi_translator.translate_file(str(input_path), temp_file.name)
                        if success:
                            temp_file.seek(0)
                            with open(temp_file.name, 'r') as f:
                                result = f.read()
                            os.unlink(temp_file.name)
                            print(result)
                            return 0
                        else:
                            os.unlink(temp_file.name)
                            print("Translation failed", file=sys.stderr)
                            return 1
            else:
                # It's a code string - process line by line using working method
                from .chi_to_py_final import ChiToPythonTranslator
                chi_translator = ChiToPythonTranslator()
                chi_translator.reset_imports()
                
                code = args.input
                lines = code.split('\n')
                translated_lines = []
                
                for line in lines:
                    if line.strip():
                        translated_line = chi_translator.translate_line(line)
                        translated_lines.append(translated_line)
                    else:
                        translated_lines.append('')
                
                if not args.no_imports:
                    # Generate imports and helper functions
                    imports = chi_translator.generate_imports()
                    helper_functions = chi_translator.generate_helper_functions()
                    
                    # Combine everything
                    result_parts = []
                    if imports:
                        result_parts.extend(imports)
                        result_parts.append('')
                    
                    if helper_functions:
                        result_parts.extend(helper_functions)
                        result_parts.append('')
                    
                    result_parts.extend(translated_lines)
                    result = '\n'.join(result_parts)
                else:
                    result = '\n'.join(translated_lines)
                
                # Output result
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"Translation saved to: {args.output}")
                else:
                    print(result)
                
                return 0
                
        elif args.source_lang == "python" and args.target_lang == "chi":
            # For Python to Chi, use the translator module (this works)
            if input_path.exists():
                with open(input_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                code = args.input
            
            result = translator.py_to_chi(code)
            
            # Output result
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Translation saved to: {args.output}")
            else:
                print(result)
            
            return 0
        else:
            print(f"Error: Unsupported translation direction: {args.source_lang} -> {args.target_lang}", 
                  file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"Error during translation: {e}", file=sys.stderr)
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1


def repl_command(args) -> int:
    """Execute the REPL command with enhanced features."""
    print(f"Chi Programming Language REPL {__version__}")
    print(f"Author: {__author__}")
    print("Type 'exit()', 'quit()', 'help()' or press Ctrl+C to quit.")
    print("Commands: 'examples()', 'clear()', 'version()'\n")
    
    from .interpreter import Interpreter
    from .lexer import tokenize
    from .parser import Parser
    
    interpreter = Interpreter()
    command_history = []
    
    def show_help():
        """Show REPL help."""
        print("Chi REPL Commands:")
        print("  help()     - Show this help")
        print("  examples() - List available examples")
        print("  clear()    - Clear screen")
        print("  version()  - Show version info")
        print("  history()  - Show command history")
        print("  exit()     - Exit REPL")
        print("\nChi Language Quick Reference:")
        print("  ika x = 5           # Variable assignment")
        print("  onetsa(\"Hello\")     # Print output")
        print("  ika list = ndandanda(1, 2, 3)  # Create list")
        print("  ngati x > 0: ...    # If statement")
    
    def show_examples():
        """Show available examples."""
        examples = list_available_examples()
        if examples:
            print("Available Examples:")
            for category, files in examples.items():
                print(f"\n{category}:")
                for file in files:
                    name = file.replace('.chi', '')
                    print(f"  • {name}")
            print(f"\nRun: chi run --example <name>")
        else:
            print("No examples found.")
    
    def clear_screen():
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_history():
        """Show command history."""
        if command_history:
            print("Command History:")
            for i, cmd in enumerate(command_history[-10:], 1):  # Show last 10
                print(f"  {i:2d}. {cmd}")
        else:
            print("No command history.")
    
    while True:
        try:
            code = input("chi> ").strip()
            
            if not code:
                continue
                
            # Handle special commands
            if code.lower() in ['exit()', 'quit()', 'exit', 'quit']:
                print("Tiwonana! (Goodbye!)")
                break
            elif code.lower() in ['help()', 'help']:
                show_help()
                continue
            elif code.lower() in ['examples()', 'examples']:
                show_examples()
                continue
            elif code.lower() in ['clear()', 'clear']:
                clear_screen()
                continue
            elif code.lower() in ['version()', 'version']:
                print(f"Chi Programming Language {__version__}")
                print(f"Author: {__author__}")
                continue
            elif code.lower() in ['history()', 'history']:
                show_history()
                continue
            
            # Add to history
            command_history.append(code)
            
            try:
                # Tokenize and parse the input
                tokens = tokenize(code)
                parser = Parser(tokens)
                statements = parser.parse()
                
                # Execute the statements
                interpreter.interpret(statements)
                
            except Exception as e:
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Error: {e}")
                    
        except KeyboardInterrupt:
            print("\n\nTiwonana! (Goodbye!)")
            break
        except EOFError:
            print("\nTiwonana! (Goodbye!)")
            break
    
    return 0


def info_command(args) -> int:
    """Execute the info command."""
    print(f"Chi Programming Language {__version__}")
    print(f"Author: {__author__}")
    print("\nA modern, intuitive programming language inspired by Chichewa")
    print("with seamless Python interoperability.\n")
    
    if args.translators:
        print("Translator Information:")
        print("=" * 50)
        info = translator.get_translation_info()
        
        for direction, details in info.items():
            if direction != "supported_directions":
                print(f"\n{direction.replace('_', ' ').title()}:")
                print(f"  Available: {'Yes' if details['available'] else 'No'}")
                if details['available']:
                    print("  Features:")
                    for feature in details['features']:
                        print(f"    • {feature}")
        
        print(f"\nSupported Translation Directions:")
        for direction in info['supported_directions']:
            print(f"  • {direction}")
    
    print("\nUsage Examples:")
    print("  chi run hello.chi           # Run a Chi program")
    print("  chi exec 'sikosa \"Hello!\"'  # Execute Chi code directly")
    print("  chi translate code.chi      # Translate Chi to Python")
    print("  chi repl                    # Start interactive REPL")
    
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to appropriate command handler
    if args.command == "run":
        return run_file_command(args)
    elif args.command == "exec":
        return exec_code_command(args)
    elif args.command == "translate":
        return translate_command(args)
    elif args.command == "repl":
        return repl_command(args)
    elif args.command == "info":
        return info_command(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
