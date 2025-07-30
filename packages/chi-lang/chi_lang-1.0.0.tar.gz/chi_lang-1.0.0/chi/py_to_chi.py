#!/usr/bin/env python3
"""
Python to Chi Translator - Complete Implementation
Converts Python (.py) files back to Chi (.chi) files with comprehensive feature support
Reverses the Chi to Python translation process
"""

import re
import sys
from pathlib import Path

class PythonToChiTranslator:
    def __init__(self):
        # Core keyword mappings (reverse of chi_to_py_final.py)
        self.keyword_mapping = {
            'def': 'panga',
            'return': 'bweza', 
            'if': 'ngati',
            'elif': 'kapena_ngati',
            'else': 'sizoona',
            ':': 'chita',
            'while': 'yesani',
            'for': 'bwereza',
            'in': 'mu',
            'break': 'leka',
            'continue': 'pitilizani',
            'and': 'komanso',
            'or': 'kapena',
            'not': 'osati',
            'True': 'zoona',
            'False': 'zabodza',
            'None': 'palibe',
        }
        
        # State tracking for helper function removal
        self.in_helper_function = False
        self.helper_function_indent = 0
        
        # Built-in functions (reverse mapping)
        self.builtin_functions = {
            'print': 'onetsa',
            'input': 'funsani',
            'len': 'kukula',
            'type': 'mtundu',
            'str': 'mawu',
            'float': 'manambala',
            'int': 'manambala_olekeza',
            '_write_to_file': 'lemba_mu_file',
            '_read_entire_file': 'werenga_zonse',
            'os.path.exists': 'pezani_file',
        }
        
        # Exception handling keywords (reverse)
        self.exception_mapping = {
            'try': 'kuyesera',
            'except': 'zakanika',
            'finally': 'pomaliza',
            'as': 'chifukwa'
        }
        
        # Exception types (reverse)
        self.exception_types = {
            'ValueError': 'vuto_la_nambala',
            'TypeError': 'vuto_la_mtundu',
            'IndexError': 'vuto_la_ndandanda',
            'KeyError': 'cholakwika_kiyi',
            'NameError': 'vuto_la_dzina',
            'ZeroDivisionError': 'vuto_la_kugawa',
            'MemoryError': 'vuto_la_kukumbukira',
            'FileNotFoundError': 'vuto_la_fayilo',
            'PermissionError': 'vuto_la_chilolezo',
            'Exception': 'vuto_lililonse'
        }
        
        # Operators (reverse)
        self.operator_mapping = {
            '==': 'wafanana',
            '!=': 'wasiyana',
            '>': 'wapambana',
            '<': 'wachepa',
            '>=': 'wafananitsa',
            '<=': 'wachepetsedwa'
        }
        
        # Math functions (reverse)
        self.math_functions = {
            'math.sqrt': 'muzu',
            'pow': 'mphamvu',
            'math.floor': 'pansi',
            'math.ceil': 'pamwamba',
            'abs': 'chopanda',
            'round': 'zungulira',
        }
        
        # Statistics functions (reverse)
        self.stats_functions = {
            'statistics.mean': 'pakatikati',
            'statistics.median': 'chapakati',
            'statistics.mode': 'yofala',
        }
        
        # Aggregate functions (reverse)
        self.aggregate_functions = {
            'sum': 'phatikiza',
            'max': 'chachikulu',
            'min': 'chachingono',
            'sorted': 'sanja'
        }
        
        # File operations (reverse)
        self.file_operations = {
            'open': 'tsegula',
            'read': 'werenga',
            'readlines': 'werenga_mizere',
            'write': 'lemba',
            'close': 'tseka'
        }
        
        # File modes (reverse)
        self.file_modes = {
            'r': 'werenga',
            'w': 'lemba',
            'a': 'wonjezera'
        }
        
        # String methods (reverse) - including typo correction
        self.string_methods = {
            'strip': 'chotsani_mimpata',
            'split': 'gawani',
            'join': 'lumikizani',
            'replace': 'sinthani',
            'upper': 'zikuluzikulu',
            'lower': 'zingonozingono',
            'startswith': 'yoyamba_ndi',
            'endswith': 'imamaliza_ndi',
            'find': 'funafuna',
            'count': 'werengera'
        }
        
        # List methods (reverse)
        self.list_methods = {
            'append': 'onjezera',
            'insert': 'lowetsa',
            'remove': 'chotsa',
            'pop': 'tulutsa',
            'index': 'funafuna',
            'count': 'werengera'
        }
        
        # Dictionary methods (reverse)
        self.dict_methods = {
            'get': 'peza',
            'keys': 'makiyi',
            'values': 'mavalu',
            'items': 'zonse',
            'clear': 'chotsani_zonse',
            'copy': 'kopani',
            'update': 'sanjirani'
        }
        
    def protect_strings_and_comments(self, line):
        """Protect strings and comments from translation"""
        protected_parts = []
        
        # Find strings (both single and double quotes)
        string_pattern = r'(\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\')'
        def replace_string(match):
            placeholder = f"__STRING_{len(protected_parts)}__"
            protected_parts.append(match.group(0))
            return placeholder
        
        line = re.sub(string_pattern, replace_string, line)
        
        # Find comments
        comment_pattern = r'(#.*)'
        def replace_comment(match):
            placeholder = f"__COMMENT_{len(protected_parts)}__"
            protected_parts.append(match.group(0))
            return placeholder
        
        line = re.sub(comment_pattern, replace_comment, line)
        
        return line, protected_parts
    
    def restore_strings_and_comments(self, line, protected_parts):
        """Restore protected strings and comments"""
        for i, part in enumerate(protected_parts):
            line = line.replace(f"__STRING_{i}__", part)
            line = line.replace(f"__COMMENT_{i}__", part)
        return line
    
    def fix_typos(self, line):
        """Fix common typos in Chi code, specifically dulaini -> dulani"""
        # Fix the typo: dulaini should be dulani  
        line = re.sub(r'\bdulaini\b', 'dulani', line)
        # Also fix it when used as a method
        line = re.sub(r'\.dulaini\(', '.dulani(', line)
        return line
    
    def translate_line(self, line):
        """Translate a single line of Python to Chi"""
        # Skip empty lines and lines that are already Chi-like
        if not line.strip():
            return line
            
        # Skip translation headers and imports that we added - but be more specific
        if (line.strip().startswith('# Translated from Chi') or 
            line.strip().startswith('# Original file:') or
            line.strip().startswith('import math') or
            line.strip().startswith('import statistics')):
            return ""  # Remove these Python-specific additions
            
        # Skip helper functions completely - check if we're in a helper function
        if self.is_helper_function_line(line):
            return ""
            
        # Check if line has multiple statements
        if self.has_multiple_statements(line):
            return self.split_and_translate_statements(line)
        
        return self.translate_single_line(line)
    
    def has_multiple_statements(self, line):
        """Check if line contains multiple statements"""
        # Look for patterns that indicate multiple statements on one line
        # But avoid false positives in strings and function calls
        protected_line, _ = self.protect_strings_and_comments(line)
        
        # Count semicolons (not commonly used in our translations, but just in case)
        semicolon_count = protected_line.count(';')
        
        # Look for assignment followed by function call patterns
        assignment_then_call = re.search(r'\w+\s*=\s*[^=\n]*?\w+\s*\([^)]*\)', protected_line)
        
        return semicolon_count > 0 or assignment_then_call is not None
    
    def split_and_translate_statements(self, line):
        """Split multiple statements and translate each"""
        # Get indentation
        indent_match = re.match(r'^(\\s*)', line)
        indent = indent_match.group(1) if indent_match else ''
        
        # For now, just translate as single line - this could be enhanced
        return self.translate_single_line(line)
    
    def translate_single_line(self, line):
        """Translate a single statement with string/comment protection"""
        # First protect strings and comments before any translation
        protected_line, protected_parts = self.protect_strings_and_comments(line)
        
        # Fix any typos
        protected_line = self.fix_typos(protected_line)
        
        # Handle variable assignment - convert Python assignment to Chi ika
        protected_line = re.sub(r'^(\s*)(\w+)\s*=\s*', r'\1ika \2 = ', protected_line)
        
        # Handle for loops - convert "for item in iterable:" to "bwereza item mu iterable:"
        protected_line = re.sub(r'\bfor\s+(\w+)\s+in\s+([^:]+):', r'bwereza \1 mu \2 chita', protected_line)
        
        # Handle with statements - convert "with ... as ..." to equivalent Chi
        protected_line = re.sub(r'\bwith\s+([^:]+)\s+as\s+(\w+):', r'# with \1 chifukwa \2:', protected_line)
        
        # Handle slice notation back to dulani (before data structures)
        protected_line = self.translate_slice_notation(protected_line)
        
        # Handle data structure creation
        protected_line = self.translate_data_structures(protected_line)
        
        # Handle method calls (must be done before keyword replacement)
        protected_line = self.translate_method_calls(protected_line)
        
        # Handle file operations
        protected_line = self.translate_file_operations(protected_line)
        
        # Handle math and statistics functions
        protected_line = self.translate_math_functions(protected_line)
        protected_line = self.translate_stats_functions(protected_line)
        protected_line = self.translate_aggregate_functions(protected_line)
        
        # Handle exception handling
        protected_line = self.translate_exception_handling(protected_line)
        
        # Handle operators (sort by length to avoid partial matches)
        sorted_operators = sorted(self.operator_mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for py_op, chi_op in sorted_operators:
            protected_line = re.sub(r'\b' + re.escape(py_op) + r'\b', chi_op, protected_line)
        
        # Handle built-in functions
        for py_func, chi_func in self.builtin_functions.items():
            protected_line = re.sub(r'\b' + re.escape(py_func) + r'\b', chi_func, protected_line)
        
        # Handle keywords (sort by length to avoid partial matches)
        sorted_keywords = sorted(self.keyword_mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for py_keyword, chi_keyword in sorted_keywords:
            protected_line = re.sub(r'\b' + re.escape(py_keyword) + r'\b', chi_keyword, protected_line)
        
        # Restore strings and comments at the very end
        final_line = self.restore_strings_and_comments(protected_line, protected_parts)
        
        return final_line.rstrip()
    
    def translate_data_structures(self, line):
        """Handle list and dict creation - convert Python [] and {} to ndandanda and kaundula"""        
        # Handle list creation [item1, item2, ...] -> ndandanda(item1, item2, ...)
        # Be very careful to distinguish between list literals and array access
        def replace_list(match):
            full_match = match.group(0)
            content = match.group(1) if match.group(1) else ''
            
            # Skip if this is clearly array access (single number, variable, or string)
            if (re.match(r'^\s*\d+\s*$', content) or 
                re.match(r'^\s*\w+\s*$', content) or
                re.match(r'^\s*"[^"]*"\s*$', content) or
                re.match(r"^\s*'[^']*'\s*$", content)):
                return full_match  # Keep as is
                
            # Skip if this contains slicing notation (already handled by slice method)
            if ':' in content:
                return full_match  # Keep as is
                
            # Only convert if it contains commas (multiple items) or is clearly a list literal
            if ',' in content or not content.strip():
                return f'ndandanda({content})'
            
            return full_match  # Keep as is for single items
        
        # Only convert lists that don't look like array access
        # Look for patterns that are NOT preceded by a variable/method call
        line = re.sub(r'(?<![.\w])\[([^\[\]]*?)\]', replace_list, line)
        
        # Handle dictionary creation {} -> kaundula()
        def replace_dict(match):
            content = match.group(1) if match.group(1) else ''
            if not content.strip():
                return 'kaundula()'
            
            # Parse key-value pairs and convert format
            pairs = [pair.strip() for pair in content.split(',')]
            chi_pairs = []
            for pair in pairs:
                if ':' in pair:
                    key_val = pair.split(':', 1)
                    key = key_val[0].strip()
                    val = key_val[1].strip()
                    chi_pairs.extend([key, val])
            
            if chi_pairs:
                return f'kaundula({", ".join(chi_pairs)})'
            return f'kaundula({content})'
        
        # Simple dict pattern
        line = re.sub(r'\{([^\{\}]*?)\}', replace_dict, line)
        
        return line
    
    def translate_slice_notation(self, line):
        """Convert Python slice notation back to dulani method"""
        # Handle specific slice patterns - must be more targeted
        # Pattern: something[start:end] -> something.dulani(start, end)
        
        # Handle chained method calls followed by slicing: .method()[start:end]
        line = re.sub(r'(\w+\(\))\[(-?\w+):(-?\w+)\]', r'\1.dulani(\2, \3)', line)
        line = re.sub(r'(\w+\(\))\[(-?\w+):\]', r'\1.dulani(\2)', line)
        line = re.sub(r'(\w+\(\))\[:(-?\w+)\]', r'\1.dulani(0, \2)', line)
        
        # Handle array access followed by slicing: var[0][start:end]
        line = re.sub(r'(\w+\[\d+\])\[(-?\w+):(-?\w+)\]', r'\1.dulani(\2, \3)', line)
        line = re.sub(r'(\w+\[\d+\])\[(-?\w+):\]', r'\1.dulani(\2)', line)
        line = re.sub(r'(\w+\[\d+\])\[:(-?\w+)\]', r'\1.dulani(0, \2)', line)
        
        # Handle simple variable slicing: var[start:end]
        line = re.sub(r'(\w+)\[(-?\w+):(-?\w+)\]', r'\1.dulani(\2, \3)', line)
        line = re.sub(r'(\w+)\[(-?\w+):\]', r'\1.dulani(\2)', line)
        line = re.sub(r'(\w+)\[:(-?\w+)\]', r'\1.dulani(0, \2)', line)
        line = re.sub(r'(\w+)\[:\]', r'\1.dulani()', line)
        
        return line
    
    def translate_method_calls(self, line):
        """Handle method calls - convert Python methods back to Chi methods"""
        # String methods
        for py_method, chi_method in self.string_methods.items():
            # Handle simple method calls
            line = re.sub(rf'\.({py_method})\(([^)]*)\)', f'.{chi_method}(\\2)', line)
        
        # List methods
        for py_method, chi_method in self.list_methods.items():
            line = re.sub(rf'\.({py_method})\(([^)]*)\)', f'.{chi_method}(\\2)', line)
        
        # Dictionary methods - these are more complex due to different syntax
        # Convert dict.get(key, default) -> dict.peza_kapena(key, default)
        line = re.sub(r'(\w+)\.get\(([^,]+),\s*([^)]+)\)', r'\1.peza_kapena(\2, \3)', line)
        line = re.sub(r'(\w+)\.get\(([^)]+)\)', r'\1.peza(\2)', line)
        
        # Convert key in dict -> dict.ali_nacho(key)
        line = re.sub(r'(\w+)\s+in\s+(\w+)(?!\s*[\[\(])', r'\2.ali_nacho(\1)', line)
        
        # Other dict methods
        line = re.sub(r'(\w+)\.keys\(\)', r'\1.makiyi()', line)
        line = re.sub(r'(\w+)\.values\(\)', r'\1.mavalu()', line)
        line = re.sub(r'(\w+)\.items\(\)', r'\1.zonse()', line)
        line = re.sub(r'(\w+)\.clear\(\)', r'\1.chotsani_zonse()', line)
        line = re.sub(r'(\w+)\.copy\(\)', r'\1.kopani()', line)
        line = re.sub(r'(\w+)\.update\(([^)]+)\)', r'\1.sanjirani(\2)', line)
        
        # Handle dictionary assignment: dict[key] = value -> dict.ika_pa(key, value)
        line = re.sub(r'(\w+)\[([^\]]+)\]\s*=\s*([^\n]+)', r'\1.ika_pa(\2, \3)', line)
        
        return line
    
    def translate_file_operations(self, line):
        """Handle file operations"""
        # Convert open() calls
        for py_op, chi_op in self.file_operations.items():
            if py_op == 'open':
                # Convert file modes
                for py_mode, chi_mode in self.file_modes.items():
                    line = re.sub(rf'open\(([^,]+),\s*["\'{py_mode}["\']\)', f'{chi_op}(\\1, "{chi_mode}")', line)
            else:
                line = re.sub(rf'\.({py_op})\(', f'.{chi_op}(', line)
        
        return line
    
    def translate_math_functions(self, line):
        """Handle math functions"""
        for py_func, chi_func in self.math_functions.items():
            if py_func == 'pow':
                # Handle pow(base, exp) -> mphamvu(base, exp)
                line = re.sub(r'pow\(([^,]+),\s*([^)]+)\)', f'{chi_func}(\\1, \\2)', line)
            else:
                line = re.sub(r'\b' + re.escape(py_func) + r'\b', chi_func, line)
        
        return line
    
    def translate_stats_functions(self, line):
        """Handle statistics functions"""
        for py_func, chi_func in self.stats_functions.items():
            line = re.sub(r'\b' + re.escape(py_func) + r'\b', chi_func, line)
        
        return line
    
    def translate_aggregate_functions(self, line):
        """Handle aggregate functions like sum, max, min"""
        for py_func, chi_func in self.aggregate_functions.items():
            # Handle function calls with arguments
            line = re.sub(f'\\b{py_func}\\(([^)]+)\\)', f'{chi_func}(\\1)', line)
        
        return line
    
    def translate_exception_handling(self, line):
        """Handle exception handling constructs"""
        # Handle try/except/finally
        for py_keyword, chi_keyword in self.exception_mapping.items():
            line = re.sub(r'\b' + py_keyword + r'\b', chi_keyword, line)
        
        # Handle exception types
        for py_exc, chi_exc in self.exception_types.items():
            line = re.sub(r'\b' + py_exc + r'\b', chi_exc, line)
        
        return line
    
    def translate_file(self, python_file_path, chi_file_path=None):
        """Translate entire Python file to Chi"""
        # Reset state for each file
        self.in_helper_function = False
        self.helper_function_indent = 0
        
        py_path = Path(python_file_path)
        
        if not py_path.exists():
            print(f"Error: File {python_file_path} not found")
            return False
        
        if chi_file_path is None:
            chi_file_path = py_path.with_suffix('.chi')
        
        try:
            with open(py_path, 'r', encoding='utf-8') as py_file:
                py_lines = py_file.readlines()
            
            # Translate all lines
            translated_lines = []
            translation_warnings = []
            
            for line_num, line in enumerate(py_lines, 1):
                try:
                    translated_line = self.translate_line(line)
                    
                    # Skip empty lines that result from removing Python-specific code
                    if translated_line.strip() or line.strip() == "":
                        translated_lines.append(translated_line + '\n' if translated_line and not translated_line.endswith('\n') else translated_line)
                        
                except Exception as e:
                    # If translation fails, add as comment
                    translated_lines.append(f"# Error translating line {line_num}: {line.rstrip()}\n")
                    translated_lines.append(f"# Error: {str(e)}\n")
                    translation_warnings.append(f"Line {line_num}: Translation error - {str(e)}")
            
            # Show warnings if any
            if translation_warnings:
                print("\n⚠️  Translation Warnings:")
                for warning in translation_warnings[:10]:  # Show first 10 warnings
                    print(f"  {warning}")
                if len(translation_warnings) > 10:
                    print(f"  ... and {len(translation_warnings) - 10} more warnings")
            
            # Generate final output
            chi_code = []
            chi_code.append("# Translated from Python to Chi\n")
            chi_code.append(f"# Original file: {py_path.name}\n")
            chi_code.append("\n")
            
            # Add translated code
            chi_code.extend(translated_lines)
            
            # Write output file
            with open(chi_file_path, 'w', encoding='utf-8') as chi_file:
                chi_file.writelines(chi_code)
            
            print(f"✅ Translation complete!")
            print(f"📁 Input:  {python_file_path}")
            print(f"📁 Output: {chi_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error translating file: {str(e)}")
            return False

    def is_helper_function_line(self, line):
        """Check if this line is part of a helper function that should be completely removed"""
        stripped = line.strip()
        
        # Check if we're starting a helper function
        if (stripped.startswith('def _write_to_file(') or
            stripped.startswith('def _read_entire_file(')):
            self.in_helper_function = True
            self.helper_function_indent = len(line) - len(line.lstrip())
            return True
        
        # If we're in a helper function, check if we're still inside it
        if self.in_helper_function:
            if not stripped:  # Empty line
                return True
                
            current_indent = len(line) - len(line.lstrip())
            
            # If we're at the same level or less indented than the function definition,
            # and it's not empty, we've exited the function
            if current_indent <= self.helper_function_indent and stripped:
                # Check if this is another function or top-level code
                if not stripped.startswith(' ') or stripped.startswith('def ') or stripped.startswith('class '):
                    self.in_helper_function = False
                    self.helper_function_indent = 0
                    # Don't return True here - this line is not part of the helper function
                else:
                    return True
            else:
                # We're still inside the helper function
                return True
                
        return False
    
def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python py_to_chi.py <python_file> [output_chi_file]")
        print("Example: python py_to_chi.py example.py example_translated.chi")
        sys.exit(1)
    
    python_file = sys.argv[1]
    chi_file = sys.argv[2] if len(sys.argv) == 3 else None
    
    translator = PythonToChiTranslator()
    success = translator.translate_file(python_file, chi_file)
    
    if success:
        print("\n🎉 Translation successful! The Chi file is ready to run.")
    else:
        print("\n❌ Translation failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
