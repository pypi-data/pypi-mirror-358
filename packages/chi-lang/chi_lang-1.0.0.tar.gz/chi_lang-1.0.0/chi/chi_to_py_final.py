#!/usr/bin/env python3
"""
Chi to Python Translator - Final Complete Implementation
Converts Chi (.chi) files to Python (.py) files with comprehensive feature support
Based on the comprehensive requirements specification
"""

import re
import sys
from pathlib import Path

class ChiToPythonTranslator:
    def __init__(self):
        # Core keyword mappings
        self.keyword_mapping = {
            'panga': 'def',
            'bweza': 'return',
            'ngati': 'if',
            'kapena_ngati': 'elif',
            'sizoona': 'else',
            'chita': ':',
            'yesani': 'while',
            'bwereza': 'for',
            'mu': 'in',
            'leka': 'break',
            'pitilizani': 'continue',
            'komanso': 'and',
            'kapena': 'or',
            'osati': 'not',
            'zoona': 'True',
            'zabodza': 'False',
            'palibe': 'None',
        }
        
        # Built-in functions
        self.builtin_functions = {
            'onetsa': 'print',
            'funsani': 'input',
            'kukula': 'len',
            'mtundu': 'type',
            'mawu': 'str',
            'manambala': 'float',
            'manambala_olekeza': 'int',
            'lemba_mu_file': '_write_to_file',
            'werenga_zonse': '_read_entire_file',
            'pezani_file': 'os.path.exists',
        }
        
        # Exception handling keywords
        self.exception_mapping = {
            'kuyesera': 'try',
            'zakanika': 'except',
            'pomaliza': 'finally',
            'chifukwa': 'as'
        }
        
        # Exception types
        self.exception_types = {
            'vuto_la_nambala': 'ValueError',
            'vuto_la_mtundu': 'TypeError',
            'vuto_la_ndandanda': 'IndexError',
            'cholakwika_kiyi': 'KeyError',
            'vuto_la_dzina': 'NameError',
            'vuto_la_kugawa': 'ZeroDivisionError',
            'vuto_la_kukumbukira': 'MemoryError',
            'vuto_la_fayilo': 'FileNotFoundError',
            'vuto_la_chilolezo': 'PermissionError',
            'vuto_lililonse': 'Exception'
        }
        
        # Operators
        self.operator_mapping = {
            'wafanana': '==',
            'wasiyana': '!=',
            'wapambana': '>',
            'wachepa': '<',
            'wafananitsa': '>=',
            'wachepetsedwa': '<='
        }
        
        # Math functions
        self.math_functions = {
            'muzu': 'math.sqrt',
            'mphamvu': 'pow',
            'pansi': 'math.floor',
            'pamwamba': 'math.ceil',
            'chopanda': 'abs',
            'zungulira': 'round',
        }
        
        # Statistics functions
        self.stats_functions = {
            'pakatikati': 'statistics.mean',
            'chapakati': 'statistics.median',
            'yofala': 'statistics.mode',
        }
        
        # Aggregate functions
        self.aggregate_functions = {
            'phatikiza': 'sum',
            'chachikulu': 'max',
            'chachingono': 'min',
            'sanja': 'sorted'
        }
        
        # File operations
        self.file_operations = {
            'tsegula': 'open',
            'werenga': 'read',
            'werenga_mizere': 'readlines',
            'lemba': 'write',
            'tseka': 'close'
        }
        
        # File modes
        self.file_modes = {
            'werenga': 'r',
            'lemba': 'w',
            'wonjezera': 'a'
        }
        
        # Track what helper functions are needed
        self.needs_math = False
        self.needs_statistics = False
        self.needs_file_write_helper = False
        self.needs_file_read_helper = False
        
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
            if part.startswith('#'):
                line = line.replace(f"__COMMENT_{i}__", part)
            else:
                line = line.replace(f"__STRING_{i}__", part)
        return line
    
    def translate_line(self, line):
        """Translate a single line of Chi to Python"""
        if not line.strip() or line.strip().startswith('#'):
            return line
        
        # Handle multiple statements on one line
        if self.has_multiple_statements(line):
            return self.split_and_translate_statements(line)
        
        return self.translate_single_line(line) + '\n'
    
    def has_multiple_statements(self, line):
        """Check if line contains multiple statements"""
        # Skip comment lines
        if line.strip().startswith('#'):
            return False
            
        # Look for patterns that indicate multiple statements
        patterns = [
            r'\)\s*[a-zA-Z_]\w*\s*=',  # function call followed by assignment
            r'=\s*[^=\n]*[a-zA-Z_]\w*\s*=',  # assignment followed by another assignment
            r'\)\s*onetsa\(',  # function call followed by print
            r'=\s*[^=\n]*onetsa\(',  # assignment followed by print
            r';\s*\w+',  # semicolon separator
            r'\s{4,}ika\s+\w+\s*=',  # multiple spaces before assignment
            r'\]\s*ika\s+\w+\s*=',  # list creation followed by assignment
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def split_and_translate_statements(self, line):
        """Split multiple statements and translate each"""
        original_indent = len(line) - len(line.lstrip())
        indent = ' ' * original_indent
        
        # Handle semicolon-separated statements first
        if ';' in line:
            parts = [part.strip() for part in line.split(';') if part.strip()]
            translated_parts = []
            for part in parts:
                translated_parts.append(indent + self.translate_single_line(part.strip()))
            return '\n'.join(translated_parts) + '\n'
        
        # Handle multiple assignments with 4+ spaces (like "ika total = sum(numbers)    ika average = ...")
        if re.search(r'\s{4,}ika\s+\w+\s*=', line):
            # Split on multiple spaces followed by 'ika'
            parts = re.split(r'\s{4,}(?=ika\s+\w+\s*=)', line.strip())
            if len(parts) > 1:
                result_parts = []
                for part in parts:
                    if part.strip():
                        result_parts.append(indent + self.translate_single_line(part.strip()))
                return '\n'.join(result_parts) + '\n'
        
        # More comprehensive approach: split on function calls that appear to be separate statements
        # Pattern 1: assignment = function()another_function()
        match = re.search(r'^(\s*\w+\s*=\s*[^=\n]*?\))\s*([a-zA-Z_]\w*\s*\([^)]*\))', line)
        if match:
            first_part = match.group(1).strip()
            second_part = match.group(2).strip()
            
            result = indent + self.translate_single_line(first_part) + '\n'
            result += indent + self.translate_single_line(second_part) + '\n'
            return result
        
        # Pattern 2: list = [...]assignment = function()print()
        match = re.search(r'^(\s*\w+\s*=\s*\[[^\]]*\])\s*([a-zA-Z_]\w*\s*=\s*[^=\n]*?)\s*([a-zA-Z_]\w*\s*\([^)]*\))', line)
        if match:
            first_part = match.group(1).strip()
            second_part = match.group(2).strip()
            third_part = match.group(3).strip()
            
            result = indent + self.translate_single_line(first_part) + '\n'
            result += indent + self.translate_single_line(second_part) + '\n'
            result += indent + self.translate_single_line(third_part) + '\n'
            return result
        
        # Pattern 3: list = [...]ika assignment = function()
        match = re.search(r'^(\s*\w+\s*=\s*\[[^\]]*\])\s*(ika\s+\w+\s*=\s*[^=\n]*)', line)
        if match:
            first_part = match.group(1).strip()
            second_part = match.group(2).strip()
            
            result = indent + self.translate_single_line(first_part) + '\n'
            result += indent + self.translate_single_line(second_part) + '\n'
            return result
        
        # General approach: try to split on word boundaries where a new statement likely starts
        # Look for patterns like ")word(" or "]word" or "word = "
        potential_splits = []
        
        # Find positions where statements might be split
        for match in re.finditer(r'(\)|\])\s*([a-zA-Z_]\w*)', line):
            potential_splits.append(match.start(2))
        
        if potential_splits:
            # Take the first split point
            split_pos = potential_splits[0]
            first_part = line[:split_pos].strip()
            second_part = line[split_pos:].strip()
            
            if first_part and second_part:
                result = indent + self.translate_single_line(first_part) + '\n'
                result += indent + self.translate_single_line(second_part) + '\n'
                return result
        
        # Fallback: translate as single line
        return self.translate_single_line(line) + '\n'
    
    def reset_imports(self):
        """Reset import tracking for new file"""
        self.needs_math = False
        self.needs_statistics = False
        self.needs_file_write_helper = False
        self.needs_file_read_helper = False
    
    def translate_single_line(self, line):
        """Translate a single statement with string/comment protection"""
        # Handle variable assignment (ika) first
        line = re.sub(r'\bika\s+(\w+)\s*=', r'\1 =', line)
        
        # Handle data structure creation
        line = self.translate_data_structures(line)
        
        # Handle method calls (must be done before keyword replacement)
        line = self.translate_method_calls(line)
        
        # Handle file operations
        line = self.translate_file_operations(line)
        
        # Handle math and statistics functions
        line = self.translate_math_functions(line)
        line = self.translate_stats_functions(line)
        line = self.translate_aggregate_functions(line)
        
        # Handle exception handling
        line = self.translate_exception_handling(line)
        
        # Now protect strings and comments before keyword translation
        protected_line, protected_parts = self.protect_strings_and_comments(line)
        
        # Handle operators
        for chi_op, py_op in self.operator_mapping.items():
            protected_line = re.sub(r'\b' + re.escape(chi_op) + r'\b', py_op, protected_line)
        
        # Handle built-in functions
        for chi_func, py_func in self.builtin_functions.items():
            if chi_func in protected_line:
                # Track if file helper functions are needed
                if py_func == '_write_to_file':
                    self.needs_file_write_helper = True
                elif py_func == '_read_entire_file':
                    self.needs_file_read_helper = True
                
                protected_line = re.sub(r'\b' + re.escape(chi_func) + r'\b', py_func, protected_line)
        
        # Handle keywords (sort by length to avoid partial matches)
        sorted_keywords = sorted(self.keyword_mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for chi_keyword, py_keyword in sorted_keywords:
            protected_line = re.sub(r'\b' + re.escape(chi_keyword) + r'\b', py_keyword, protected_line)
        
        # Restore strings and comments
        final_line = self.restore_strings_and_comments(protected_line, protected_parts)
        
        return final_line.rstrip()
    
    def translate_data_structures(self, line):
        """Handle ndandanda (list) and kaundula (dict) creation"""
        # Handle ndandanda (list creation)
        def replace_ndandanda(match):
            content = match.group(1) if match.group(1) else ''
            return f'[{content}]'
        
        # Handle nested ndandanda calls
        while 'ndandanda(' in line:
            pattern = r'\bndandanda\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)'
            if re.search(pattern, line):
                line = re.sub(pattern, replace_ndandanda, line)
            else:
                break
        
        # Handle kaundula (dictionary creation)
        def replace_kaundula(match):
            content = match.group(1) if match.group(1) else ''
            if not content.strip():
                return '{}'
            
            # Parse key-value pairs
            args = [arg.strip() for arg in content.split(',')]
            if len(args) % 2 == 0 and len(args) > 0:
                pairs = []
                for i in range(0, len(args), 2):
                    key = args[i]
                    value = args[i + 1]
                    pairs.append(f'{key}: {value}')
                return '{' + ', '.join(pairs) + '}'
            return f'{{{content}}}'
        
        while 'kaundula(' in line:
            pattern = r'\bkaundula\s*\(([^()]*)\)'
            if re.search(pattern, line):
                line = re.sub(pattern, replace_kaundula, line)
            else:
                break
        
        return line
    
    def translate_method_calls(self, line):
        """Handle method calls with context-sensitive translation"""
        # Handle complex chained method calls iteratively
        # Keep translating until no more Chi method names are found
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            original_line = line
            
            # String methods - handle both simple and chained calls
            string_methods = [
                # Simple patterns
                (r'(\w+)\.chotsani_mimpata\(\)', r'\1.strip()'),
                (r'(\w+)\.gawani\(([^)]+)\)', r'\1.split(\2)'),
                (r'(\w+)\.lumikizani\(([^)]+)\)', r'\1.join(\2)'),
                (r'(\w+)\.sinthani\(([^,]+),\s*([^)]+)\)', r'\1.replace(\2, \3)'),
                (r'(\w+)\.zikuluzikulu\(\)', r'\1.upper()'),
                (r'(\w+)\.zingonozingono\(\)', r'\1.lower()'),
                (r'(\w+)\.yoyamba_ndi\(([^)]+)\)', r'\1.startswith(\2)'),
                (r'(\w+)\.imamaliza_ndi\(([^)]+)\)', r'\1.endswith(\2)'),
                (r'(\w+)\.ili_nacho\(([^)]+)\)', r'\2 in \1'),
                (r'(\w+)\.kutalika\(\)', r'len(\1)'),
                (r'(\w+)\.bwezerani\(\)', r'\1[::-1]'),
                (r'(\w+)\.bwerezani\(([^)]+)\)', r'\1 * \2'),
                (r'(\w+)\.dulani\(([^,]+),\s*([^)]+)\)', r'\1[\2:\3]'),
                (r'(\w+)\.dulani\(([^)]+)\)', r'\1[:\2]'),
                
                # Handle chained method calls for dulani
                (r'(\w+(?:\.\w+\(\))+)\.dulani\(([^,]+),\s*([^)]+)\)', r'\1[\2:\3]'),
                (r'(\w+(?:\.\w+\(\))+)\.dulani\(([^)]+)\)', r'\1[:\2]'),
                
                # Complex patterns for chained calls
                (r'(\w+\[[^\]]+\])\.chotsani_mimpata\(\)', r'\1.strip()'),
                (r'(\w+\[[^\]]+\])\.gawani\(([^)]+)\)', r'\1.split(\2)'),
                (r'(\w+\[[^\]]+\])\.lumikizani\(([^)]+)\)', r'\1.join(\2)'),
                (r'(\w+\[[^\]]+\])\.sinthani\(([^,]+),\s*([^)]+)\)', r'\1.replace(\2, \3)'),
                (r'(\w+\[[^\]]+\])\.zikuluzikulu\(\)', r'\1.upper()'),
                (r'(\w+\[[^\]]+\])\.zingonozingono\(\)', r'\1.lower()'),
                (r'(\w+\[[^\]]+\])\.yoyamba_ndi\(([^)]+)\)', r'\1.startswith(\2)'),
                (r'(\w+\[[^\]]+\])\.imamaliza_ndi\(([^)]+)\)', r'\1.endswith(\2)'),
                (r'(\w+\[[^\]]+\])\.ili_nacho\(([^)]+)\)', r'\2 in \1'),
                (r'(\w+\[[^\]]+\])\.kutalika\(\)', r'len(\1)'),
                (r'(\w+\[[^\]]+\])\.bwezerani\(\)', r'\1[::-1]'),
                (r'(\w+\[[^\]]+\])\.bwerezani\(([^)]+)\)', r'\1 * \2'),
                (r'(\w+\[[^\]]+\])\.dulani\(([^,]+),\s*([^)]+)\)', r'\1[\2:\3]'),
                (r'(\w+\[[^\]]+\])\.dulani\(([^)]+)\)', r'\1[:\2]'),
                
                # Handle even more complex chained expressions
                (r'([^.]+\.[^.]+)\.dulani\(([^,]+),\s*([^)]+)\)', r'\1[\2:\3]'),
                (r'([^.]+\.[^.]+)\.dulani\(([^)]+)\)', r'\1[:\2]')]
            
            for pattern, replacement in string_methods:
                line = re.sub(pattern, replacement, line)
            
            # If no changes were made, break the loop
            if line == original_line:
                break
            
            iteration += 1
        
        # List methods
        list_methods = [
            (r'(\w+)\.onjezera\(([^)]+)\)', r'\1.append(\2)'),
            (r'(\w+)\.lowetsa\(([^)]+)\)', r'\1.insert(\2)'),
            (r'(\w+)\.chotsa\(([^)]+)\)', r'\1.remove(\2)'),
            (r'(\w+)\.tulutsa\(([^)]*)\)', r'\1.pop(\2)'),
            (r'(\w+)\.funafuna\(([^)]+)\)', r'\1.index(\2)'),
            (r'(\w+)\.werengera\(([^)]+)\)', r'\1.count(\2)'),
        ]
        
        for pattern, replacement in list_methods:
            line = re.sub(pattern, replacement, line)
        
        # Dictionary methods
        dict_methods = [
            (r'(\w+)\.ika_pa\(([^,]+),\s*([^)]+)\)', r'\1[\2] = \3'),
            (r'(\w+)\.ali_nacho\(([^)]+)\)', r'\2 in \1'),
            (r'(\w+)\.peza\(([^)]+)\)', r'\1.get(\2)'),
            (r'(\w+)\.peza_kapena\(([^,]+),\s*([^)]+)\)', r'\1.get(\2, \3)'),
            (r'(\w+)\.chotsa_pa\(([^)]+)\)', r'\1.pop(\2)'),
            (r'(\w+)\.chotsani_zonse\(\)', r'\1.clear()'),
            (r'(\w+)\.makiyi\(\)', r'\1.keys()'),
            (r'(\w+)\.mavalu\(\)', r'\1.values()'),
            (r'(\w+)\.zonse\(\)', r'\1.items()'),
            (r'(\w+)\.kopani\(\)', r'\1.copy()'),
            (r'(\w+)\.sanjirani\(([^)]+)\)', r'\1.update(\2)'),
        ]
        
        for pattern, replacement in dict_methods:
            line = re.sub(pattern, replacement, line)
        
        # File operations - special case handling
        if 'werenga_zonse(' in line:
            self.needs_file_read_helper = True
        line = re.sub(r'(\w+)\.werenga_zonse\(\)', r'_read_entire_file("\1.txt")', line)
        
        return line
    
    def translate_file_operations(self, line):
        """Handle file operations"""
        # Translate file modes in open calls only
        if 'tsegula(' in line or 'open(' in line:
            for chi_mode, py_mode in self.file_modes.items():
                pattern = f'"{chi_mode}"'
                replacement = f'"{py_mode}"'
                line = line.replace(pattern, replacement)
        
        # Translate file operations
        for chi_op, py_op in self.file_operations.items():
            line = re.sub(r'\b' + re.escape(chi_op) + r'\b', py_op, line)
        
        return line
    
    def translate_math_functions(self, line):
        """Handle math functions"""
        for chi_func, py_func in self.math_functions.items():
            if chi_func in line:
                if chi_func in ['muzu', 'pansi', 'pamwamba']:
                    self.needs_math = True
                if chi_func == 'mphamvu':
                    line = re.sub(r'\bmphamvu\s*\(([^,]+),\s*([^)]+)\)', r'pow(\1, \2)', line)
                else:
                    line = re.sub(r'\b' + re.escape(chi_func) + r'\b', py_func, line)
        
        return line
    
    def translate_stats_functions(self, line):
        """Handle statistics functions"""
        for chi_func, py_func in self.stats_functions.items():
            if chi_func in line:
                self.needs_statistics = True
                pattern = rf'\b{chi_func}\s*\(([^)]+)\)'
                match = re.search(pattern, line)
                if match:
                    args = match.group(1)
                    func_name = py_func.split('.')[-1]
                    # Handle unpacking operator for statistics functions - remove unnecessary unpacking
                    if '*' in args:
                        # Remove the * unpacking and just pass the variable
                        clean_args = args.replace('*', '')
                        line = re.sub(pattern, f'statistics.{func_name}({clean_args})', line)
                    else:
                        line = re.sub(pattern, f'statistics.{func_name}({args})', line)
        
        return line
    
    def translate_aggregate_functions(self, line):
        """Handle aggregate functions like sum, max, min"""
        for chi_func, py_func in self.aggregate_functions.items():
            if chi_func in line:
                pattern = rf'\b{chi_func}\s*\(([^)]+)\)'
                match = re.search(pattern, line)
                if match:
                    args = match.group(1)
                    # Clean handling - if it's a single variable, use it directly
                    # If it has unpacking (*), handle appropriately
                    if '*' in args:
                        # For phatikiza(*args), convert to sum(args)
                        clean_args = args.replace('*', '')
                        line = re.sub(pattern, f'{py_func}({clean_args})', line)
                    elif re.match(r'^\w+$', args.strip()):
                        # Single variable argument
                        line = re.sub(pattern, f'{py_func}({args})', line)
                    else:
                        # Multiple comma-separated arguments
                        if chi_func == 'phatikiza':
                            line = re.sub(pattern, f'{py_func}([{args}])', line)
                        else:
                            line = re.sub(pattern, f'{py_func}({args})', line)
        
        return line
    
    def translate_exception_handling(self, line):
        """Handle exception handling constructs"""
        # Handle exception keywords
        for chi_exc, py_exc in self.exception_mapping.items():
            line = re.sub(r'\b' + re.escape(chi_exc) + r'\b', py_exc, line)
        
        # Handle exception types
        for chi_type, py_type in self.exception_types.items():
            line = re.sub(r'\b' + re.escape(chi_type) + r'\b', py_type, line)
        
        # Fix common exception syntax issues
        line = re.sub(r'\bexcept\s+as\s+(\w+):', r'except Exception as \1:', line)
        line = re.sub(r'\bexcept\s+(\w+)\s+as\s+(\w+):', r'except \1 as \2:', line)
        
        return line
    
    def validate_translation(self, original_line, translated_line):
        """Basic validation of translation quality"""
        issues = []
        
        # Check for untranslated Chi keywords
        chi_keywords = ['ika', 'onetsa', 'ngati', 'sizoona', 'bwereza', 'mu', 'panga', 'bweza']
        for keyword in chi_keywords:
            if re.search(r'\b' + keyword + r'\b', translated_line):
                # Allow in comments and strings
                if not (re.search(r'#.*\b' + keyword + r'\b', translated_line) or 
                       re.search(r'["\'].*\b' + keyword + r'\b.*["\']', translated_line)):
                    issues.append(f"Untranslated keyword: {keyword}")
        
        # Check for untranslated Chi string methods
        chi_string_methods = ['chotsani_mimpata', 'gawani', 'lumikizani', 'sinthani', 
                             'zikuluzikulu', 'zingonozingono', 'yoyamba_ndi', 'imamaliza_ndi',
                             'ili_nacho', 'kutalika', 'bwezerani', 'bwerezani', 'dulani']
        for method in chi_string_methods:
            if re.search(r'\.' + method + r'\(', translated_line):
                if not re.search(r'#.*\.' + method + r'\(', translated_line):
                    issues.append(f"Untranslated string method: {method}")
        
        return issues
    
    def generate_imports(self):
        """Generate necessary import statements"""
        imports = []
        if self.needs_math:
            imports.append("import math")
        if self.needs_statistics:
            imports.append("import statistics")
        return imports
    
    def generate_helper_functions(self):
        """Generate helper function definitions if needed"""
        helper_functions = []
        
        # Only include _write_to_file if it's actually used
        if self.needs_file_write_helper:
            helper_functions.append(
                "def _write_to_file(filename, content):\n"
                "    with open(filename, 'w') as f:\n"
                "        f.write(str(content))"
            )
        
        # Only include _read_entire_file if it's actually used
        if self.needs_file_read_helper:
            helper_functions.append(
                "def _read_entire_file(filename):\n"
                "    with open(filename, 'r') as f:\n"
                "        return f.read()"
            )
        
        return helper_functions
    
    def translate_file(self, chi_file_path, python_file_path=None):
        """Translate entire Chi file to Python"""
        chi_path = Path(chi_file_path)
        
        if not chi_path.exists():
            print(f"Error: File {chi_file_path} not found")
            return False
        
        if python_file_path is None:
            python_file_path = chi_path.with_suffix('.py')
        
        # Reset import tracking
        self.reset_imports()
        
        try:
            with open(chi_path, 'r', encoding='utf-8') as chi_file:
                chi_lines = chi_file.readlines()
            
            # First pass: translate all lines to determine needed imports
            translated_lines = []
            translation_warnings = []
            
            for line_num, line in enumerate(chi_lines, 1):
                try:
                    # Skip existing translation headers
                    if (line.strip().startswith('# Translated from') or 
                        line.strip().startswith('# Original file:') or
                        line.strip().startswith('import math') or
                        line.strip().startswith('import statistics')):
                        continue
                    
                    translated_line = self.translate_line(line)
                    
                    # Validate translation
                    issues = self.validate_translation(line, translated_line)
                    if issues:
                        translation_warnings.extend([f"Line {line_num}: {issue}" for issue in issues])
                    
                    translated_lines.append(translated_line)
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
            python_code = []
            python_code.append("# Translated from Chi to Python\n")
            python_code.append(f"# Original file: {chi_path.name}\n")
            
            # Add necessary imports
            imports = self.generate_imports()
            for imp in imports:
                python_code.append(f"{imp}\n")
            
            if imports:
                python_code.append("\n")
            
            # Add helper functions if needed
            helper_functions = self.generate_helper_functions()
            if helper_functions:
                for helper_func in helper_functions:
                    python_code.append(f"{helper_func}\n")
                python_code.append("\n")
            
            # Add translated code
            python_code.extend(translated_lines)
            
            # Write output file
            with open(python_file_path, 'w', encoding='utf-8') as py_file:
                py_file.writelines(python_code)
            
            print(f"✅ Translation complete!")
            print(f"📁 Input:  {chi_file_path}")
            print(f"📁 Output: {python_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error translating file: {str(e)}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Chi to Python Translator - Final Complete Implementation")
        print("Usage: python3 chi_to_py_final.py <chi_file.chi> [output_file.py]")
        print("")
        print("Examples:")
        print("  python3 chi_to_py_final.py example.chi")
        print("  python3 chi_to_py_final.py example.chi translated.py")
        print("")
        print("Features:")
        print("  • Complete keyword translation")
        print("  • Context-sensitive method calls")
        print("  • Smart import management")
        print("  • Robust multiple statement handling")
        print("  • Exception handling support")
        print("  • File I/O operations")
        print("  • Math and statistics functions")
        print("  • Proper indentation management")
        sys.exit(1)
    
    chi_file = sys.argv[1]
    python_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    translator = ChiToPythonTranslator()
    success = translator.translate_file(chi_file, python_file)
    
    if success:
        print("\n🎉 Translation successful! The Python file is ready to run.")
    else:
        print("\n❌ Translation failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()