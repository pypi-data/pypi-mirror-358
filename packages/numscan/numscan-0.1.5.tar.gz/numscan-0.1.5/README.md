# numscan

**numscan** is a lightweight Python package that scans large text files for interesting number patterns — such as Fibonacci numbers, prime numbers, perfect squares, and more.

It’s designed for fast processing of files with mixed content (letters, symbols, digits), supports cross-line matching, and is fully extensible.

## Features

- Count appearances of numeric patterns in large files
- Works across lines and inside mixed strings (e.g., `abc123xyz`)
- Built-in support for:
  - Fibonacci numbers
  - Prime numbers
  - Square numbers
  - Pop culture numbers (e.g., 42, 1337)
  - All integers
- Easy to extend with custom pattern counters
- Python 3.9+ compatible

## Installation

Install directly from [PyPI](https://pypi.org/project/numscan/):

```bash
pip install numscan
```

Or from GitHub (development version):

```bash
pip install git+https://github.com/ChristianRabenstein/numscan.git
```

## Basic Usage

### 1. Count Fibonacci numbers in a file

```python
from numscan import FibonacciCounter

counter = FibonacciCounter("example.txt")
print(counter.counts)
```

### 2. Count prime numbers

```python
from numscan import PrimeCounter

prime_counter = PrimeCounter("example.txt")
print(prime_counter.counts)
```

### 3. Show top matches in a formatted way

```python
def print_top_counts(counter, title, top_n=5):
    print(f"Top {top_n} matches for {title}:
")
    for number, count in sorted(counter.counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        print(f"{number}: {count}")

fib_counter = FibonacciCounter("example.txt")
print_top_counts(fib_counter, "Fibonacci Numbers")
```

### Example Output

```
Top 5 matches for Fibonacci Numbers:

1: 1582
0: 891
2: 474
3: 211
5: 102
```

## Custom Pattern Example

Create your own number matcher by subclassing `NumberCounter`:

```python
from numscan import NumberCounter

class MyLuckyNumbers(NumberCounter):
    def generate_numbers(self):
        return [7, 13, 21, 42]

lucky = MyLuckyNumbers("example.txt")
print(lucky.counts)
```

## All Available Counters

| Class              | Description                         |
|-------------------|-------------------------------------|
| `FibonacciCounter` | Matches Fibonacci numbers up to 1000 |
| `PrimeCounter`     | Matches prime numbers up to 1000     |
| `SquareCounter`    | Matches perfect square numbers       |
| `PopCultureCounter`| Matches 42, 1337, 666, and more      |
| `IntegerCounter`   | Matches all integer numbers          |

## Project Structure (Package Layout)

```
numscan/
│
├── base.py           # Base class: NumberCounter
├── fibonacci.py      # FibonacciCounter
├── prime.py          # PrimeCounter
├── squares.py        # SquareCounter
├── popculture.py     # PopCultureCounter
├── all.py            # IntegerCounter
├── __init__.py       # Unified exports
```

## 🧾 License

MIT License  
© Christian Rabenstein — [rabenstein.at](https://rabenstein.at)
