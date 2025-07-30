# Chi Programming Language Examples

This directory contains comprehensive examples demonstrating all features of the Chi programming language.

## Quick Start

### Command Line Usage

```bash
# List all available examples
chi run --list-examples

# Run an example
chi run --example hello_world

# View example source code
chi run --see hello_world

# Run example with verbose output
chi run --example simple_math --verbose
```

### Python Import Usage

```python
# Import specific examples
from chi.examples import hello_world
from chi.examples import simple_math

# Run examples
hello_world.run()
simple_math.run()

# View source code
hello_world.show()
print(simple_math.content)

# Capture output
output = hello_world.run(capture_output=True)
print(output)

# List all examples
from chi import examples
examples.list()
examples.help()
```

## Example Categories

### 1. Basic Language Features
- **hello_world.chi** - Simple hello world demonstration
- **simple_data_types.chi** - Basic data types (strings, numbers, booleans, null)
- **type_constructors.chi** - Type conversion functions (mawu, manambala, manambala_olekeza)
- **operators_demo.chi** - All arithmetic, comparison, and logical operators

### 2. Mathematical Operations
- **simple_math.chi** - Basic mathematical operations and functions
- **builtin_functions_demo.chi** - Built-in mathematical functions (mphamvu, muzu, chopanda, etc.)

### 3. Data Structures
- **simple_lists.chi** - Basic list operations that work reliably
- **list_operations_demo.chi** - Comprehensive list operations and methods
- **dictionary_operations_demo.chi** - Complete dictionary operations with all Chi methods
- **string_methods_demo.chi** - String manipulation methods and operations

### 4. Control Flow
- **control_structures_demo.chi** - If-else statements, loops, and control flow

### 5. Advanced Features
- **functions_demo.chi** - Function definition, parameters, return values, recursion
- **exception_handling_demo.chi** - Try-catch-finally with all Chi exception types
- **file_operations_demo.chi** - File reading, writing, and manipulation

### 6. Real-World Applications
- **real_world_app_demo.chi** - Complete student grade management system

## Feature Coverage

These examples demonstrate all features from the Chi language specification:

### ✅ Core Data Types
- Strings (mawu), Float/Integer Numbers (manambala/manambala_olekeza)
- Booleans (yankho - zoona/zabodza), Null Values (palibe)
- Lists (ndandanda), Dictionaries (kaundula), Files (fayilo)

### ✅ Language Constructs
- Variable declaration (ika), All operators (arithmetic, comparison, logical)
- Control flow (ngati/sizoona, yesani, bwereza/mu, leka/pitilizani)
- Function definition (panga), Exception handling (kuyesera/zakanika/pomaliza)

### ✅ Built-in Functions
- I/O: onetsa(), funsani()
- Utility: mtundu(), kukula()
- Type conversion: mawu(), manambala(), manambala_olekeza()
- Mathematical: mphamvu(), muzu(), chopanda(), zungulira(), etc.
- Statistical: phatikiza(), pakatikati(), chachikulu(), chachingono(), sanja()

### ✅ Methods and Operations
- String methods: All Chichewa string operations
- List methods: All Chichewa list operations  
- Dictionary methods: All Chichewa dictionary operations
- File operations: Comprehensive file I/O

## Development Features

### Command Line Interface
- `chi run --example <name>` - Execute example
- `chi run --see <name>` - View source code
- `chi run --list-examples` - List all examples
- `chi run --verbose` - Detailed execution output

### Python Integration
- Import examples as Python modules
- Execute Chi code within Python scripts
- Capture output programmatically
- Access source code as strings

### Educational Value
- Progressive complexity from basic to advanced
- Real-world application examples
- Comprehensive feature demonstration
- Cultural appropriateness with Chichewa keywords

## Example Verification

All examples have been tested and verified to work with the Chi programming language interpreter. They demonstrate proper Chi syntax and showcase the full capabilities of the language.

---

**Chi Programming Language** - Making programming accessible in Chichewa!
