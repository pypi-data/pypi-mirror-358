#lexer.py
import re
from .keywords import KEYWORDS

# Token types
TOKEN_TYPES = {
    'NUMBER': r'\d+(\.\d+)?',
    'STRING': r'"(?:[^"\\]|\\.)*"',  # Updated to handle escaped characters
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'OPERATOR': r'\*\*|==|!=|\<=|\>=|[+\-*/%=\<\>]',
    'PUNCTUATION': r'[\(\)\[\]:,.]',
    'BRACE': r'[{}]',
    'NEWLINE': r'\n',
    'WHITESPACE': r'[ \t]+',
    'COMMENT': r'#.*',
}

# Compile regex into patterns
TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES.items())
token_re = re.compile(TOKEN_REGEX)

def tokenize(code):
    tokens = []
    line_number = 1
    indent_stack = [0]  # Track indentation levels
    lines = code.split('\n')
    previous_token_type = None
    
    for line in lines:
        # Calculate indentation
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            line_number += 1
            continue
            
        indent_level = len(line) - len(stripped)
        
        # Handle indentation changes
        if indent_level > indent_stack[-1]:
            indent_stack.append(indent_level)
            tokens.append({'type': 'INDENT', 'value': '', 'line': line_number})
        elif indent_level < indent_stack[-1]:
            while indent_stack and indent_level < indent_stack[-1]:
                indent_stack.pop()
                tokens.append({'type': 'DEDENT', 'value': '', 'line': line_number})
                
        # Tokenize the line content
        for match in token_re.finditer(stripped):
            kind = match.lastgroup
            value = match.group()

            if kind == 'NEWLINE':
                continue
            elif kind == 'WHITESPACE' or kind == 'COMMENT':
                continue
            elif kind == 'IDENTIFIER' and value == 'chita':
                # 'chita' acts as a block starter, equivalent to ':'
                kind = 'BLOCK_STARTER'
            elif kind == 'IDENTIFIER' and value in ['wafanana', 'wasiyana', 'wapambana', 'wachepa', 'wafananitsa', 'wachepetsedwa']:
                # Chichewa comparison operators
                kind = 'CHI_OPERATOR'
            elif kind == 'IDENTIFIER' and value in ['komanso', 'kapena', 'osati']:
                # Chichewa logical operators
                kind = 'CHI_LOGICAL'
            elif kind == 'IDENTIFIER' and value in ['kapena_ngati']:
                # Chichewa elif
                kind = 'CHI_ELIF'
            elif kind == 'IDENTIFIER' and value in ['kuyesera', 'zakanika', 'pomaliza', 'chifukwa', 'chimodzimodzi', 'vuto_la_nambala', 'vuto_la_mtundu', 'vuto_la_ndandanda', 'cholakwika_kiyi', 'vuto_la_dzina', 'vuto_la_kugawa', 'vuto_la_kukumbukira', 'vuto_la_fayilo', 'vuto_la_chilolezo', 'vuto_lililonse']:
                # Exception handling keywords should always be keywords
                kind = 'KEYWORD'
            # Dictionary methods should remain as identifiers when used as function/method names
            elif kind == 'IDENTIFIER' and value in ['ika_pa', 'peza', 'peza_kapena', 'ali_nacho', 'chotsa_pa', 'chotsani_zonse', 'makiyi', 'mavalu', 'zonse', 'kopani', 'sanjirani']:
                # Keep as IDENTIFIER for method calls
                pass
            elif kind == 'IDENTIFIER' and value in KEYWORDS:
                # Don't treat method names and function names as keywords - they should remain identifiers
                # when used for method calls or function calls
                # BUT panga and bweza should always be keywords
                if value in ['panga', 'bweza']:
                    kind = 'KEYWORD'
                elif value not in ['onjezera', 'lowetsa', 'chotsa', 'tulutsa', 'funafuna', 'werengera', 'funsani', 'mawu', 'manambala', 'manambala_olekeza', 'kukula', 'mtundu', 'mphamvu', 'chotsalira', 'muzu', 'chopanda', 'pansi', 'pamwamba', 'zungulira', 'phatikiza', 'pakatikati', 'chachikulu', 'chachingono', 'sanja', 'chapakati', 'yofala', 'kaundula', 'ndandanda', 'tsegula', 'werenga_zonse', 'lemba_mu_file', 'pezani_file', 'werenga', 'lemba', 'tseka', 'mizere', 'wonjezera', 'chotsani_mimpata', 'gawani', 'lumikizani', 'sinthani', 'zikuluzikulu', 'zingonozingono', 'yoyamba_ndi', 'imamaliza_ndi', 'ili_nacho', 'kutalika', 'bwezerani', 'dulani']:
                    kind = 'KEYWORD'

            tokens.append({'type': kind, 'value': value, 'line': line_number})
            
        tokens.append({'type': 'NEWLINE', 'value': '\n', 'line': line_number})
        line_number += 1
    
    # Add final DEDENTs for any remaining indentation
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append({'type': 'DEDENT', 'value': '', 'line': line_number})

    return tokens

# For testing
if __name__ == "__main__":
    sample_code = '''
    ika dzina = mawu("Jakesh")
    ngati dzina == mawu("Jakesh"):
        onetsa("Moni!")
    '''

    for token in tokenize(sample_code):
        print(token)
