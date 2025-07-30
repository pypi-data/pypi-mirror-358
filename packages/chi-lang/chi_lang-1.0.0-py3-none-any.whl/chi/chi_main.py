#!/usr/bin/env python3
"""
Chi Programming Language Interpreter
A Chichewa-inspired programming language with intuitive syntax

Usage: chi <filename.chi>
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) != 2:
        print("Chi Programming Language v1.0")
        print("Usage: chi <filename.chi>")
        print("")
        print("Examples:")
        print("  chi hello.chi")
        print("  chi examples/chi_language_introduction.chi")
        sys.exit(1)

    filename = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    # Check if file has .chi extension
    if not filename.endswith('.chi'):
        print(f"Warning: File '{filename}' does not have .chi extension.")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Tokenize
        tokens = tokenize(code)
        
        # Parse
        parser = Parser(tokens)
        statements = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.interpret(statements)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

