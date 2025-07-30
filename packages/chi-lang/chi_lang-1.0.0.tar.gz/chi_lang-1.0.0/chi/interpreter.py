# Control flow exceptions
class BreakException(Exception):
    """Exception to handle break statements"""
    pass

class ContinueException(Exception):
    """Exception to handle continue statements"""
    pass

class ReturnException(Exception):
    """Exception to handle return statements"""
    def __init__(self, value):
        self.value = value
        super().__init__()

class ChiBoolean:
    """Custom boolean type for Chi language"""
    def __init__(self, value):
        self.value = bool(value)
    
    def __bool__(self):
        return self.value
    
    def __str__(self):
        return "zoona" if self.value else "zabodza"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, ChiBoolean):
            return self.value == other.value
        return self.value == bool(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)

class ChiNull:
    """Custom null type for Chi language"""
    def __init__(self):
        pass
    
    def __bool__(self):
        return False
    
    def __str__(self):
        return "palibe"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return isinstance(other, ChiNull) or other is None
    
    def __ne__(self, other):
        return not self.__eq__(other)

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name)
        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'.")


class Expression:
    class Literal:
        def __init__(self, value):
            self.value = value

        def evaluate(self, env):
            return self.value

    class Variable:
        def __init__(self, name):
            self.name = name

        def evaluate(self, env):
            return env.get(self.name)

    class FunctionCall:
        def __init__(self, callee, arguments):
            self.callee = callee
            self.arguments = arguments

        def evaluate(self, env):
            if isinstance(self.callee, Expression.Variable):
                func_name = self.callee.name
                func = env.get(func_name)
                if callable(func):
                    args = [arg.evaluate(env) for arg in self.arguments]
                    return func(*args)
                else:
                    raise RuntimeError(f"'{func_name}' is not a function.")
            else:
                raise RuntimeError("Invalid function call target.")
    
    class Index:
        def __init__(self, object_expr, index_expr):
            self.object_expr = object_expr
            self.index_expr = index_expr
        
        def evaluate(self, env):
            obj = self.object_expr.evaluate(env)
            index = self.index_expr.evaluate(env)
            
            try:
                # Check if it's a dictionary access
                if isinstance(obj, ChiDict):
                    return obj[index]  # Use key directly for dictionary
                else:
                    # For lists, convert index to integer
                    return obj[int(index)]
            except IndexError as e:
                # Raise the original IndexError instead of RuntimeError
                raise IndexError(f"List index out of range")
            except KeyError as e:
                # Handle dictionary key errors
                raise KeyError(f"Key '{index}' not found in dictionary")
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Index error: {e}")
    
    class Slice:
        def __init__(self, object_expr, start_expr, end_expr):
            self.object_expr = object_expr
            self.start_expr = start_expr
            self.end_expr = end_expr
        
        def evaluate(self, env):
            obj = self.object_expr.evaluate(env)
            
            # Evaluate start and end indices (can be None)
            start = None if self.start_expr is None else int(self.start_expr.evaluate(env))
            end = None if self.end_expr is None else int(self.end_expr.evaluate(env))
            
            try:
                # For now, only support slicing on lists and strings
                if isinstance(obj, (ChiList, list, str)):
                    return obj[start:end]
                else:
                    raise RuntimeError(f"Cannot slice object of type {type(obj).__name__}")
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Slice error: {e}")
    
    class MethodCall:
        def __init__(self, object_expr, method_name, arguments):
            self.object_expr = object_expr
            self.method_name = method_name
            self.arguments = arguments
        
        def evaluate(self, env):
            obj = self.object_expr.evaluate(env)
            args = [arg.evaluate(env) for arg in self.arguments]
            
            # Map Chichewa method names to their actual method names
            method_mapping = {
                # List methods
                'onjezera': 'append',
                'lowetsa': 'insert', 
                'chotsa': 'remove',
                'tulutsa': 'pop',
                'funafuna': 'index',
                'werengera': 'count',
                # String methods (Chichewa names mapped to custom implementations)
                'chotsani_mimpata': 'chotsani_mimpata',  # strip
                'gawani': 'gawani',                      # split
                'lumikizani': 'lumikizani',              # join
                'sinthani': 'sinthani',                  # replace
                'zikuluzikulu': 'zikuluzikulu',          # upper
                'zingonozingono': 'zingonozingono',      # lower
                'yoyamba_ndi': 'yoyamba_ndi',            # startswith
                'imamaliza_ndi': 'imamaliza_ndi',        # endswith
                'ili_nacho': 'ili_nacho',                # contains (for strings)
                'kutalika': 'kutalika',                  # length
                'bwezerani': 'bwezerani',                # reverse
                'bwerezani': 'bwerezani',                    # repeat
                'dulani': 'dulani',                    # slice (method version)
                # Dictionary methods (keep Chichewa names since they're implemented directly)
                'ika_pa': 'ika_pa',
                'peza': 'peza',
                'peza_kapena': 'peza_kapena',
                'ali_nacho_dict': 'ali_nacho',  # Dictionary version
                'chotsa_pa': 'chotsa_pa',
                'chotsani_zonse': 'chotsani_zonse',
                'makiyi': 'makiyi',
                'mavalu': 'mavalu',
                'zonse': 'zonse',
                'kopani': 'kopani',
                'sanjirani': 'sanjirani',
                # File methods (keep Chichewa names since they're implemented directly)
                'werenga': 'werenga',
                'werenga_mizere': 'werenga_mizere',
                'lemba': 'lemba',
                'lemba_mzere': 'lemba_mzere',
                'tseka': 'tseka'
            }
            
            # Get the actual method name (English or Chichewa)
            actual_method = method_mapping.get(self.method_name, self.method_name)
            
            # Handle special cases for methods that need integer arguments
            if actual_method in ['insert', 'pop'] and args:
                # Convert first argument to int for insert/pop methods
                if actual_method == 'insert' and len(args) >= 1:
                    args[0] = int(args[0])
                elif actual_method == 'pop' and len(args) >= 1:
                    args[0] = int(args[0])
            
            # Handle string methods with custom implementations
            if isinstance(obj, str) and actual_method in ['chotsani_mimpata', 'gawani', 'lumikizani', 'sinthani', 'zikuluzikulu', 'zingonozingono', 'yoyamba_ndi', 'imamaliza_ndi', 'ili_nacho', 'kutalika', 'bwezerani', 'bwerezani', 'dulani']:
                return self._execute_string_method(obj, actual_method, args)
            
            # Check if the object has the method
            if hasattr(obj, actual_method):
                method = getattr(obj, actual_method)
                return method(*args)
            else:
                raise RuntimeError(f"Object has no method '{self.method_name}'")
        
        def _execute_string_method(self, string_obj, method_name, args):
            """Execute Chichewa string methods"""
            if method_name == 'chotsani_mimpata':
                # Strip whitespace from both ends
                return string_obj.strip()
            
            elif method_name == 'gawani':
                # Split string by delimiter (default: space)
                delimiter = args[0] if args else " "
                return ChiList(*string_obj.split(str(delimiter)))
            
            elif method_name == 'lumikizani':
                # Join - string acts as separator for a list
                if not args or not hasattr(args[0], '__iter__'):
                    raise RuntimeError("lumikizani requires a list to join")
                items = args[0]
                if isinstance(items, ChiList):
                    items = items.items
                return string_obj.join(str(item) for item in items)
            
            elif method_name == 'sinthani':
                # Replace old with new
                if len(args) < 2:
                    raise RuntimeError("sinthani requires 2 arguments: old, new")
                old, new = str(args[0]), str(args[1])
                count = int(args[2]) if len(args) > 2 else -1
                return string_obj.replace(old, new, count)
            
            elif method_name == 'zikuluzikulu':
                # Convert to uppercase
                return string_obj.upper()
            
            elif method_name == 'zingonozingono':
                # Convert to lowercase
                return string_obj.lower()
            
            elif method_name == 'yoyamba_ndi':
                # Check if string starts with prefix
                if not args:
                    raise RuntimeError("yoyamba_ndi requires a prefix argument")
                prefix = str(args[0])
                return ChiBoolean(string_obj.startswith(prefix))
            
            elif method_name == 'imamaliza_ndi':
                # Check if string ends with suffix
                if not args:
                    raise RuntimeError("imamaliza_ndi requires a suffix argument")
                suffix = str(args[0])
                return ChiBoolean(string_obj.endswith(suffix))
            
            elif method_name == 'ili_nacho':
                # Check if string contains substring
                if not args:
                    raise RuntimeError("ili_nacho requires a substring argument")
                substring = str(args[0])
                return ChiBoolean(substring in string_obj)
            
            elif method_name == 'kutalika':
                # Get string length
                return len(string_obj)
            
            elif method_name == 'bwezerani':
                # Reverse string
                return string_obj[::-1]
            
            elif method_name == 'bwerezani':
                # Repeat string n times
                if not args:
                    raise RuntimeError("bwerezani requires a count argument")
                count = int(args[0])
                return string_obj * count
            
            elif method_name == 'dulani':
                # Slice string (start, end)
                if len(args) == 1:
                    # Single argument - slice from start to that position
                    end = int(args[0])
                    return string_obj[:end]
                elif len(args) == 2:
                    # Two arguments - slice from start to end
                    start, end = int(args[0]), int(args[1])
                    return string_obj[start:end]
                else:
                    raise RuntimeError("dulani requires 1 or 2 arguments: end, or start and end")
            
            else:
                raise RuntimeError(f"Unknown string method: {method_name}")
    
    class PropertyAccess:
        def __init__(self, object_expr, property_name):
            self.object_expr = object_expr
            self.property_name = property_name
        
        def evaluate(self, env):
            obj = self.object_expr.evaluate(env)
            
            # For properties, we might want to handle special cases
            # For now, just return the attribute if it exists  
            if hasattr(obj, self.property_name):
                return getattr(obj, self.property_name)
            else:
                raise RuntimeError(f"Object has no property '{self.property_name}'")
    
    class Binary:
        def __init__(self, left, operator, right):
            self.left = left
            self.operator = operator
            self.right = right
            
        def evaluate(self, env):
            left_val = self.left.evaluate(env)
            right_val = self.right.evaluate(env)
            
            if self.operator == '==':
                return ChiBoolean(left_val == right_val)
            elif self.operator == '!=':
                return ChiBoolean(left_val != right_val)
            elif self.operator == '>':
                return ChiBoolean(left_val > right_val)
            elif self.operator == '<':
                return ChiBoolean(left_val < right_val)
            elif self.operator == '>=':
                return ChiBoolean(left_val >= right_val)
            elif self.operator == '<=':
                return ChiBoolean(left_val <= right_val)
            elif self.operator == 'and':
                return ChiBoolean(bool(left_val) and bool(right_val))
            elif self.operator == 'or':
                return ChiBoolean(bool(left_val) or bool(right_val))
            elif self.operator == '+':
                return left_val + right_val
            elif self.operator == '-':
                return left_val - right_val
            elif self.operator == '*':
                return left_val * right_val
            elif self.operator == '/':
                return left_val / right_val
            elif self.operator == '**':
                return left_val ** right_val
            elif self.operator == '%':
                return left_val % right_val
            
            raise RuntimeError(f"Unknown binary operator: {self.operator}")
    
    class Unary:
        def __init__(self, operator, right):
            self.operator = operator
            self.right = right
            
        def evaluate(self, env):
            right_val = self.right.evaluate(env)
            
            if self.operator == 'not':
                return ChiBoolean(not bool(right_val))
            elif self.operator == '-':
                return -right_val
                
            raise RuntimeError(f"Unknown unary operator: {self.operator}")
    
    class DictLiteral:
        def __init__(self, pairs):
            self.pairs = pairs  # List of (key_expr, value_expr) tuples
        
        def evaluate(self, env):
            # Evaluate all key-value pairs and create ChiDict
            items = {}
            for key_expr, value_expr in self.pairs:
                key = key_expr.evaluate(env)
                value = value_expr.evaluate(env)
                items[key] = value
            return ChiDict(items)


