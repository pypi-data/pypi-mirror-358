#parser.py
from .interpreter import Expression, Statement, ChiBoolean, ChiNull

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def match(self, *types):
        if self.check(*types):
            self.advance()
            return True
        return False

    def check(self, *types):
        if self.is_at_end():
            return False
        token_type = self.peek()['type']
        token_value = self.peek()['value']
        return token_type in types or token_value in types

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.current >= len(self.tokens)

    def consume(self, expected_type, error_message):
        if self.check(expected_type):
            return self.advance()
        token = self.peek() if not self.is_at_end() else self.previous()
        line = token['line'] if token else "unknown"
        raise Exception(f"[Line {line}] {error_message}")
        
    def consume_block_starter(self, error_message):
        """Consume either ':' (PUNCTUATION) or 'chita' (BLOCK_STARTER)"""
        if self.check('PUNCTUATION') and self.peek()['value'] == ':':
            return self.advance()
        elif self.check('BLOCK_STARTER'):
            return self.advance()
        token = self.peek() if not self.is_at_end() else self.previous()
        line = token['line'] if token else "unknown"
        raise Exception(f"[Line {line}] {error_message}")

    def parse(self):
        statements = []
        while not self.is_at_end():
            # Skip newlines and dedents at top level
            while self.match('NEWLINE', 'DEDENT'):
                pass
                
            if self.is_at_end():
                break
                
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except Exception as e:
                token = self.peek() if not self.is_at_end() else self.previous()
                line = token['line'] if token else "unknown"
                raise Exception(f"[Line {line}] Error parsing statement: {str(e)}")
        return statements

    def statement(self):
        if self.match('KEYWORD'):
            keyword = self.previous()['value']

            if keyword == 'ika':
                return self.var_declaration()
            elif keyword == 'ngati':
                return self.if_statement()
            elif keyword == 'yesani':
                return self.while_loop()
            elif keyword == 'bwereza':
                return self.for_loop()
            elif keyword == 'onetsa':
                return self.print_statement()
            elif keyword == 'panga':
                return self.function_definition()
            elif keyword == 'bweza':
                return self.return_statement()
            elif keyword == 'leka':
                return Statement.Break()
            elif keyword == 'pitilizani':
                return Statement.Continue()
            elif keyword == 'kuyesera':
                return self.try_statement()

        return self.expression_statement()

    def var_declaration(self):
        name = self.consume('IDENTIFIER', "Expected variable name.")
        self.consume('OPERATOR', "Expected '=' after variable name.")
        value = self.expression()
        return Statement.VarDeclaration(name['value'], value)

    def print_statement(self):
        self.consume('PUNCTUATION', "Expected '(' after 'onetsa'.")  # consume '('
        args = []
        if not (self.check('PUNCTUATION') and self.peek()['value'] == ')'):
            while True:
                args.append(self.expression())
                if self.check('PUNCTUATION') and self.peek()['value'] == ',':
                    self.advance()  # consume ','
                else:
                    break
        self.consume('PUNCTUATION', "Expected ')' after print arguments.")  # consume ')'
        return Statement.Print(args)


    def if_statement(self):
        condition = self.expression()
        self.consume_block_starter("Expected ':' or 'chita' after condition.")
        then_branch = self.block()
        
        # Consume DEDENT after the then_branch block
        if self.check('DEDENT'):
            self.advance()
        
        # Handle elif (kapena_ngati) chains
        elif_branches = []
        while self.check('CHI_ELIF') and self.peek()['value'] == 'kapena_ngati':
            self.advance()  # consume kapena_ngati
            elif_condition = self.expression()
            self.consume_block_starter("Expected ':' or 'chita' after elif condition.")
            elif_body = self.block()
            elif_branches.append((elif_condition, elif_body))
            
            # Consume DEDENT after each elif block
            if self.check('DEDENT'):
                self.advance()
        
        # Handle else (sizoona)
        else_branch = None
        if self.check('KEYWORD') and self.peek()['value'] == 'sizoona':
            self.advance()  # consume sizoona
            self.consume_block_starter("Expected ':' or 'chita' after else.")
            else_branch = self.block()
            
            # Consume DEDENT after else block
            if self.check('DEDENT'):
                self.advance()
        
        return Statement.If(condition, then_branch, else_branch, elif_branches)

    def while_loop(self):
        condition = self.expression()
        self.consume_block_starter("Expected ':' or 'chita' after condition.")
        body = self.block()
        return Statement.While(condition, body)

    def for_loop(self):
        var = self.consume('IDENTIFIER', "Expected loop variable.")
        self.consume('KEYWORD', "Expected 'mu' after loop variable.")
        iterable = self.expression()
        self.consume_block_starter("Expected ':' or 'chita' after iterable.")
        body = self.block()
        
        # Consume DEDENT after for loop body
        if self.check('DEDENT'):
            self.advance()
        
        return Statement.For(var['value'], iterable, body)
    
    def function_definition(self):
        # panga function_name(param1, param2, ...):
        name = self.consume('IDENTIFIER', "Expected function name.")
        
        self.consume('PUNCTUATION', "Expected '(' after function name.")
        
        # Parse parameters
        params = []
        if not (self.check('PUNCTUATION') and self.peek()['value'] == ')'):
            while True:
                param = self.consume('IDENTIFIER', "Expected parameter name.")
                params.append(param['value'])
                if self.check('PUNCTUATION') and self.peek()['value'] == ',':
                    self.advance()  # consume ','
                else:
                    break
        
        self.consume('PUNCTUATION', "Expected ')' after parameters.")
        self.consume_block_starter("Expected ':' or 'chita' after function declaration.")
        
        body = self.block()
        
        return Statement.FunctionDefinition(name['value'], params, body)
    
    def return_statement(self):
        value = None
        if not self.check('NEWLINE') and not self.is_at_end():
            value = self.expression()
        return Statement.Return(value)

    def expression_statement(self):
        expr = self.expression()
        return Statement.Expression(expr)

    def expression(self):
        return self.logical_or()
        
    def logical_or(self):
        expr = self.logical_and()
        
        while True:
            if self.check('CHI_LOGICAL') and self.peek()['value'] == 'kapena':
                self.advance()  # consume kapena
                operator = 'or'
                right = self.logical_and()
                expr = Expression.Binary(expr, operator, right)
            elif self.check('KEYWORD') and self.peek()['value'] == 'kapena':
                self.advance()  # consume kapena
                operator = 'or'
                right = self.logical_and()
                expr = Expression.Binary(expr, operator, right)
            else:
                break
            
        return expr
        
    def logical_and(self):
        expr = self.equality()
        
        while self.check('CHI_LOGICAL') and self.peek()['value'] == 'komanso':
            self.advance()  # consume komanso
            operator = 'and'
            right = self.equality()
            expr = Expression.Binary(expr, operator, right)
            
        return expr
        
    def unary(self):
        if self.match('CHI_LOGICAL') and self.previous()['value'] == 'osati':
            operator = 'not'
            right = self.unary()
            return Expression.Unary(operator, right)
        elif self.match('OPERATOR') and self.previous()['value'] == '-':
            operator = '-'
            right = self.unary()
            return Expression.Unary(operator, right)
            
        return self.call()
        
    def equality(self):
        expr = self.comparison()
        
        while True:
            if self.check('OPERATOR') and self.peek()['value'] in ['==', '!=']:
                operator = self.advance()['value']
                right = self.comparison()
                expr = Expression.Binary(expr, operator, right)
            elif self.check('CHI_OPERATOR') and self.peek()['value'] in ['wafanana', 'wasiyana']:
                chi_op = self.advance()['value']
                operator = '==' if chi_op == 'wafanana' else '!='
                right = self.comparison()
                expr = Expression.Binary(expr, operator, right)
            else:
                break
                
        return expr
        
    def comparison(self):
        expr = self.term()
        
        while True:
            if self.check('OPERATOR') and self.peek()['value'] in ['>', '<', '>=', '<=']:
                operator = self.advance()['value']
                right = self.term()
                expr = Expression.Binary(expr, operator, right)
            elif self.check('CHI_OPERATOR') and self.peek()['value'] in ['wapambana', 'wachepa', 'wafananitsa', 'wachepetsedwa']:
                chi_op = self.advance()['value']
                operator_map = {
                    'wapambana': '>',
                    'wachepa': '<', 
                    'wafananitsa': '>=',
                    'wachepetsedwa': '<='
                }
                operator = operator_map[chi_op]
                right = self.term()
                expr = Expression.Binary(expr, operator, right)
            else:
                break
                
        return expr

    def term(self):
        expr = self.factor()
        
        while self.check('OPERATOR') and self.peek()['value'] in ['+', '-']:
            operator = self.advance()['value']
            right = self.factor()
            expr = Expression.Binary(expr, operator, right)
            
        return expr
        
    def factor(self):
        expr = self.power()
        
        while self.check('OPERATOR') and self.peek()['value'] in ['*', '/', '%']:
            operator = self.advance()['value']
            right = self.power()
            expr = Expression.Binary(expr, operator, right)
            
        return expr
    
    def power(self):
        expr = self.unary()
        
        while self.check('OPERATOR') and self.peek()['value'] == '**':
            operator = self.advance()['value']
            right = self.unary()
            expr = Expression.Binary(expr, operator, right)
            
        return expr

    def call(self):
        expr = self.primary()

        while True:
            if self.check('PUNCTUATION') and self.peek()['value'] == '(':
                # Function call
                self.advance()  # consume '('
                args = []

                # Accept zero, one, or many arguments
                if not (self.check('PUNCTUATION') and self.peek()['value'] == ')'):
                    while True:
                        args.append(self.expression())
                        if self.check('PUNCTUATION') and self.peek()['value'] == ',':
                            self.advance()  # consume ','
                        else:
                            break

                self.consume('PUNCTUATION', "Expected ')' after arguments.")
                expr = Expression.FunctionCall(expr, args)
            elif self.check('PUNCTUATION') and self.peek()['value'] == '[':
                # Index access or slice
                self.advance()  # consume '['
                
                # Handle different indexing patterns
                start_index = None
                end_index = None
                
                # Check if it starts with colon (empty start)
                if self.check('PUNCTUATION') and self.peek()['value'] == ':':
                    # Slice starting from beginning like [:5]
                    self.advance()  # consume ':'
                    end_index = self.expression()
                    expr = Expression.Slice(expr, start_index, end_index)
                else:
                    # Parse first expression (could be start index or single index)
                    first_expr = self.expression()
                    
                    # Check if there's a colon for slicing
                    if self.check('PUNCTUATION') and self.peek()['value'] == ':':
                        self.advance()  # consume ':'
                        start_index = first_expr
                        
                        # Check if there's an end index
                        if not (self.check('PUNCTUATION') and self.peek()['value'] == ']'):
                            end_index = self.expression()
                        
                        expr = Expression.Slice(expr, start_index, end_index)
                    else:
                        # Simple index access
                        expr = Expression.Index(expr, first_expr)
                
                if not (self.check('PUNCTUATION') and self.peek()['value'] == ']'):
                    raise Exception("Expected ']' after index.")
                self.advance()  # consume ']'
            elif self.check('PUNCTUATION') and self.peek()['value'] == '.':
                # Method call or property access
                self.advance()  # consume '.'
                
                # Check if next token is an identifier (method/property name)
                if not self.check('IDENTIFIER'):
                    raise Exception("Expected method or property name after '.'")
                    
                method_name = self.advance()['value']  # consume method name
                
                # Check if it's a function call with parentheses
                if self.check('PUNCTUATION') and self.peek()['value'] == '(':
                    self.advance()  # consume '('
                    args = []
                    if not (self.check('PUNCTUATION') and self.peek()['value'] == ')'):
                        while True:
                            args.append(self.expression())
                            if self.check('PUNCTUATION') and self.peek()['value'] == ',':
                                self.advance()  # consume ','
                            else:
                                break
                    self.consume('PUNCTUATION', "Expected ')' after method arguments.")
                    expr = Expression.MethodCall(expr, method_name, args)
                else:
                    # Property access (no parentheses)
                    expr = Expression.PropertyAccess(expr, method_name)
            else:
                break

        return expr


    def primary(self):
        if self.match('KEYWORD'):
            value = self.previous()['value']
            if value in ('choona', 'zoona'):
                return Expression.Literal(ChiBoolean(True))
            if value in ('chabodza', 'zabodza'):
                return Expression.Literal(ChiBoolean(False))
            if value == 'palibe':
                return Expression.Literal(ChiNull())
        if self.is_at_end():
            token = self.previous() if self.current > 0 else None
            line = token['line'] if token else "unknown"
            raise Exception(f"[Line {line}] Unexpected end of input while parsing expression")

        token = self.advance()

        if token['type'] == 'NUMBER':
            return Expression.Literal(float(token['value']))
        elif token['type'] == 'STRING':
            # Process escape sequences in strings
            raw_string = token['value'][1:-1]  # Remove quotes
            processed_string = self.process_escape_sequences(raw_string)
            return Expression.Literal(processed_string)
        elif token['type'] == 'IDENTIFIER':
            return Expression.Variable(token['value'])

        elif token['value'] in ['choona', 'chabodza', 'zoona', 'zabodza']:
            return Expression.Literal(ChiBoolean(token['value'] in ['choona', 'zoona']))
        elif token['type'] == 'PUNCTUATION' and token['value'] == '(':
            expr = self.expression()
            self.consume('PUNCTUATION', "Expected ')' after expression.")
            return expr
        elif token['type'] == 'BRACE' and token['value'] == '{':
            # Dictionary literal {key: value, key2: value2}
            return self.dict_literal()

        raise Exception(f"[Line {token['line']}] Unexpected token '{token['value']}' of type '{token['type']}'")

    def block(self,is_top_level=False):
        """Parse a block of statements - handles indentation-based blocks"""
        statements = []
        
        # Skip newlines after colon
        while self.match('NEWLINE'):
            pass
            
        # Expect an INDENT token for the block
        if self.match('INDENT'):
            # Parse statements until DEDENT
            while not self.check('DEDENT') and not self.is_at_end():
                # Skip newlines between statements
                while self.match('NEWLINE'):
                    pass
                    
                if not self.check('DEDENT') and not self.is_at_end():
                    stmt = self.statement()
                    if stmt:
                        statements.append(stmt)
            # --- FIX: Always consume DEDENT after block ---
            #if self.check('DEDENT') and not is_top_level:
            #    self.advance()            
            # Don't consume DEDENT here - leave it for the main parse loop
        else:
            # Single line block (no indentation)
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        
        return Statement.Block(statements)
    
    def try_statement(self):
        """Parse try-except-finally statement"""
        # Parse try block
        self.consume_block_starter("Expected ':' or 'chita' after 'kuyesera'.")
        try_block = self.block()
        
        # Consume DEDENT after try block
        if self.check('DEDENT'):
            self.advance()
        
        # Parse except blocks (zakanika)
        except_blocks = []
        while self.check('KEYWORD') and self.peek()['value'] == 'zakanika':
            self.advance()  # consume 'zakanika'
            
            # Check for exception type specification and variable capture
            exception_type = None
            exception_var = None
            
            # Check for exception type (could be IDENTIFIER or KEYWORD for Chichewa types)
            if self.check('IDENTIFIER') or (self.check('KEYWORD') and self.peek()['value'].startswith('vuto_') or self.peek()['value'] == 'cholakwika_kiyi'):
                exception_type = self.advance()['value']
                
                # Check for 'chifukwa' (as) for exception variable capture
                if self.check('KEYWORD') and self.peek()['value'] == 'chifukwa':
                    self.advance()  # consume 'chifukwa'
                    if self.check('IDENTIFIER'):
                        exception_var = self.advance()['value']
                    else:
                        raise Exception("Expected variable name after 'chifukwa'")
            # Also check for 'chifukwa' without exception type
            elif self.check('KEYWORD') and self.peek()['value'] == 'chifukwa':
                self.advance()  # consume 'chifukwa'
                if self.check('IDENTIFIER'):
                    exception_var = self.advance()['value']
                else:
                    raise Exception("Expected variable name after 'chifukwa'")
            
            self.consume_block_starter("Expected ':' or 'chita' after except clause.")
            except_block = self.block()
            except_blocks.append((exception_type, exception_var, except_block))
            
            # Consume DEDENT after except block
            if self.check('DEDENT'):
                self.advance()
        
        # Parse finally block (pomaliza) if present
        finally_block = None
        if self.check('KEYWORD') and self.peek()['value'] == 'pomaliza':
            self.advance()  # consume 'pomaliza'
            self.consume_block_starter("Expected ':' or 'chita' after 'pomaliza'.")
            finally_block = self.block()
            
            # Consume DEDENT after finally block
            if self.check('DEDENT'):
                self.advance()
        
        # Must have at least one except block or finally block
        if not except_blocks and not finally_block:
            raise Exception("Try statement must have at least one 'zakanika' or 'pomaliza' clause")
        
        return Statement.TryExcept(try_block, except_blocks, finally_block)
    
    def dict_literal(self):
        """Parse dictionary literal {key: value, key2: value2}"""
        pairs = []
        
        # Handle empty dictionary {}
        if self.check('BRACE') and self.peek()['value'] == '}':
            self.advance()  # consume '}'
            return Expression.DictLiteral(pairs)
        
        # Parse key-value pairs
        while True:
            # Parse key
            key = self.expression()
            
            # Expect colon
            if not (self.check('PUNCTUATION') and self.peek()['value'] == ':'):
                raise Exception("Expected ':' after dictionary key")
            self.advance()  # consume ':'
            
            # Parse value
            value = self.expression()
            pairs.append((key, value))
            
            # Check for comma (more pairs) or closing brace
            if self.check('PUNCTUATION') and self.peek()['value'] == ',':
                self.advance()  # consume ','
                # Check if this is a trailing comma before }
                if self.check('BRACE') and self.peek()['value'] == '}':
                    break
            elif self.check('BRACE') and self.peek()['value'] == '}':
                break
            else:
                raise Exception("Expected ',' or '}' in dictionary literal")
        
        # Consume closing brace
        if not (self.check('BRACE') and self.peek()['value'] == '}'):
            raise Exception("Expected '}' to close dictionary literal")
        self.advance()  # consume '}'
        
        return Expression.DictLiteral(pairs)
    
    def process_escape_sequences(self, raw_string):
        """Process escape sequences in strings"""
        result = ""
        i = 0
        while i < len(raw_string):
            if raw_string[i] == '\\' and i + 1 < len(raw_string):
                next_char = raw_string[i + 1]
                if next_char == 'n':
                    result += '\n'
                elif next_char == 't':
                    result += '\t'
                elif next_char == 'r':
                    result += '\r'
                elif next_char == '\\':
                    result += '\\'
                elif next_char == '"':
                    result += '"'
                elif next_char == '\'':
                    result += '\''
                else:
                    # Unknown escape sequence, keep as is
                    result += raw_string[i:i+2]
                i += 2  # Skip both characters
            else:
                result += raw_string[i]
                i += 1
        return result
