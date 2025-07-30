# Chi Programming Language - Complete Features Guide

## Overview
Chi is a programming language that uses Chichewa keywords and syntax, making programming accessible to Chichewa speakers while maintaining modern programming capabilities.

## Core Data Types

### 1. **Strings (mawu)**
```chi
ika text = "Moni, dziko!"
ika converted = mawu(42)  # Convert to string
onetsa("Type:", mtundu(text))  # Output: mawu
```

### 2. **Numbers**
- **Float (manambala)**: Decimal numbers
- **Integer (manambala_olekeza)**: Whole numbers

```chi
ika decimal = 42.5
ika whole = manambala_olekeza(42.7)  # Converts to 42
onetsa("Float type:", mtundu(decimal))      # Output: manambala
onetsa("Integer type:", mtundu(whole))      # Output: manambala_olekeza
```

### 3. **Booleans (yankho)**
- **zoona**: True
- **zabodza**: False

```chi
ika truth = zoona
ika falsehood = zabodza
onetsa("Boolean type:", mtundu(truth))      # Output: yankho
onetsa("Value:", truth)                    # Output: zoona
```

### 4. **Null Values (palibe)**
```chi
ika nothing = palibe
onetsa("Null type:", mtundu(nothing))       # Output: palibe_mtundu
onetsa("Value:", nothing)                  # Output: palibe
```

### 5. **Lists (ndandanda)**
```chi
ika my_list = ndandanda(1, "text", zoona, palibe)
onetsa("List type:", mtundu(my_list))       # Output: ndandanda
onetsa("Contents:", my_list)               # Output: [1.0, 'text', zoona, palibe]
```

## Variable Declaration
```chi
ika variable_name = value
```

## Operators

### Arithmetic Operators
```chi
ika result = 10 + 5    # Addition
ika result = 10 - 5    # Subtraction  
ika result = 10 * 5    # Multiplication
ika result = 10 / 5    # Division
```

### Comparison Operators (Chichewa)
```chi
ika a = 5
ika b = 3

ika greater = a wapambana b      # > (greater than)
ika less = a wachepa b           # < (less than)
ika equal = a wafanana b         # == (equal to)
ika not_equal = a wasiyana b     # != (not equal to)
ika gte = a wafananitsa b        # >= (greater than or equal)
ika lte = a wachepetsedwa b      # <= (less than or equal)
```

### Logical Operators (Chichewa)
```chi
ika result1 = zoona komanso zabodza    # AND
ika result2 = zoona kapena zabodza     # OR
ika result3 = osati zoona              # NOT
```

## Control Structures

### If-Else Statements
```chi
ngati condition:
    # then block
sizoona:
    # else block
```

### If-Elif-Else
```chi
ngati age wachepa 13:
    onetsa("Child")
kapena_ngati age wachepa 20:
    onetsa("Teenager") 
sizoona:
    onetsa("Adult")
```

### While Loops
```chi
ika count = 0
yesani count wachepa 5:
    onetsa("Count:", count)
    ika count = count + 1
```

### For Loops
```chi
ika numbers = ndandanda(1, 2, 3, 4, 5)
bwereza num mu numbers:
    onetsa("Number:", num)
```

### Loop Control
```chi
bwereza item mu my_list:
    ngati item == palibe:
        pitilizani    # continue
    ngati item wapambana 10:
        leka          # break
    onetsa(item)
```

## Built-in Functions

### 1. **Output (onetsa)**
```chi
onetsa("Hello")
onetsa("Multiple", "values", 42)
```

### 2. **Input (funsani)**
```chi
ika name = funsani("Enter your name: ")
```

### 3. **Type Checking (mtundu)**
```chi
onetsa(mtundu("text"))      # mawu
onetsa(mtundu(42.5))        # manambala
onetsa(mtundu(zoona))       # yankho
onetsa(mtundu(palibe))      # palibe_mtundu
onetsa(mtundu(my_list))     # ndandanda
```

### 4. **Length/Size (kukula)**
```chi
ika my_list = ndandanda(1, 2, 3)
onetsa("Length:", kukula(my_list))    # Output: 3
onetsa("String length:", kukula("hello"))  # Output: 5
```

