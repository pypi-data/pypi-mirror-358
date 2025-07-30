# spellbind

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/FancyNeuron/spellbind/actions/workflows/python-package.yml/badge.svg)](https://github.com/FancyNeuron/spellbind/actions/workflows/python-package.yml)

> Reactive programming for Python with reactive variables and events.

spellbind is a reactive programming library that lets you create Variables that automatically update when their dependencies change, plus an event system for notifying observers.

## Installation

```bash
pip install spellbind
```

## Quick Start

```python
from spellbind.int_values import IntVariable
from spellbind.str_values import StrVariable

# Create reactive variables
name = StrVariable("Alice")
age = IntVariable(25)

# Create computed values that automatically update
greeting = name + " is " + age.to_str() + " years old"

print(greeting)  # "Alice is 25 years old"

# Update source values - computed values update automatically!
name.value = "Bob"
age.value = 30

print(greeting)  # "Bob is 30 years old"
```

## Core Concepts

### Values, Variables and Events

The foundation of spellbind consists of three key components:

**Values** are read-only reactive data that can be observed for changes. **Variables** are mutable Values that can be changed and bound to other Values. **Events** provide a way to notify observers when something happens.

```python
from spellbind.values import Constant
from spellbind.int_values import IntVariable
from spellbind.event import Event

# Variables can be changed
counter = IntVariable(0)
counter.value = 10

# Constants cannot be changed
pi = Constant(3.14159)

# Events notify observers
button_clicked = Event()
button_clicked.observe(lambda: print("Clicked!"))
button_clicked()  # Prints: "Clicked!"
```

### Reactive Bindings

Variables can be **bound** to other Values, making them automatically update:

```python
from spellbind.int_values import IntVariable

# Create computed values
base = IntVariable(10)
multiplier = IntVariable(3)
result = base * multiplier

# Bind variables to computed values
my_variable = IntVariable(0)
my_variable.bind_to(result)

print(my_variable)  # 30

# Updates propagate automatically
base.value = 20
print(my_variable)  # 60

# Unbind to break connections
my_variable.unbind()
```

## Advanced Features

### Weak vs Strong Binding

Control memory management with binding strength:

```python
from spellbind.str_values import StrVariable

source = StrVariable("hello")
target = StrVariable("")

# Strong binding (default) - keeps source alive
target.bind_to(source, bind_weakly=False)

# Weak binding - allows source to be garbage collected
target.bind_to(source, bind_weakly=True)
```

### Circular Dependency Detection

spellbind automatically prevents circular dependencies:

```python
from spellbind.int_values import IntVariable

a = IntVariable(1)
b = IntVariable(2)

a.bind_to(b)
# b.bind_to(a)  # This would raise RecursionError
```

### Observing Changes

React to value changes with observers:

```python
from spellbind.int_values import IntVariable


def on_value_change(new_value):
    print(f"Value changed to: {new_value}")


my_var = IntVariable(42)
my_var.observe(on_value_change)

my_var.value = 100  # Prints: "Value changed to: 100"
```

## Event System

spellbind includes an event system for notifying observers when things happen.

### Basic Events

```python
from spellbind.event import Event

# Create an event
button_clicked = Event()


# Add observers
def handle_click():
    print("Button was clicked!")


button_clicked.observe(handle_click)

# Trigger the event
button_clicked()  # Prints: "Button was clicked!"
```

### Value Events

Events that pass data to observers:

```python
from spellbind.event import ValueEvent

user_logged_in = ValueEvent[str]()


def welcome_user(username: str):
    print(f"Welcome, {username}!")


user_logged_in.observe(welcome_user)
user_logged_in("Alice")  # Prints: "Welcome, Alice!"
```

### Multi-Parameter Events

Events with multiple parameters:

```python
from spellbind.event import BiEvent, TriEvent

# Two parameters
position_changed = BiEvent[int, int]()
position_changed.observe(lambda x, y: print(f"Position: ({x}, {y})"))
position_changed(10, 20)  # Prints: "Position: (10, 20)"

# Three parameters
rgb_changed = TriEvent[int, int, int]()
rgb_changed.observe(lambda r, g, b: print(f"Color: rgb({r}, {g}, {b})"))
rgb_changed(255, 128, 0)  # Prints: "Color: rgb(255, 128, 0)"
```

### Weak Observation

Prevent memory leaks with weak observers:

```python
from spellbind.event import Event

event = Event()


def temporary_handler():
    print("Handling event")


# Weak observation - handler can be garbage collected
event.weak_observe(temporary_handler)
```

## Example Application

Here's a practical example showing how to create automatically positioned windows:

```python
from spellbind.int_values import IntVariable


class Window:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = IntVariable(x)
        self.y = IntVariable(y)
        self.width = IntVariable(width)
        self.height = IntVariable(height)

    def __repr__(self):
        return f"Window(x={self.x.value}, y={self.y.value}, width={self.width.value}, height={self.height.value})"


# Create two windows
main_window = Window(100, 50, 800, 600)
sidebar_window = Window(0, 0, 200, 400)

# Automatically position sidebar to the right of main window
margin = IntVariable(10)
sidebar_window.x.bind_to(main_window.x + main_window.width + margin)
sidebar_window.y.bind_to(main_window.y)

print(main_window)  # Window(x=100, y=50, width=800, height=600)
print(sidebar_window)  # Window(x=910, y=50, width=200, height=400)

# Moving the main window automatically repositions the sidebar
main_window.x.value = 200
main_window.y.value = 100

print(main_window)  # Window(x=200, y=100, width=800, height=600)
print(sidebar_window)  # Window(x=1010, y=100, width=200, height=400)

# Changing margin updates sidebar position
margin.value = 20
print(sidebar_window)  # Window(x=1020, y=100, width=200, height=400)
```

## API Reference

### Core Classes

- **`Value[T]`** - Type for all reactive values, useful for typing function parameters
- **`Variable[T]`** - Type for mutable values, useful for typing function parameters  
- **`Constant[T]`** - Immutable value

### Type-Specific Classes

- **`IntValue`**, **`IntVariable`** - Integer values with arithmetic operations
- **`FloatValue`**, **`FloatVariable`** - Float values with arithmetic operations  
- **`StrValue`**, **`StrVariable`** - String values with concatenation
- **`BoolValue`** - Boolean values with logical operations

### Event Classes

- **`Event`** - Basic event with no parameters
- **`ValueEvent[T]`** - Event that passes one value
- **`BiEvent[S, T]`** - Event that passes two values
- **`TriEvent[S, T, U]`** - Event that passes three values

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src
```

### Linting

```bash
flake8 .
```

---

Author: Georg Plaz