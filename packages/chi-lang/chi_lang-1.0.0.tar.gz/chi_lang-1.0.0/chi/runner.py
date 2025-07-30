#runner.py
from .lexer import tokenize as lexer
from .parser import Parser
from .interpreter import Interpreter

def run_chi_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    tokens = lexer(code)
    parser = Parser(tokens)
    statements = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(statements)
