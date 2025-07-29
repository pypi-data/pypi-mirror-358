# ArithMath

A simple Python package providing basic mathematical utilities.

## Installation

```bash
pip install arithmath
```

## Usage

```python
from arithmath import add, subtract, multiply, divide

# Basic operations
result = add(5, 3)        # 8
result = subtract(10, 4)  # 6
result = multiply(3, 7)   # 21
result = divide(15, 3)    # 5.0

# You can also import the entire module
import arithmath
result = arithmath.add(2, 3)  # 5
```

## Functions

- `add(a, b)` - Add two numbers
- `subtract(a, b)` - Subtract b from a
- `multiply(a, b)` - Multiply two numbers
- `divide(a, b)` - Divide a by b (raises ValueError if b is zero)

## Development

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Make your changes
4. Test your package locally

## License

MIT License