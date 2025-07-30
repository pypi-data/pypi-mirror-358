# Try-Except-Finally (Kuyesera-Zakanika-Pomaliza) in Chichewa

## Overview
The Chichewa programming language now supports exception handling with try-except-finally statements using natural Chichewa keywords.

## Keywords
- `kuyesera` - try (meaning "to try/attempt")
- `zakanika` - except (meaning "failed/went wrong")
- `pomaliza` - finally (meaning "at the end/to finish")
- `chifukwa` - as (for exception capture, meaning "because/reason")
- `chimodzimodzi` - as (alias, meaning "the same as")

## Chichewa Exception Types
- `vuto_la_nambala` - ValueError (number problem)
- `vuto_la_mtundu` - TypeError (type problem)
- `vuto_la_ndandanda` - IndexError (list problem)
- `cholakwika_kiyi` - KeyError (wrong key)
- `vuto_la_dzina` - NameError (name problem)
- `vuto_la_kugawa` - ZeroDivisionError (division problem)
- `vuto_la_kukumbukira` - MemoryError (memory problem)
- `vuto_la_fayilo` - FileNotFoundError (file problem)
- `vuto_la_chilolezo` - PermissionError (permission problem)
- `vuto_lililonse` - Exception (any problem)

## Basic Syntax

### Simple Try-Except
```chichewa
kuyesera:
    # Code that might cause an error
    ika nambala = manambala_olekeza("invalid")
zakanika:
    # Code to handle any exception
    onetsa("An error occurred!")
```

### Try-Except with Exception Variable Capture
```chichewa
kuyesera:
    # Code that might cause an error
    ika nambala = manambala_olekeza("abc")
zakanika chifukwa error:
    # Access the exception message through 'error' variable
    onetsa("Error message:", error)
```

### Try-Except with Specific Exception Type
```chichewa
kuyesera:
    # Code that might cause an error
    ika result = manambala_olekeza("invalid_number")
zakanika vuto_la_nambala chifukwa ve:
    # Handle specific number problem (ValueError)
    onetsa("Number problem occurred:", ve)
zakanika chifukwa any_error:
    # Handle any other exception
    onetsa("Other error:", any_error)
```

### Try-Except-Finally
```chichewa
kuyesera:
    # Code that might cause an error
    ika file_content = funsani("Enter filename: ")
zakanika chifukwa error:
    # Handle exceptions
    onetsa("Error reading file:", error)
pomaliza:
    # Code that always runs (cleanup)
    onetsa("Cleanup operations completed")
```

### Try-Finally (without except)
```chichewa
kuyesera:
    # Code that might cause an error
    ika result = some_operation()
pomaliza:
    # Cleanup code that always runs
    onetsa("Cleanup completed")
```

## Multiple Except Blocks
You can have multiple except blocks to handle different types of exceptions:

```chichewa
kuyesera:
    ika x = manambala_olekeza("invalid")
    ika y = x / 0
zakanika vuto_la_nambala chifukwa ve:
    onetsa("Number problem:", ve)
zakanika vuto_la_kugawa chifukwa zde:
    onetsa("Division problem:", zde)
zakanika chifukwa general_error:
    onetsa("Unexpected error:", general_error)
pomaliza:
    onetsa("All done!")
```

## Exception Handling Flow

1. **Try Block (`kuyesera`)**: Code that might raise an exception is executed
2. **Except Blocks (`zakanika`)**: If an exception occurs, the appropriate except block is executed
   - Specific exception types are matched first
   - Generic except blocks (without type) catch any remaining exceptions
3. **Finally Block (`pomaliza`)**: Always executed, regardless of whether an exception occurred
   - Used for cleanup operations
   - Executes even if an exception is re-raised

## Notes

- At least one `zakanika` or `pomaliza` block is required after `kuyesera`
- Exception variable capture with `chifukwa` is optional
- Exception type specification is optional (defaults to catching all exceptions)
- Multiple except blocks are evaluated in order
- The finally block always executes, even if an exception is not handled

## Examples in Practice

### File Operations with Cleanup
```chichewa
kuyesera:
    ika filename = funsani("Enter filename: ")
    # Simulate file operations
    onetsa("Processing file:", filename)
zakanika chifukwa file_error:
    onetsa("File operation failed:", file_error)
pomaliza:
    onetsa("File processing complete")
```

### Mathematical Operations with Error Handling
```chichewa
kuyesera:
    ika a = manambala_olekeza("10")
    ika b = manambala_olekeza("0")
    ika result = a / b
    onetsa("Result:", result)
zakanika vuto_la_kugawa chifukwa zde:
    onetsa("Cannot divide by zero!")
zakanika vuto_la_nambala chifukwa ve:
    onetsa("Invalid number format:", ve)
pomaliza:
    onetsa("Calculation attempt completed")
```

This feature makes error handling in Chichewa code more robust and follows the natural flow of the language.

