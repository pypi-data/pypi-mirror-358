#!/usr/bin/env python3
"""
Chi Programming Language - Examples Module

This module provides access to Chi example files and can execute them within Python.

Author: Duncan Masiye
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from .interpreter import Interpreter
from .lexer import tokenize
from .parser import Parser


def get_examples_directory() -> Path:
    """Get the path to the examples directory."""
    package_dir = Path(__file__).parent
    examples_dir = package_dir / "examples" / "chi_files"
    
    # If not found, try relative to package
    if not examples_dir.exists():
        examples_dir = package_dir.parent / "examples" / "chi_files"
    
    return examples_dir


def list_examples() -> List[str]:
    """Get a list of all available example files."""
    examples_dir = get_examples_directory()
    
    if not examples_dir.exists():
        return []
    
    # Get all .chi files
    chi_files = []
    for file_path in examples_dir.glob("*.chi"):
        # Remove .chi extension for the name
        example_name = file_path.stem
        chi_files.append(example_name)
    
    return sorted(chi_files)


def get_example_content(example_name: str) -> str:
    """Get the content of an example file."""
    examples_dir = get_examples_directory()
    
    # Add .chi extension if not present
    if not example_name.endswith('.chi'):
        example_name += '.chi'
    
    file_path = examples_dir / example_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Example '{example_name}' not found")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def run_example(example_name: str, capture_output: bool = False) -> Optional[str]:
    """
    Run a Chi example and optionally capture its output.
    
    Args:
        example_name: Name of the example (without .chi extension)
        capture_output: If True, capture and return output instead of printing
    
    Returns:
        Output string if capture_output=True, None otherwise
    """
    examples_dir = get_examples_directory()
    
    # Add .chi extension if not present
    if not example_name.endswith('.chi'):
        example_name += '.chi'
    
    file_path = examples_dir / example_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Example '{example_name}' not found")
    
    # Read and execute the file
    with open(file_path, 'r', encoding='utf-8') as f:
        chi_code = f.read()
    
    if capture_output:
        # Capture output by redirecting stdout
        import io
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                # Tokenize and parse
                tokens = tokenize(chi_code)
                parser = Parser(tokens)
                statements = parser.parse()
                
                # Execute
                interpreter = Interpreter()
                interpreter.interpret(statements)
            
            return output_buffer.getvalue()
        except Exception as e:
            return f"Error executing example: {e}"
    else:
        try:
            # Tokenize and parse
            tokens = tokenize(chi_code)
            parser = Parser(tokens)
            statements = parser.parse()
            
            # Execute
            interpreter = Interpreter()
            interpreter.interpret(statements)
        except Exception as e:
            print(f"Error executing example: {e}", file=sys.stderr)


class ChiExample:
    """
    A class representing a single Chi example that can be imported and executed.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._content = None
        self._loaded = False
    
    @property
    def content(self) -> str:
        """Get the Chi source code content."""
        if not self._loaded:
            self._content = get_example_content(self.name)
            self._loaded = True
        return self._content
    
    def run(self, capture_output: bool = False) -> Optional[str]:
        """Run this example."""
        return run_example(self.name, capture_output)
    
    def show(self) -> None:
        """Print the source code of this example."""
        print(f"=== Chi Example: {self.name} ===")
        print(self.content)
    
    def __repr__(self) -> str:
        return f"ChiExample('{self.name}')"
    
    def __str__(self) -> str:
        return f"Chi example: {self.name}"


# Create example instances dynamically
class ExamplesModule:
    """
    Dynamic module for accessing Chi examples as attributes.
    """
    
    def __getattr__(self, name: str) -> ChiExample:
        """Get an example by name."""
        available_examples = list_examples()
        
        if name in available_examples:
            return ChiExample(name)
        else:
            raise AttributeError(f"Example '{name}' not found. Available examples: {available_examples}")
    
    def __dir__(self) -> List[str]:
        """List all available examples."""
        return list_examples()
    
    def list(self) -> List[str]:
        """List all available examples."""
        return list_examples()
    
    def help(self) -> None:
        """Show help information about available examples."""
        examples = list_examples()
        print("Available Chi Examples:")
        print("=" * 30)
        
        for example in examples:
            print(f"  • {example}")
        
        print(f"\nUsage:")
        print(f"  from chi.examples import hello_world")
        print(f"  hello_world.run()  # Execute the example")
        print(f"  hello_world.show() # Show source code")
        print(f"  hello_world.content # Get source as string")


# Create the module instance
sys.modules[__name__] = ExamplesModule()
