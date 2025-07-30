# `reduce-ex`

n-ary reduce operator with support for prefix/suffix elements. Intermediate results are yielded as well. Like `functools.reduce` but more powerful.

## Key Features

- **N-ary operation support**: Works with functions of any arity (n ≥ 2)
- **Intermediate results yielded**: Not just the last result is returned
- **Flexible input**: Supports prefix/suffix elements for initialization/termination
- **Memory efficient**: Uses bounded deque for argument handling
- **Zero Dependencies**: Works with stock Python 2+

## Usage

### Basic Usage

For binary operations (n=2), `reduce_ex` maintains identical left-associative evaluation order as `functools.reduce`, while yielding intermediate results:

```python
from reduce_ex import reduce_ex

for partial_sum in reduce_ex(lambda a, b: a + b, range(1, 5)):
    print(partial_sum)
# Computation steps:
# 1+2 = 3
# 3+3 = 6
# 6+4 = 10
# Yields: 3, 6, 10
```

### N-ary Operation (n=3)

For n-ary operations, the evaluation proceeds via left-associative sliding windows:

```python
from reduce_ex import reduce_ex

# Polynomial recurrence: a * b + c
for partial_result in reduce_ex(lambda a, b, c: a * b + c, [2, 3, 4, 5, 6], n=3):
    print(partial_result)
# Computation steps:
# 2 * 3 + 4 = 10
# 10 * 5 + 6 = 56
# Yields: 10, 56
```

### With `prefix`

```python
from math import tanh

from reduce_ex import reduce_ex

W_h = 0.5
W_x = 0.5
B = 0.5


# Simulate an RNN cell
def rnn_cell(h_prev, x):
    global W_h, W_x, B
    
    return tanh(W_h * h_prev + W_x * x + B)


h_0 = 0.0

for i, h_i in enumerate(
    reduce_ex(
        rnn_cell,
        [0.1, 0.2, 0.3],
        prefix=[h_0]
    ),
    start=1
):
    print(f"Hidden state {i}: {h_i}")
```

### With `prefix` and `suffix`

```python
from reduce_ex import reduce_ex

for partial_sum in reduce_ex(lambda a, b: a + b, range(5), prefix=(1, 2), suffix=(10,)):
    print(partial_sum)
# Computation steps:
# 1 + 2 = 3
# 3 + 0 = 3
# 3 + 1 = 4
# 4 + 2 = 6
# 6 + 3 = 9
# 9 + 4 = 13
# 13 + 10 = 23
# Yields: 3, 3, 4, 6, 9, 13, 23
```

## How It Works

The reducer maintains the following invariants:

- Consumes `n` elements.
- Calls function, yields result, uses the previous result as first argument, and consumes `(n-1)` more elements.
- Calls function, yields result, uses the previous result as first argument, and consumes `(n-1)` more elements.
- ...

## API Reference

### `reduce_ex(function, iterable, n=2, prefix=(), suffix=())`

- `function`: Callable of arity n
- `iterable`: Input elements
- `n`: Operation arity (must be ≥ 2)
- `prefix`: Elements prepended to input
- `suffix`: Elements appended to input

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).