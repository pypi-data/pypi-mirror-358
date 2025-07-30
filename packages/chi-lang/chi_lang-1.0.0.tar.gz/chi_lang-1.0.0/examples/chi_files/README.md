# Chi Programming Language - Examples

Welcome to the Chi programming language examples directory! Chi is a Chichewa-inspired programming language with intuitive syntax that makes programming accessible.

## Quick Start

### Running the Examples

From the main directory, use the `chi` executable to run any example:

```bash
./chi examples/chi_language_introduction.chi
```

## Featured Examples

### 📚 **chi_language_introduction.chi**
**THE MAIN TUTORIAL** - Start here!

A comprehensive introduction that covers all current working features:
- Variable declarations and data types
- All Chichewa comparison operators
- Logical operators
- If-elif-else statements
- While and for loops
- Data structures (lists)
- Complex real-world examples

### 🔬 **working_chichewa_test.chi**
A complete test file demonstrating all working Chichewa operators and control structures.

### 🎯 **simple_elif_test.chi**
Focuses specifically on the `kapena_ngati` (elif) functionality.

### ⚡ **basic_if_test.chi**
Simple test for basic conditional statements.

## Language Reference

### Core Keywords (Currently Working)

#### Variable & Control
- `ika` - variable declaration
- `onetsa` - print statement
- `ngati` - if statement
- `kapena_ngati` - elif statement
- `sizoona` - else statement
- `chita` - block starter (alternative to `:`)

#### Data Types
- `zoona` - true
- `zabodza` - false
- `ndandanda()` - create list

#### Chichewa Comparison Operators
- `wafanana` - equals (==)
- `wasiyana` - not equal (!=)
- `wapambana` - greater than (>)
- `wachepa` - less than (<)
- `wafananitsa` - greater than or equal (>=)
- `wachepetsedwa` - less than or equal (<=)

#### Chichewa Logical Operators
- `komanso` - and
- `kapena` - or
- `osati` - not

#### Loops
- `yesani` - while loop
- `bwereza ... mu ...` - for loop

### Example Syntax

```chi
# Variables
ika name = "Jakesh"
ika age = 25
ika is_student = zoona

# Conditions with Chichewa operators
ngati age wafananitsa 18 komanso is_student chita
    onetsa("Young adult student")
kapena_ngati age wapambana 65 chita
    onetsa("Senior citizen")
sizoona chita
    onetsa("Regular adult")

# Loops
ika numbers = ndandanda(1, 2, 3, 4, 5)
bwereza num mu numbers chita
    ika squared = num * num
    onetsa("Square of", num, "is", squared)

# While loop
ika counter = 1
yesani counter wachepetsedwa 5 chita
    onetsa("Count:", counter)
    ika counter = counter + 1
```

## Testing Your Understanding

Try modifying the examples:

1. **chi_language_introduction.chi**: Change the grade thresholds in the grading examples
2. **working_chichewa_test.chi**: Add your own complex conditional logic
3. Create a new `.chi` file with your own program

## Future Features

See `chi_future_features.md` for detailed roadmap of upcoming features including:
- Function definitions (`phunzitsa`)
- Enhanced data types (`mawu`, `manambala`)
- File I/O operations (`lemba`)
- Switch/case statements (`sankhani`)
- And much more!

## Language Philosophy

Chi programming language aims to:
- 🌍 Make programming accessible in Chichewa
- 🎯 Provide intuitive, readable syntax
- 🚀 Enable rapid prototyping and learning
- 🤝 Bridge language barriers in programming education

## Contributing

Interested in contributing? Check out the roadmap in `chi_future_features.md` for priority features to implement!

---

**Happy coding in Chi!** 🔥