### 5. **Advanced Mathematical Functions**
```chi
# Power and modulo
onetsa(mphamvu(2, 8))        # Power: 256
onetsa(chotsalira(17, 5))    # Modulo: 2

# Square root and absolute value
onetsa(muzu(25))             # Square root: 5.0
onetsa(chopanda(-10))        # Absolute value: 10.0

# Floor, ceiling, and rounding
onetsa(pansi(4.8))           # Floor: 4
onetsa(pamwamba(4.2))        # Ceiling: 5
onetsa(zungulira(3.14159, 2))  # Round: 3.14

# Sum and average
onetsa(phatikiza(1, 2, 3, 4, 5))  # Sum: 15
onetsa(pakatikati(10, 20, 30))    # Average: 20

# Maximum and minimum
onetsa(chachikulu(5, 12, 8)) # Maximum: 12
onetsa(chachingono(5, 12, 8)) # Minimum: 5
```

### 6. **Type Conversion**
```chi
ika str_result = mawu(42)              # Convert to string
ika float_result = manambala("42.5")   # Convert to float
ika int_result = manambala_olekeza(42.7)  # Convert to integer
```

## List Operations

### Creating Lists
```chi
ika my_list = ndandanda(1, 2, 3, "text", zoona)
```

### List Methods (Chichewa)
```chi
# Add to end
my_list.onjezera("new_item")

# Insert at position
my_list.lowetsa(0, "first_item")

# Remove item
my_list.chotsa("text")

# Remove and return item at position
ika removed = my_list.tulutsa(0)

# Find index of item
ika position = my_list.funafuna("new_item")

# Count occurrences
ika count = my_list.werengera("item")
```

### List Indexing
```chi
ika first = my_list[0]
ika last = my_list[kukula(my_list) - 1]
```

## Null Handling

### Null Comparisons
```chi
ika value = palibe

ngati value == palibe:
    onetsa("Value is null")

ngati value != palibe:
    onetsa("Value has content")
```

### Null in Data Structures
```chi
ika mixed = ndandanda("apple", palibe, "banana", palibe)
bwereza item mu mixed:
    ngati item == palibe:
        onetsa("Found null value")
    sizoona:
        onetsa("Item:", item)
```

## Type System

### Chichewa Type Names
- **mawu**: String
- **manambala**: Float number
- **manambala_olekeza**: Integer
- **yankho**: Boolean
- **palibe_mtundu**: Null type
- **ndandanda**: List
- **chinthu**: Generic object

### Type Checking Examples
```chi
ika data = ndandanda("text", 42, zoona, palibe)

bwereza item mu data:
    ika item_type = mtundu(item)
    onetsa("Item:", item, "Type:", item_type)
```

## Error Handling

### Type Conversion Errors
```chi
# This will show an error message
ika invalid = manambala("not_a_number")
```

### Index Errors
```chi
ika my_list = ndandanda(1, 2, 3)
# This will show an error for invalid index
ika item = my_list[10]
```

## Best Practices

### 1. **Null Checking**
```chi
ika user_input = funsani("Enter something: ")
ngati user_input == palibe:
    ika user_input = "default_value"
```

### 2. **Type Validation**
```chi
ngati mtundu(value) == "manambala":
    onetsa("It's a number:", value)
```

### 3. **Safe List Operations**
```chi
ngati kukula(my_list) wapambana 0:
    ika first = my_list[0]
    onetsa("First item:", first)
```

## Complete Example Program

```chi
# Chi Language Demonstration Program

onetsa("=== Chi Programming Language Demo ===")

# Variables and types
ika name = "Jakesh"
ika age = 25
ika is_student = zoona
ika score = palibe

onetsa("Name:", name, "Type:", mtundu(name))
onetsa("Age:", age, "Type:", mtundu(age))
onetsa("Student:", is_student, "Type:", mtundu(is_student))
onetsa("Score:", score, "Type:", mtundu(score))

# Lists and operations
ika subjects = ndandanda("Math", "Science", "English")
onetsa("Subjects:", subjects)

subjects.onjezera("History")
onetsa("After adding History:", subjects)

# Conditional logic
ngati age wafananitsa 18:
    onetsa("Adult")
sizoona:
    onetsa("Minor")

# Loops and null handling
ika grades = ndandanda(85, palibe, 92, 78, palibe)
ika total = 0
ika count = 0

bwereza grade mu grades:
    ngati grade != palibe:
        ika total = total + grade
        ika count = count + 1

ngati count wapambana 0:
    ika average = total / count
    onetsa("Average grade:", average)

onetsa("=== Demo Complete ===")
```

---

*Chi Programming Language - Bridging technology and culture through localized programming*

