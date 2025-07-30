"""
Chi Language Translator Module

Provides bidirectional translation between Chi and Python languages.

Author: Duncan Masiye
"""

from typing import Optional, Dict, Any
import sys
import os

# Import the translator classes
try:
    from .chi_to_py_final import ChiToPythonTranslator
    from .py_to_chi import PythonToChiTranslator
except ImportError:
    # Fallback import for development
    try:
        from chi_to_py_final import ChiToPythonTranslator
        from py_to_chi import PythonToChiTranslator
    except ImportError as e:
        raise ImportError(f"Could not import translator modules: {e}")

# Global translator instances
_chi_to_py_translator = None
_py_to_chi_translator = None

def get_chi_to_py_translator():
    """Get or create the Chi to Python translator instance."""
    global _chi_to_py_translator
    if _chi_to_py_translator is None:
        _chi_to_py_translator = ChiToPythonTranslator()
    return _chi_to_py_translator

def get_py_to_chi_translator():
    """Get or create the Python to Chi translator instance."""
    global _py_to_chi_translator
    if _py_to_chi_translator is None:
        _py_to_chi_translator = PythonToChiTranslator()
    return _py_to_chi_translator

def chi_to_py(chi_code: str, include_imports: bool = True) -> str:
    """
    Translate Chi code to Python.
    
    Args:
        chi_code (str): The Chi code to translate
        include_imports (bool): Whether to include necessary imports and helper functions
        
    Returns:
        str: The translated Python code
        
    Example:
        >>> from chi import translator
        >>> python_code = translator.chi_to_py('sikosa "Hello, World!"')
        >>> print(python_code)
        print("Hello, World!")
    """
    translator = get_chi_to_py_translator()
    translator.reset_imports()
    
    lines = chi_code.split('\n')
    translated_lines = []
    
    for line in lines:
        if line.strip():
            translated_line = translator.translate_line(line)
            # Remove any trailing newlines since we'll join with newlines later
            translated_line = translated_line.rstrip('\n')
            translated_lines.append(translated_line)
        else:
            translated_lines.append('')
    
    if include_imports:
        # Generate imports and helper functions
        imports = translator.generate_imports()
        helper_functions = translator.generate_helper_functions()
        
        # Combine everything
        result = []
        if imports:
            result.extend(imports)
            result.append('')
        
        if helper_functions:
            result.extend(helper_functions)
            result.append('')
        
        result.extend(translated_lines)
        return '\n'.join(result)
    else:
        return '\n'.join(translated_lines)

def py_to_chi(python_code: str) -> str:
    """
    Translate Python code to Chi.
    
    Args:
        python_code (str): The Python code to translate
        
    Returns:
        str: The translated Chi code
        
    Example:
        >>> from chi import translator
        >>> chi_code = translator.py_to_chi('print("Hello, World!")')
        >>> print(chi_code)
        sikosa "Hello, World!"
    """
    translator = get_py_to_chi_translator()
    
    lines = python_code.split('\n')
    translated_lines = []
    
    for line in lines:
        if line.strip():
            translated_line = translator.translate_line(line)
            if translated_line.strip():
                translated_lines.append(translated_line)
        else:
            translated_lines.append('')
    
    return '\n'.join(translated_lines)

def translate(code: str, source_lang: str = "chi", target_lang: str = "python", **kwargs) -> str:
    """
    Generic translation function.
    
    Args:
        code (str): The source code to translate
        source_lang (str): Source language ("chi" or "python")
        target_lang (str): Target language ("chi" or "python")
        **kwargs: Additional arguments passed to specific translators
        
    Returns:
        str: The translated code
        
    Raises:
        ValueError: If invalid language combination is specified
    """
    source_lang = source_lang.lower()
    target_lang = target_lang.lower()
    
    if source_lang == "chi" and target_lang == "python":
        return chi_to_py(code, **kwargs)
    elif source_lang == "python" and target_lang == "chi":
        return py_to_chi(code, **kwargs)
    else:
        raise ValueError(f"Unsupported translation: {source_lang} -> {target_lang}")

def get_translation_info() -> Dict[str, Any]:
    """
    Get information about available translators.
    
    Returns:
        dict: Information about translators and supported features
    """
    return {
        "chi_to_python": {
            "available": _chi_to_py_translator is not None or ChiToPythonTranslator is not None,
            "features": [
                "Variable declarations (ika)",
                "Function definitions (ntchito)",
                "Conditional statements (ngati/sizoona)",
                "Loops (bwereza)",
                "List operations (ndandanda)",
                "Arithmetic operations",
                "Boolean operations (komanso/kapena/osati)",
                "String operations",
                "Type conversions"
            ]
        },
        "python_to_chi": {
            "available": _py_to_chi_translator is not None or PythonToChiTranslator is not None,
            "features": [
                "Basic Python constructs to Chi equivalents",
                "Function calls to Chi syntax",
                "Control structures translation",
                "Variable assignments",
                "Expressions and operators"
            ]
        },
        "supported_directions": [
            "chi -> python",
            "python -> chi"
        ]
    }

# Convenience aliases
chi2py = chi_to_py
py2chi = py_to_chi

__all__ = [
    "chi_to_py",
    "py_to_chi", 
    "translate",
    "get_translation_info",
    "chi2py",
    "py2chi",
    "get_chi_to_py_translator",
    "get_py_to_chi_translator"
]
