# Algorithm Visualization

This project is a visualization program for algorithms represented by block schemas. It parses Microsoft Visio `.vsdx` files to extract blocks and connections, which can then be used to visualize the algorithm's structure.

## Features

- Parse `.vsdx` files to extract blocks and connections.
- Handle missing or malformed `.vsdx` files gracefully.
- Support for multiple pages in Visio diagrams.
- Visualize the extracted block schema (future feature).

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Parsing a `.vsdx` File

Use the `VSDXParser` class to parse a `.vsdx` file:

```python
from alg_vis.libs.schema_parser import VSDXParser

parser = VSDXParser("path/to/file.vsdx")
schema = parser.parse()
print(schema)
```

### Test Script

Run the test script to parse a sample `.vsdx` file:

```bash
python alg_vis/test/test_parser.py
```

## File Structure

- `alg_vis/libs/schema_parser.py`: Contains the `VSDXParser` class for parsing `.vsdx` files.
- `alg_vis/test/parser.py`: Test script for the `VSDXParser` class.
- `requirements.txt`: Lists the required Python dependencies.

## Requirements

- Python 3.7+
- `lxml`

## Future Work

- Add a visualization module to render the parsed block schema as a graphical representation.
- Support additional diagram formats.
