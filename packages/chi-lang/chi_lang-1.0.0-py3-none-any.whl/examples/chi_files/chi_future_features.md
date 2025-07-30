# Chi Programming Language - Future Features & Roadmap

## Current Working Features ✅

### 1. **Core Language Constructs**
- ✅ Variable declarations with `ika`
- ✅ Print function with `onetsa()`
- ✅ Boolean values: `zoona` (true), `zabodza` (false)
- ✅ Numbers (integers and floats)
- ✅ Strings
- ✅ Comments with `#`
- ✅ Type conversion functions: `mawu()`, `manambala()`, `manambala_olekeza()`

### 2. **Chichewa Operators**
- ✅ **Comparison Operators:**
  - `wafanana` (equals ==)
  - `wasiyana` (not equal !=)
  - `wapambana` (greater than >)
  - `wachepa` (less than <)
  - `wafananitsa` (greater than or equal >=)
  - `wachepetsedwa` (less than or equal <=)

- ✅ **Logical Operators:**
  - `komanso` (and)
  - `kapena` (or)
  - `osati` (not)

### 3. **Control Flow**
- ✅ If statements with `ngati`
- ✅ Elif statements with `kapena_ngati`
- ✅ Else statements with `sizoona`
- ✅ While loops with `yesani`
- ✅ For loops with `bwereza ... mu ...`
- ✅ Block syntax with `chita` (alternative to `:`)

### 4. **Data Structures**
- ✅ Lists with `ndandanda()`
- ✅ List iteration in for loops
- ✅ List methods in Chichewa (onjezera, chotsa, etc.)

### 5. **Type System** 
- ✅ Type checking with `mtundu()`
- ✅ Type conversion: `mawu()` (string), `manambala()` (float), `manambala_olekeza()` (int)
- ✅ Type names in Chichewa: "mawu", "manambala", "manambala_olekeza", "yankho", "palibe_mtundu"

### 5. **Expression System**
- ✅ Arithmetic operations (+, -, *, /)
- ✅ Operator precedence
- ✅ Parentheses for grouping
- ✅ Complex nested expressions

### 6. **Built-in Functions**
- ✅ Output: `onetsa()` - print/display values
- ✅ Input: `funsani()` - get user input
- ✅ Type checking: `mtundu()` - get type of value
- ✅ Length: `kukula()` - get length of strings, lists
- ✅ Math functions: `mphamvu()`, `muzu()`, `chopanda()`, etc.

---

## Planned Features for Next Updates 🚀

### **HIGH PRIORITY** 🔥

#### 1. **Function Definitions & Calls**
**Keywords Available:** `panga` (define function), `bweza` (return)

```chi
# Example future syntax:
panga calculate_area(length, width):
    ika area = length * width
    bweza area

# Function call
ika result = calculate_area(5, 3)
onetsa("Area:", result)
```

#### 2. **String Operations**
- String concatenation with `+`
- String length with `kukula()`
- String methods: `chotsani_mimpata()`, `gawani()`, `lumikizani()`, etc.
- String indexing and slicing
- Advanced string methods (upper, lower, split, etc.)

#### 3. **Better Error Handling**
- Line numbers in error messages
- Better syntax error reporting
- Runtime error context

### **MEDIUM PRIORITY** 📋

#### 4. **Advanced Data Structures**
- Dictionaries/Maps
- Sets
- Tuples
- Multi-dimensional arrays

#### 5. **File I/O Operations**
**Keywords Available:** `tsegula` (open), `werenga_zonse` (read all), `lemba_mu_file` (write to file)

```chi
# Future file operations:
lemba_mu_file("data.txt", "Hello from Chi!")
ika content = werenga_zonse("data.txt")
```

#### 7. **Module System**
- Import/export functionality
- Package management
- Standard library modules

#### 8. **Switch/Case Statements**
**Keywords Available:** `sankhani` (switch/case)

```chi
# Future switch syntax:
sankhani grade chita
    case "A": onetsa("Excellent!")
    case "B": onetsa("Good!")
    case "C": onetsa("Average")
    default: onetsa("Unknown grade")
```

### **LOW PRIORITY** 🔮

#### 9. **Object-Oriented Programming**
- Class definitions
- Inheritance
- Method definitions
- Constructor functions

#### 10. **Advanced Control Flow**
**Keywords Available:** `kulamulira` (control), `tsatira` (then/do), `konza` (setup/init)

#### 11. **Concurrency & Async**
- Thread support
- Async/await patterns
- Parallel processing

#### 12. **Standard Library Functions**
- Math functions (sin, cos, sqrt, etc.)
- Date and time operations
- Random number generation
- Regular expressions

---

## Interpreter Improvements Needed 🔧

### **Core Infrastructure**
1. **Memory Management**
   - Garbage collection
   - Better variable scoping
   - Memory leak prevention

2. **Performance Optimizations**
   - AST optimization
   - Bytecode compilation
   - JIT compilation for hot paths

3. **Debugging Support**
   - Step-through debugging
   - Breakpoints
   - Variable inspection
   - Call stack traces

### **Language Features**
1. **Type System**
   - Optional static typing
   - Type inference
   - Generic types
   - Union types

2. **Advanced Parsing**
   - Better operator precedence
   - Macro system
   - Pattern matching
   - Lambda expressions

### **Developer Experience**
1. **Better Tooling**
   - Syntax highlighting
   - Auto-completion
   - Linting
   - Formatting tools

2. **Documentation**
   - API documentation generator
   - Interactive tutorials
   - Code examples repository

---

## Unused Keywords Available 📝

These keywords are defined but not yet implemented:
- `yasiyana` (assignment - alternative syntax)
- `pansi` (down - directional)
- `pereka` (give - data passing)
- `ndipo` (and - alternative to komanso)
- `sati` (not - alternative to osati)

---

## Contributing Guidelines 🤝

### Implementation Priority Order:
1. Functions and return statements
2. Enhanced data types
3. String operations
4. Error handling improvements
5. File I/O operations
6. Advanced data structures

### Code Quality Requirements:
- Comprehensive test coverage
- Clear documentation
- Performance benchmarks
- Backward compatibility

---

## Version Roadmap 🗓️

- **v0.2.0** - Functions and enhanced data types
- **v0.3.0** - File I/O and string operations
- **v0.4.0** - Advanced data structures
- **v0.5.0** - Module system
- **v1.0.0** - Stable release with full feature set

---

**Chi Programming Language** - Making programming accessible in Chichewa! 🌍

