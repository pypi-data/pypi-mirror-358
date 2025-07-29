# pyresult

[![PyPI version](https://badge.fury.io/py/py-pyresult.svg)](https://badge.fury.io/py/py-pyresult)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, type-safe `Result` type for Python, inspired by Rust.

`pyresult` provides a robust and ergonomic way to handle operations that can either succeed (`Ok`) or fail (`Err`), eliminating the ambiguity of returning `None` or raising exceptions for expected errors.

This library is built with two core principles:
- **Maximum Performance**: The core logic is compiled to a native C extension using **Mypyc**, removing Python's interpreter overhead and delivering C-level speed.
- **Absolute Type Safety**: It is designed to pass `mypy --strict` checks, ensuring that your error-handling logic is sound and free of type-related bugs.

## Core Philosophy

In many functions, errors are an expected possibility. Traditional Python error handling often relies on returning `None` (which can be ambiguous) or raising exceptions (which can be costly and verbose for control flow). `pyresult` offers a better way: a function returns a `Result` object, which is either an `Ok` containing a success value or an `Err` containing an error value. This makes the possibility of an error explicit in the function's type signature, forcing the caller to handle it gracefully.

## Key Features

- **Blazing Fast**: Compiled with Mypyc for performance that rivals native C code.
- **Type-Safe by Design**: Fully annotated and validated with `mypy --strict`.
- **Zero Dependencies**: Relies only on the Python standard library.
- **Ergonomic API**: Provides a fluent, chainable interface for elegant error handling.
- **Drop-in & Easy to Use**: A simple and intuitive API that is easy to adopt in any project.

## Installation

You can install `pyresult` directly from PyPI:
```bash
pip install py-pyresult
```

Or, install it directly from the GitHub repository:
```bash
pip install git+https://github.com/imsf04/py-pyresult.git
```

## Quick Start

Here is a simple example of how to use `pyresult`:

```python
from pyresult.result import Ok, Err, Result

def divide(a: int, b: int) -> Result[float, str]:
    """
    A function that returns a Result: Ok(float) on success, or Err(str) on failure.
    """
    if b == 0:
        return Err("Cannot divide by zero")
    return Ok(a / b)

# --- Example 1: Successful division ---
res1 = divide(10, 2)

if res1.is_ok:
    # The operation was a success, we can safely unwrap the value.
    value = res1.unwrap()
    print(f"Success! Result is {value}")  # Output: Success! Result is 5.0

# --- Example 2: Failed division ---
res2 = divide(10, 0)

if res2.is_err:
    # The operation failed. We can get the error.
    error_message = res2.unwrap_err()
    print(f"Error: {error_message}")  # Output: Error: Cannot divide by zero

# --- Example 3: Using the chainable API ---
result = divide(20, 2)
(result.map(lambda x: x - 5)         # Ok(10.0) -> Ok(5.0)
       .and_then(lambda x: Ok(x * 2)) # Ok(5.0) -> Ok(10.0)
       .map_err(lambda e: f"Error: {e}")
)
print(result.unwrap_or(0.0)) # Output: 10.0
```

## API Reference

### Checking for Success or Failure
- `res.is_ok` (property): Returns `True` if the result is `Ok`.
- `res.is_err` (property): Returns `True` if the result is `Err`.

### Extracting Values
- `res.ok() -> Optional[T]`: Returns the value if the result is `Ok`, otherwise `None`.
- `res.err() -> Optional[E]`: Returns the error if the result is `Err`, otherwise `None`.
- `res.unwrap() -> T`: Returns the value if `Ok`, but **panics** (raises an `Exception`) if `Err`. Only use when you are certain of success.
- `res.unwrap_err() -> E`: Returns the error if `Err`, but **panics** if `Ok`.
- `res.unwrap_or(default: T) -> T`: Returns the value if `Ok`, or `default` if `Err`.
- `res.unwrap_or_else(op: Callable[[E], T]) -> T`: Returns the value if `Ok`, or computes it from a function if `Err`.

### Transforming Values
- `res.map(op: Callable[[T], U]) -> Result[U, E]`: Maps a `Result[T, E]` to `Result[U, E]` by applying a function to a contained `Ok` value, leaving an `Err` value untouched.
- `res.map_err(op: Callable[[E], F]) -> Result[T, F]`: Maps a `Result[T, E]` to `Result[T, F]` by applying a function to a contained `Err` value, leaving an `Ok` value untouched.

### Chaining Operations
- `res.and_then(op: Callable[[T], Result[U, E]]) -> Result[U, E]`: Calls `op` if the result is `Ok`, otherwise returns the `Err` value of `res`. This is useful for chaining operations that might fail.
- `res.or_else(op: Callable[[E], Result[T, F]]) -> Result[T, F]`: Calls `op` if the result is `Err`, otherwise returns the `Ok` value of `res`. This is useful for handling an error by trying an alternative operation.

### Checking Contents
- `res.contains(value: T) -> bool`: Returns `True` if the result is an `Ok` value containing the given value.
- `res.contains_err(error_value: E) -> bool`: Returns `True` if the result is an `Err` value containing the given error.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

