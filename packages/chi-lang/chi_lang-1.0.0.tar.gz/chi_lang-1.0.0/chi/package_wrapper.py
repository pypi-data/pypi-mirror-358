"""
Chi Language Package Wrapper

This module provides a clean interface for the chi-lang package
without modifying the original Chi interpreter code.

Author: Duncan Masiye
"""

import sys
import os
import traceback
from pathlib import Path

# Import everything from the original interpreter
from .interpreter import *
from .lexer import tokenize
from .parser import Parser

class ChiInterpreterWrapper:
    """
    Package wrapper for the Chi interpreter.
    
    This class provides a clean interface for the chi-lang package
    while using the original Chi interpreter code unchanged.
    """
    
    def __init__(self, verbose: bool = False, debug: bool = False):
        """
        Initialize the Chi interpreter wrapper.
        
        Args:
            verbose (bool): Enable verbose output
            debug (bool): Enable debug mode
        """
        self.verbose = verbose
        self.debug = debug
        self.interpreter = Interpreter()  # Original interpreter
        
    def run_code(self, code: str):
        """
        Execute Chi code directly.
        
        Args:
            code (str): Chi code to execute
        """
        if self.verbose:
            print(f"Executing Chi code: {code[:50]}{'...' if len(code) > 50 else ''}")
        
        try:
            # Use original tokenizer and parser
            tokens = tokenize(code)
            if self.debug:
                print(f"Tokens: {tokens}")
            
            parser = Parser(tokens)
            ast = parser.parse()
            if self.debug:
                print(f"AST: {ast}")
            
            # Use original interpreter
            self.interpreter.interpret(ast)
                
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            raise e
    
    def run_file(self, filename: str):
        """
        Execute a Chi file.
        
        Args:
            filename (str): Path to the Chi file
        """
        if self.verbose:
            print(f"Running Chi file: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            self.run_code(code)
        except FileNotFoundError:
            raise FileNotFoundError(f"Chi file not found: {filename}")
        except Exception as e:
            raise e
    
    def get_environment(self):
        """Get access to the interpreter environment."""
        return self.interpreter.env

# Create aliases for backwards compatibility and ease of use
ChiRunner = ChiInterpreterWrapper
ChiExecutor = ChiInterpreterWrapper

# Export the wrapper as the main Interpreter for the package
PackageInterpreter = ChiInterpreterWrapper