class Statement:
    class VarDeclaration:
        def __init__(self, name, initializer):
            self.name = name
            self.initializer = initializer

        def execute(self, env):
            value = self.initializer.evaluate(env)
            env.define(self.name, value)

    class Print:
        def __init__(self, expressions):
            self.expressions = expressions  # list of expressions

        def execute(self, env):
            values = [expr.evaluate(env) for expr in self.expressions]
            print(*values)

    class Expression:
        def __init__(self, expression):
            self.expression = expression

        def execute(self, env):
            self.expression.evaluate(env)

    class If:
        def __init__(self, condition, then_branch, else_branch=None, elif_branches=None):
            self.condition = condition
            self.then_branch = then_branch
            self.else_branch = else_branch
            self.elif_branches = elif_branches or []

        def execute(self, env):
            if self.condition.evaluate(env):
                self.then_branch.execute(env)
            else:
                # Check elif branches
                for elif_condition, elif_body in self.elif_branches:
                    if elif_condition.evaluate(env):
                        elif_body.execute(env)
                        return
                # If no elif matched, execute else
                if self.else_branch:
                    self.else_branch.execute(env)

    class While:
        def __init__(self, condition, body):
            self.condition = condition
            self.body = body

        def execute(self, env):
            try:
                while self.condition.evaluate(env):
                    try:
                        self.body.execute(env)
                    except ContinueException:
                        continue  # Skip to next iteration
            except BreakException:
                pass  # Exit the loop

    class For:
        def __init__(self, var_name, iterable, body):
            self.var_name = var_name
            self.iterable = iterable
            self.body = body

        def execute(self, env):
            iterable_val = self.iterable.evaluate(env)
            try:
                for item in iterable_val:
                    env.define(self.var_name, item)
                    try:
                        self.body.execute(env)
                    except ContinueException:
                        continue  # Skip to next iteration
            except BreakException:
                pass  # Exit the loop

    class Break:
        def __init__(self):
            pass
        
        def execute(self, env):
            raise BreakException()
    
    class Continue:
        def __init__(self):
            pass
        
        def execute(self, env):
            raise ContinueException()
    
    class Block:
        def __init__(self, statements):
            self.statements = statements

        def execute(self, env):
            for stmt in self.statements:
                stmt.execute(env)
    
    class FunctionDefinition:
        def __init__(self, name, params, body):
            self.name = name
            self.params = params
            self.body = body
        
        def execute(self, env):
            # Create a ChiFunction object and define it in the environment
            function = ChiFunction(self.name, self.params, self.body, env)
            env.define(self.name, function)
    
    class Return:
        def __init__(self, value):
            self.value = value
        
        def execute(self, env):
            val = None if self.value is None else self.value.evaluate(env)
            raise ReturnException(val)
    
    class TryExcept:
        def __init__(self, try_block, except_blocks, finally_block=None):
            self.try_block = try_block
            self.except_blocks = except_blocks  # list of (exception_type, exception_var, block)
            self.finally_block = finally_block
        
        def execute(self, env):
            exception_occurred = False
            caught_exception = None
            
            try:
                # Execute try block
                self.try_block.execute(env)
            except Exception as e:
                exception_occurred = True
                caught_exception = e
                
                # Try to match exception with except blocks
                handled = False
                for exception_type, exception_var, except_block in self.except_blocks:
                    if exception_type is None:  # Catch all exceptions
                        if exception_var:
                            # Store exception in variable
                            env.define(exception_var, str(e))
                        except_block.execute(env)
                        handled = True
                        break
                    else:
                        # Map Chichewa exception types to English equivalents
                        chichewa_to_english = {
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
                        
                        exception_name = type(e).__name__
                        
                        # Check if the exception type matches (either Chichewa or English)
                        expected_english = chichewa_to_english.get(exception_type, exception_type)
                        
                        # Debug print to see what's happening
                        # print(f"Debug: exception_type={exception_type}, exception_name={exception_name}, expected_english={expected_english}")
                        
                        if (exception_name == expected_english or 
                            exception_type == "Exception" or 
                            exception_type == "vuto_lililonse" or
                            (exception_type in chichewa_to_english and exception_name == chichewa_to_english[exception_type])):
                            if exception_var:
                                # Store exception in variable
                                env.define(exception_var, str(e))
                            except_block.execute(env)
                            handled = True
                            break
                
                # If no except block handled the exception, re-raise it
                if not handled:
                    if self.finally_block:
                        self.finally_block.execute(env)
                    raise e
            finally:
                # Always execute finally block if present
                if self.finally_block:
                    self.finally_block.execute(env)


class ChiDict:
    """Custom dictionary type for Chi language with Chichewa methods"""
    def __init__(self, *args):
        self.items = {}
        # Handle key-value pairs from arguments
        if len(args) % 2 == 0:
            for i in range(0, len(args), 2):
                self.items[args[i]] = args[i + 1]
        elif len(args) == 1 and isinstance(args[0], dict):
            self.items = args[0].copy()
    
    def __getitem__(self, key):
        """Enable indexing with []"""
        return self.items[key]
    
    def __setitem__(self, key, value):
        """Enable item assignment with []"""
        self.items[key] = value
    
    def __len__(self):
        return len(self.items)
    
    def __iter__(self):
        return iter(self.items)
    
    def __str__(self):
        return str(self.items)
    
    def __repr__(self):
        pairs = [f"{repr(k)}: {repr(v)}" for k, v in self.items.items()]
        return f"ChiDict({{{', '.join(pairs)}}})"
    
    def __contains__(self, key):
        """Support 'in' operator"""
        return key in self.items
    
    # Chichewa dictionary methods
    def ika_pa(self, key, value):
        """Put at - set key-value pair"""
        self.items[key] = value
    
    def peza(self, key):
        """Find/get - get value by key"""
        return self.items[key]
    
    def peza_kapena(self, key, default=None):
        """Find or default - get value with fallback"""
        return self.items.get(key, default)
    
    def ali_nacho(self, key):
        """Has it - check if key exists"""
        return ChiBoolean(key in self.items)
    
    def chotsa_pa(self, key):
        """Remove from - pop key and return value"""
        return self.items.pop(key)
    
    def chotsani_zonse(self):
        """Remove all - clear dictionary"""
        self.items.clear()
    
    def makiyi(self):
        """The keys - get all keys"""
        return ChiList(*list(self.items.keys()))
    
    def mavalu(self):
        """The values - get all values"""
        return ChiList(*list(self.items.values()))
    
    def zonse(self):
        """Everything - get all key-value pairs"""
        pairs = [ChiList(k, v) for k, v in self.items.items()]
        return ChiList(*pairs)
    
    def kopani(self):
        """Copy - create a copy of the dictionary"""
        return ChiDict(self.items)
    
    def sanjirani(self, other):
        """Join/merge - update with another dictionary"""
        if isinstance(other, ChiDict):
            self.items.update(other.items)
        elif isinstance(other, dict):
            self.items.update(other)
        else:
            raise RuntimeError("Can only merge with another kaundula (dictionary)")

class ChiList:
    """Custom list type for Chi language with indexing capability"""
    def __init__(self, *args):
        self.items = list(args)
    
    def __getitem__(self, index):
        """Enable indexing with []"""
        return self.items[index]
    
    def __setitem__(self, index, value):
        """Enable item assignment with []"""
        self.items[index] = value
    
    def __len__(self):
        return len(self.items)
    
    def __iter__(self):
        return iter(self.items)
    
    def __str__(self):
        return str(self.items)
    
    def __repr__(self):
        return f"ChiList({', '.join(map(repr, self.items))})"
    
    def append(self, item):
        """Add item to end of list"""
        self.items.append(item)
    
    def insert(self, index, item):
        """Insert item at specific index"""
        self.items.insert(index, item)
    
    def remove(self, item):
        """Remove first occurrence of item"""
        self.items.remove(item)
    
    def pop(self, index=-1):
        """Remove and return item at index (default last)"""
        return self.items.pop(index)
    
    def index(self, item):
        """Return index of first occurrence of item"""
        return self.items.index(item)
    
    def count(self, item):
        """Return number of occurrences of item"""
        return self.items.count(item)

class Interpreter:
    def __init__(self):
        self.env = Environment()
        # Optional: define built-ins if needed
        self.env.define('onetsa', print)
        self.env.define('ndandanda', lambda *args: ChiList(*args))
        self.env.define('kaundula', lambda *args: ChiDict(*args))
        self.env.define('funsani', lambda prompt="": input(prompt))
        
        # Type conversion functions with proper error handling
        def chi_str(value):
            return str(value)
        
        def chi_float(value):
            try:
                return float(value)
            except (ValueError, TypeError) as e:
                # Raise the original exception type instead of RuntimeError
                raise type(e)(f"Cannot convert '{value}' to float")
        
        def chi_int(value):
            try:
                return int(float(value))
            except (ValueError, TypeError) as e:
                # Raise the original exception type instead of RuntimeError
                raise type(e)(f"Cannot convert '{value}' to integer")
        
        self.env.define('mawu', chi_str)  # Convert to string
        self.env.define('manambala', chi_float)  # Convert to float
        self.env.define('manambala_olekeza', chi_int)  # Convert to int
        
        # Utility functions
        def chi_len(obj):
            try:
                return len(obj)
            except TypeError:
                raise RuntimeError(f"Object of type '{type(obj).__name__}' has no length")
        
        self.env.define('kukula', chi_len)  # Get length/size
        
        # Type checking function
        def chi_type(obj):
            """Return Chichewa type name for any object"""
            if isinstance(obj, ChiBoolean):
                return "yankho"  # boolean type
            elif isinstance(obj, ChiNull):
                return "palibe_mtundu"  # null type  
            elif isinstance(obj, str):
                return "mawu"  # string
            elif isinstance(obj, float):
                return "manambala"  # float number
            elif isinstance(obj, int):
                return "manambala_olekeza"  # integer
            elif isinstance(obj, ChiList):
                return "ndandanda"  # list
            elif isinstance(obj, ChiDict):
                return "kaundula"  # dictionary
            elif isinstance(obj, ChiFile):
                return "fayilo"  # file
            else:
                return "chinthu"  # generic object/thing
        
        self.env.define('mtundu', chi_type)  # Get type
        
        # Advanced mathematical functions
        import math
        
        def chi_power(base, exponent):
            """Power function - base raised to exponent"""
            try:
                return base ** exponent
            except (TypeError, ValueError, OverflowError) as e:
                raise RuntimeError(f"Power calculation error: {e}")
        
        def chi_modulo(dividend, divisor):
            """Modulo function - remainder of division"""
            try:
                return dividend % divisor
            except (TypeError, ZeroDivisionError) as e:
                raise RuntimeError(f"Modulo calculation error: {e}")
        
        def chi_sqrt(number):
            """Square root function"""
            try:
                return math.sqrt(float(number))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Square root calculation error: {e}")
        
        def chi_abs(number):
            """Absolute value function"""
            try:
                return abs(float(number))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Absolute value calculation error: {e}")
        
        def chi_floor(number):
            """Floor function - round down to nearest integer"""
            try:
                return math.floor(float(number))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Floor calculation error: {e}")
        
        def chi_ceil(number):
            """Ceiling function - round up to nearest integer"""
            try:
                return math.ceil(float(number))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Ceiling calculation error: {e}")
        
        def chi_round(number, digits=0):
            """Round function"""
            try:
                return round(float(number), int(digits))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Round calculation error: {e}")
        
        def chi_sum(*args):
            """Sum function - add all arguments"""
            try:
                if len(args) == 0:
                    return 0
                
                # Handle single ChiList argument
                if len(args) == 1 and isinstance(args[0], ChiList):
                    values = args[0].items
                else:
                    values = args
                
                # Filter out null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                return sum(values)
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Sum calculation error: {e}")
        
        def chi_avg(*args):
            """Average function - mean of all arguments"""
            try:
                if len(args) == 0:
                    raise RuntimeError("Cannot calculate average of empty set")
                
                # Handle single ChiList argument
                if len(args) == 1 and isinstance(args[0], ChiList):
                    values = args[0].items
                else:
                    values = args
                
                # Filter out null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                if len(values) == 0:
                    raise RuntimeError("Cannot calculate average: all values are null")
                
                return sum(values) / len(values)
            except (TypeError, ValueError, ZeroDivisionError) as e:
                raise RuntimeError(f"Average calculation error: {e}")
        
        def chi_max(*args):
            """Maximum function"""
            try:
                if len(args) == 0:
                    raise RuntimeError("Cannot find maximum of empty set")
                
                # Handle single ChiList argument
                if len(args) == 1 and isinstance(args[0], ChiList):
                    values = args[0].items
                else:
                    values = args
                
                # Filter out null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                if len(values) == 0:
                    raise RuntimeError("Cannot find maximum: all values are null")
                
                return max(values)
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Maximum calculation error: {e}")
        
        def chi_min(*args):
            """Minimum function"""
            try:
                if len(args) == 0:
                    raise RuntimeError("Cannot find minimum of empty set")
                
                # Handle single ChiList argument
                if len(args) == 1 and isinstance(args[0], ChiList):
                    values = args[0].items
                else:
                    values = args
                
                # Filter out null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                if len(values) == 0:
                    raise RuntimeError("Cannot find minimum: all values are null")
                
                return min(values)
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Minimum calculation error: {e}")
        
        def chi_sort(data, koyambila="koyamba"):
            """Sort function - arrange values with direction
            koyambila: 'koyamba' (ascending) or 'komaliza' (descending)
            """
            try:
                # Handle different input types
                if hasattr(data, '__iter__') and not isinstance(data, str):
                    # If data is a list or iterable
                    values = list(data)
                else:
                    # Single value
                    values = [data]
                
                # Determine sort direction
                if koyambila == "komaliza":
                    # Descending order (start from end/largest)
                    sorted_items = sorted(values, reverse=True)
                elif koyambila == "koyamba":
                    # Ascending order (start from beginning/smallest) 
                    sorted_items = sorted(values)
                else:
                    # Default to ascending if direction not recognized
                    sorted_items = sorted(values)
                
                return ChiList(*sorted_items)
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Sort calculation error: {e}")
        
        def chi_median(*args):
            """Median function - middle value when sorted"""
            try:
                if len(args) == 0:
                    raise RuntimeError("Cannot find median of empty set")
                
                if len(args) == 1 and hasattr(args[0], '__iter__') and not isinstance(args[0], str):
                    # If single argument is a list, find median of that list
                    values = list(args[0])
                else:
                    # Find median of all arguments
                    values = list(args)
                
                # Remove null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                if len(values) == 0:
                    raise RuntimeError("Cannot find median: all values are null")
                
                sorted_values = sorted(values)
                n = len(sorted_values)
                
                if n % 2 == 1:
                    # Odd number of values
                    return sorted_values[n // 2]
                else:
                    # Even number of values - average of two middle values
                    mid1 = sorted_values[n // 2 - 1]
                    mid2 = sorted_values[n // 2]
                    return (mid1 + mid2) / 2
                    
            except (TypeError, ValueError, ZeroDivisionError) as e:
                raise RuntimeError(f"Median calculation error: {e}")
        
        def chi_mode(*args):
            """Mode function - most frequently occurring value"""
            try:
                if len(args) == 0:
                    raise RuntimeError("Cannot find mode of empty set")
                
                if len(args) == 1 and hasattr(args[0], '__iter__') and not isinstance(args[0], str):
                    # If single argument is a list, find mode of that list
                    values = list(args[0])
                else:
                    # Find mode of all arguments
                    values = list(args)
                
                # Remove null values
                values = [v for v in values if not isinstance(v, ChiNull) and v is not None]
                
                if len(values) == 0:
                    raise RuntimeError("Cannot find mode: all values are null")
                
                # Count occurrences
                from collections import Counter
                counts = Counter(values)
                
                # Find maximum frequency
                max_count = max(counts.values())
                
                # Find all values with maximum frequency
                modes = [value for value, count in counts.items() if count == max_count]
                
                if len(modes) == 1:
                    return modes[0]
                else:
                    # Multiple modes - return list of modes
                    return ChiList(*modes)
                    
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Mode calculation error: {e}")
        
        # Register advanced math functions with Chichewa names
        self.env.define('mphamvu', chi_power)      # Power - "strength/power"
        self.env.define('chotsalira', chi_modulo)   # Modulo - "remainder"
        self.env.define('muzu', chi_sqrt)          # Square root - "root"
        self.env.define('chopanda', chi_abs)       # Absolute value - "without sign"
        self.env.define('pansi', chi_floor)        # Floor - "down/below"
        self.env.define('pamwamba', chi_ceil)      # Ceiling - "up/above"
        self.env.define('zungulira', chi_round)    # Round - "to go around" (updated)
        self.env.define('phatikiza', chi_sum)      # Sum - "to add together"
        self.env.define('pakatikati', chi_avg)     # Average - "in the middle"
        self.env.define('chachikulu', chi_max)     # Maximum - "the biggest"
        self.env.define('chachingono', chi_min)    # Minimum - "the smallest"
        
        # Statistical and sorting functions
        self.env.define('sanja', chi_sort)         # Sort - "to arrange/organize"
        self.env.define('chapakati', chi_median)   # Median - "in the middle"
        self.env.define('yofala', chi_mode)        # Mode - "most frequent"
        
        # File operation functions
        import os
        
        def chi_open_file(filename, mode="werenga"):
            """Open file with Chichewa mode - tsegula means 'to open'"""
            try:
                return ChiFile(filename, mode)
            except Exception as e:
                raise RuntimeError(f"Cannot open file '{filename}': {e}")
        
        def chi_read_entire_file(filename):
            """Read entire file content - werenga_zonse means 'read everything'"""
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise RuntimeError(f"File '{filename}' not found")
            except Exception as e:
                raise RuntimeError(f"Error reading file '{filename}': {e}")
        
        def chi_write_to_file(filename, content):
            """Write content to file - lemba_mu_file means 'write in file'"""
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(content))
                return True
            except Exception as e:
                raise RuntimeError(f"Error writing to file '{filename}': {e}")
        
        def chi_file_exists(filename):
            """Check if file exists - pezani_file means 'find file'"""
            try:
                return ChiBoolean(os.path.exists(filename))
            except Exception as e:
                raise RuntimeError(f"Error checking file '{filename}': {e}")
        
        # Register file operation functions
        self.env.define('tsegula', chi_open_file)           # Open file
        self.env.define('werenga_zonse', chi_read_entire_file)  # Read entire file
        self.env.define('lemba_mu_file', chi_write_to_file)    # Write to file
        self.env.define('pezani_file', chi_file_exists)        # Check if file exists

    def interpret(self, statements):
        try:
            for stmt in statements:
                stmt.execute(self.env)
        except RuntimeError as e:
            print(f"Runtime error: {e}")

class ChiFile:
    """File object for Chi language with Chichewa methods"""
    def __init__(self, filename, mode="read"):
        self.filename = filename
        self.mode = mode
        self.file_obj = None
        self.is_open = False
        
        # Map Chichewa modes to Python modes
        mode_mapping = {
            "werenga": "r",     # read
            "lemba": "w",       # write
            "wonjezera": "a",   # append
            "read": "r",        # English fallback
            "write": "w",       # English fallback
            "append": "a"       # English fallback
        }
        
        python_mode = mode_mapping.get(mode, "r")
        
        try:
            self.file_obj = open(filename, python_mode, encoding='utf-8')
            self.is_open = True
        except Exception as e:
            raise RuntimeError(f"Cannot open file '{filename}': {e}")
    
    def werenga(self, size=None):
        """Read from file - werenga means 'to read'"""
        if not self.is_open or not self.file_obj:
            raise RuntimeError("File is not open for reading")
        try:
            if size is None:
                return self.file_obj.read()
            else:
                return self.file_obj.read(int(size))
        except Exception as e:
            raise RuntimeError(f"Error reading file: {e}")
    
    def werenga_mizere(self):
        """Read all lines - werenga mizere means 'read lines'"""
        if not self.is_open or not self.file_obj:
            raise RuntimeError("File is not open for reading")
        try:
            lines = self.file_obj.readlines()
            # Remove newlines and return as ChiList
            cleaned_lines = [line.rstrip('\n') for line in lines]
            return ChiList(*cleaned_lines)
        except Exception as e:
            raise RuntimeError(f"Error reading lines: {e}")
    
    def lemba(self, content):
        """Write to file - lemba means 'to write'"""
        if not self.is_open or not self.file_obj:
            raise RuntimeError("File is not open for writing")
        try:
            self.file_obj.write(str(content))
            self.file_obj.flush()  # Ensure content is written
        except Exception as e:
            raise RuntimeError(f"Error writing to file: {e}")
    
    def lemba_mzere(self, content):
        """Write line to file - lemba mzere means 'write line'"""
        if not self.is_open or not self.file_obj:
            raise RuntimeError("File is not open for writing")
        try:
            self.file_obj.write(str(content) + '\n')
            self.file_obj.flush()
        except Exception as e:
            raise RuntimeError(f"Error writing line: {e}")
    
    def tseka(self):
        """Close file - tseka means 'to close'"""
        if self.is_open and self.file_obj:
            try:
                self.file_obj.close()
                self.is_open = False
                self.file_obj = None
            except Exception as e:
                raise RuntimeError(f"Error closing file: {e}")
    
    def __str__(self):
        status = "open" if self.is_open else "closed"
        return f"ChiFile('{self.filename}', mode='{self.mode}', status='{status}')"
    
    def __repr__(self):
        return self.__str__()
    
    def __del__(self):
        # Automatically close file when object is destroyed
        if self.is_open:
            self.tseka()

class ChiFunction:
    """User-defined function in Chi language"""
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure  # Environment where function was defined
    
    def __call__(self, *args):
        # Check parameter count
        if len(args) != len(self.params):
            expected = len(self.params)
            got = len(args)
            raise RuntimeError(f"Kufunika ma parameter {expected} koma mwapereka {got} ku '{self.name}'")
        
        # Create new environment for function execution
        func_env = Environment(self.closure)
        
        # Bind parameters to arguments
        for i, param in enumerate(self.params):
            func_env.define(param, args[i])
        
        # Execute function body
        try:
            self.body.execute(func_env)
            return None  # No explicit return
        except ReturnException as ret:
            return ret.value
