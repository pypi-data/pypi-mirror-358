"""
Chi Programming Language

A modern, intuitive programming language inspired by Chichewa 
with seamless Python interoperability.

Author: Duncan Masiye
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Duncan Masiye"
__email__ = "duncan.masiye16@gmail.com"

# Import main components for easy access
from .interpreter import Interpreter
from .lexer import tokenize
from .parser import Parser
from . import translator
from . import examples

# Main API
def run_file(filename: str, verbose: bool = False):
    """Run a Chi file."""
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    return run_code(code, verbose)

def run_code(code: str, verbose: bool = False):
    """Execute Chi code directly."""
    if verbose:
        print(f"Executing Chi code: {code[:50]}{'...' if len(code) > 50 else ''}")
    
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    return interpreter.interpret(ast)

# Convenience aliases
execute = run_code
run = run_file

__all__ = [
    "Interpreter",
    "tokenize", 
    "Parser",
    "translator",
    "run_file",
    "run_code",
    "execute",
    "run",
    "__version__",
    "__author__",
    "__email__"
]
