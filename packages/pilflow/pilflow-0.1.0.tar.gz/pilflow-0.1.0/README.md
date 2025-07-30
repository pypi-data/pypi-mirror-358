# Pilflow

A Pillow-based image processing pipeline project with a functional programming approach for image processing operations.

## Features

- Modular and extensible image processing pipeline
- Functional programming approach with immutable operations
- Method chaining for clean and readable code
- Easy to extend with custom operations
- Comprehensive test suite

## Python Version Compatibility

This project is developed and tested with Python 3.8.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

For a quick start, see `examples/example_usage.py`.

```python
from pilflow import from_file, Operation

# Load an image
pipeline = from_file('path/to/image.jpg')

# Apply operations
result = (pipeline
         .decide_resolution()  # Analyze resolution
         .resize(width=800)    # Resize to width 800px
         .blur(radius=1.5))    # Apply blur

# Access the final image
final_image = result.img

# Access context data
print(result.context)
```

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
python run_tests.py
```

Or with coverage reporting:

```bash
python run_tests.py --html
```

See `tests/README.md` for more details on testing.