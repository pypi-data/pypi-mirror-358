# Text2File

[![PyPI version](https://badge.fury.io/py/text2file.svg)](https://badge.fury.io/py/text2file)
[![Python Version](https://img.shields.io/pypi/pyversions/text2file.svg)](https://pypi.org/project/text2file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/veridock/text2file/actions/workflows/tests.yml/badge.svg)](https://github.com/veridock/text2file/actions)
[![Codecov](https://codecov.io/gh/veridock/text2file/branch/main/graph/badge.svg)](https://codecov.io/gh/veridock/text2file)

A powerful utility to generate test files in various formats from text content. Perfect for testing, development, and automation tasks.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Using pip (recommended)](#using-pip-recommended)
  - [From source](#from-source)
- [Usage](#usage)
  - [Basic Syntax](#basic-syntax)
  - [Available Commands](#available-commands)
  - [Examples](#examples)
- [File Format Examples](#file-format-examples)
  - [Text Files](#text-files)
  - [Code Files](#code-files)
  - [Documents](#documents)
  - [Spreadsheets](#spreadsheets)
  - [Images](#images)
  - [Archives](#archives)
- [API Reference](#api-reference)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🚀 Generate files in multiple formats with a single command
- 📄 Support for various file types:
  - **Text**: `.txt`, `.md`, `.html`, `.css`, `.js`, `.py`, `.json`, `.csv`
  - **Documents**: `.pdf`, `.docx`, `.odt`
  - **Spreadsheets**: `.xlsx` (Excel)
  - **Images**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.svg`
  - **Videos**: `.mp4`, `.avi`, `.mov` (basic support)
  - **Archives**: `.zip`, `.tar`, `.tar.gz`, `.tgz`
- ✅ File validation to ensure generated files are not corrupted
- 🔄 Clean up invalid files with a single command
- 📂 Customizable output directory and filename prefix
- 🔍 Recursive directory scanning for validation and cleanup
- 🛠️ Extensible architecture for adding new file formats
- 🧪 Built-in testing and validation

## Installation

### Using pip (recommended)

```bash
pip install text2file
```

### From source

1. Clone the repository:
   ```bash
   git clone https://github.com/veridock/text2file.git
   cd text2file
   ```

2. Install with Poetry (recommended):
   ```bash
   poetry install
   ```

   Or with pip:
   ```bash
   pip install .
   ```

## Usage

### Basic Syntax

```bash
text2file [COMMAND] [OPTIONS]
```

### Available Commands

- `generate` - Generate files in various formats
- `generate-set` - Generate a set of images from a JSON configuration
- `validate` - Validate generated files
- `cleanup` - Clean up invalid files
- `--version` - Show version and exit
- `--help` - Show help message and exit

### Examples

#### Generate a text file
```bash
# Short syntax
text2file "Hello, World!" txt

# Long syntax
text2file generate --content "Hello, World!" --extension txt

# Specify output directory and filename prefix
text2file generate --content "Hello, World!" --extension txt --output-dir ./output --prefix myfile
```

#### List all supported file formats
```bash
text2file list
```

#### Generate a video file
```bash
# Generate a basic video with text overlay
text2file generate --content "Sample video content" --extension mp4

# Generate a video with custom duration and resolution
text2file generate --content "Custom video" --extension mp4 --duration 10 --resolution 1280x720
```

This will create a video file with the specified content as text overlay. Video generation supports:
- Custom duration (in seconds)
- Custom resolution (e.g., 1920x1080)
- Background and text color customization

### Advanced Image Generation

#### Generate a set of images from a JSON configuration

Create a JSON file (e.g., `icons.json`) with the following format:

```json
{
  "icons": [
    {"src": "icon-16x16.png", "sizes": "16x16"},
    {"src": "icon-32x32.png", "sizes": "32x32"},
    {"src": "icon-64x64.png", "sizes": "64x64"}
  ]
}
```

Then run:

```bash
# Generate placeholder images with default text
text2file generate-set icons.json

# Use a base image and resize it
text2file generate-set icons.json --base-image source-icon.png

# Customize the placeholder appearance
text2file generate-set icons.json --text "My App" --background-color "#f0f0f0" --text-color "#333333"

# Generate SVG images with custom content
text2file generate --content "<svg><circle cx='50' cy='50' r='40' fill='blue'/></svg>" --extension svg
```

Options:
- `-o, --output-dir`: Output directory (default: current directory)
- `-b, --base-image`: Base image to use for resizing (optional)
- `--bg, --background-color`: Background color for placeholders (default: "#ffffff")
- `-t, --text`: Text to render on placeholder images
- `--fg, --text-color`: Text color for placeholders (default: "#000000")

Create a JSON file (e.g., `icons.json`) with the following format:

```json
{
  "icons": [
    {"src": "icon-16x16.png", "sizes": "16x16"},
    {"src": "icon-32x32.png", "sizes": "32x32"},
    {"src": "icon-64x64.png", "sizes": "64x64"}
  ]
}
```

Then run:

```bash
# Generate placeholder images with default text
text2file generate-set icons.json

# Use a base image and resize it
text2file generate-set icons.json --base-image source-icon.png

# Customize the placeholder appearance
text2file generate-set icons.json --text "My App" --background-color "#f0f0f0" --text-color "#333333"
```

Options:
- `-o, --output-dir`: Output directory (default: current directory)
- `-b, --base-image`: Base image to use for resizing (optional)
- `--bg, --background-color`: Background color for placeholders (default: "#ffffff")
- `-t, --text`: Text to render on placeholder images
- `--fg, --text-color`: Text color for placeholders (default: "#000000")

#### Generate an Excel (.xlsx) file

Generate Excel spreadsheets with support for:
- Multiple worksheets
- Auto-adjusted column widths
- Custom sheet names
- CSV-like data input

```bash
# Basic usage with CSV-like content
content="Name,Age,City\nJohn,30,New York\nAlice,25,London"
text2file generate --content "$content" --extension xlsx

# Custom sheet name
text2file generate --content "$content" --extension xlsx --sheet-name "Users"

# Disable auto-adjust column widths
text2file generate --content "$content" --extension xlsx --no-auto-adjust
```

**Options:**
- `--sheet-name`: Custom worksheet name (default: "Sheet1")
- `--no-auto-adjust`: Disable auto-adjustment of column widths (enabled by default)

The input content should be in CSV format where:
- Rows are separated by newlines (`\n`)
- Cells within a row are separated by commas (`,`)
- The first row is treated as headers if present

Example with multiple data types:
```bash
content="Name,Age,Salary,HireDate\nJohn Doe,35,75000,2020-05-15\nJane Smith,28,85000,2021-03-22"
text2file generate --content "$content" --extension xlsx --sheet-name "Employees"
```

This will create an Excel file with properly formatted cells, including:
- Text alignment
- Number formatting
- Date recognition
- Auto-adjusted column widths

For more complex spreadsheets, you can generate the XLSX file programmatically using the Python API:

```python
from text2file import generate_file

# Generate with custom options
generate_file(
    content="Product,Price,Stock\nLaptop,999,15\nMouse,25,100",
    extension="xlsx",
    output_dir="./reports",
    prefix="inventory",
    sheet_name="Products",
    auto_adjust=True
)
```
# Basic Excel file from CSV-like content
content="Name,Age,City\nJohn,30,New York\nAlice,25,London"
text2file generate --content "$content" --extension xlsx

# With custom sheet name
text2file generate --content "$content" --extension xlsx --sheet_name "Employees"

# Disable auto-adjusting column widths
text2file generate --content "$content" --extension xlsx --no-auto-adjust
```

### Generate multiple files with different formats
```bash
text2file generate --content "Sample content" --extension txt,md,html,xlsx --output-dir ./output
```

#### Validate generated files
```bash
text2file validate --path ./output --recursive --verbose
```

#### Clean up invalid files
```bash
text2file cleanup --path ./output --recursive --dry-run
```

## File Format Examples

### Text Files

#### Plain Text (.txt)
```bash
text2file generate --content "This is a plain text file" --extension txt
```

#### Markdown (.md)
```bash
content="# Sample Markdown\n\n- Item 1\n- Item 2\n- Item 3"
text2file generate --content "$content" --extension md
```

### Code Files

#### Python (.py)
```bash
content="def hello_world():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    hello_world()"
text2file generate --content "$content" --extension py
```

#### JavaScript (.js)
```bash
content="function helloWorld() {\n  console.log('Hello, World!');\n}\n\nhelloWorld();"
text2file generate --content "$content" --extension js
```

### Documents

#### PDF (.pdf)
```bash
text2file generate --content "This is a sample PDF document" --extension pdf
```

#### Word Document (.docx)
```bash
text2file generate --content "This is a sample Word document" --extension docx
```

### Spreadsheets

#### Excel (.xlsx)
```bash
content="Name,Age,City\nJohn,30,New York\nAlice,25,London"
text2file generate --content "$content" --extension xlsx
```

### Image Sets

Generate multiple images from a JSON configuration file. This is useful for creating icon sets or multiple resolutions of the same image.

#### JSON Configuration Format

Create a file (e.g., `icons.json`) with the following structure:

```json
{
  "icons": [
    {
      "src": "icon-16x16.png",
      "sizes": "16x16"
    },
    {
      "src": "icon-32x32.png",
      "sizes": "32x32"
    },
    {
      "src": "subdir/icon-64x64.png",
      "sizes": "64x64"
    }
  ]
}
```

Each entry in the `icons` array should have:
- `src`: Output file path (relative to output directory)
- `sizes`: Dimensions in format "WIDTHxHEIGHT" (e.g., "32x32")

#### Usage Examples

```bash
# Generate placeholder images with default text
text2file generate-set icons.json

# Use a base image and resize it
text2file generate-set icons.json --base-image source-icon.png

# Customize the placeholder appearance
text2file generate-set icons.json --text "My App" --background-color "#f0f0f0" --text-color "#333333"

# Specify output directory
text2file generate-set icons.json --output-dir ./output
```

#### Options
- `-o, --output-dir`: Output directory (default: current directory)
- `-b, --base-image`: Base image to use for resizing (optional)
- `--bg, --background-color`: Background color for placeholders (default: "#ffffff")
- `-t, --text`: Text to render on placeholder images
- `--fg, --text-color`: Text color for placeholders (default: "#000000")

### Single Images

#### JPEG (.jpg, .jpeg)
```bash
text2file generate --content "Sample image content" --extension jpg --width 800 --height 600
```

#### PNG (.png)
```bash
text2file generate --content "Sample image content" --extension png --width 800 --height 600
```

#### SVG Image (.svg)
```bash
text2file generate --content "Sample SVG" --extension svg

# With custom dimensions (width x height)
text2file generate --content "Custom Size" --extension svg --width 400 --height 200
```

### Archives

#### ZIP (.zip)
```bash
text2file generate --content "Sample content for archive" --extension zip
```

#### TAR.GZ (.tar.gz)
```bash
text2file generate --content "Sample content for tar.gz archive" --extension tar.gz
```

## API Reference

### text2file.generate_file(content: str, extension: str, output_dir: str = ".", filename: Optional[str] = None) -> str
Generate a file with the given content and extension.

#### Parameters
- `content`: The content to write to the file
- `extension`: The file extension (without dot)
- `output_dir`: Output directory (default: current directory)
- `filename`: Optional custom filename (without extension)

#### Returns
- Path to the generated file

### text2file.validate_file(filepath: str) -> bool
Validate if a file is not corrupted.

#### Parameters
- `filepath`: Path to the file to validate

#### Returns
- `True` if file is valid, `False` otherwise

### text2file.cleanup_invalid_files(directory: str, recursive: bool = False, dry_run: bool = False) -> List[str]
Remove invalid files from a directory.

#### Parameters
- `directory`: Directory to clean up
- `recursive`: Whether to scan subdirectories
- `dry_run`: If True, only show what would be deleted

#### Returns
- List of removed files

## Development

### Prerequisites
- Python 3.8+
- [Poetry](https://python-poetry.org/)

### Optional Dependencies
- `Pillow` for image generation
- `openpyxl` for Excel file generation
- `python-docx` for Word document generation
- `PyPDF2` for PDF file generation

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/veridock/text2file.git
   cd text2file
   ```

2. Install development dependencies:
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install project with all optional dependencies
   make install-dev
   ```

3. Run tests:
   ```bash
   make test
   ```

4. Run linters and formatters:
   ```bash
   make lint       # Run all linters
   make format     # Auto-format code
   make typecheck  # Run static type checking
   ```

5. Install the package in development mode:
   ```bash
   pip install -e .
   ```

6. Run the CLI directly:
   ```bash
   python -m text2file --help
   ```

### Linting and Formatting

```bash
# Run linter
ruff check .

# Format code
black .

# Check types
mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Adding New File Formats

To add support for a new file format:

1. Create a new generator function in the appropriate module under `src/text2file/generators/`
2. Add a validator in `src/text2file/validators/`
3. Register the generator using the `@register_generator` decorator
4. Add tests in the `tests/` directory
5. Update the documentation

## Changelog

### 0.2.0 (Unreleased)
- Added lazy loading of generators for better performance
- Added support for video file generation (`.mp4`, `.avi`, `.mov`)
- Added `text2file list` command to show supported formats
- Improved error messages for missing dependencies
- Updated documentation and examples

See [CHANGELOG.md](CHANGELOG.md) for the full changelog.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

Created with ❤️ by [Veridock](https://veridock.com)

## Commands

#### Generate Files

```bash
text2file generate "Your text content" [EXTENSIONS...] [OPTIONS]
```

**Options:**
- `-o, --output-dir PATH`: Output directory (default: current directory)
- `-p, --prefix TEXT`: Filename prefix (default: "generated")
- `--help`: Show help message and exit

**Examples:**

1. Generate a simple text file:
   ```bash
   text2file generate "This is a test file" txt
   ```

2. Generate multiple file formats at once:
   ```bash
   text2file generate "Sample content" txt md pdf jpg
   ```

3. Custom output directory and prefix:
   ```bash
   text2file generate "Test content" -o ./output -p custom_ txt pdf
   ```

#### Validate Files

```bash
text2file validate PATH [OPTIONS]
```

**Options:**
- `-r, --recursive`: Recursively validate files in subdirectories
- `-v, --verbose`: Show detailed validation results
- `--json`: Output results in JSON format
- `--help`: Show help message and exit

**Examples:**

1. Validate a single file:
   ```bash
   text2file validate document.pdf
   ```

2. Validate all files in a directory recursively:
   ```bash
   text2file validate ./test_files -r
   ```

3. Get detailed validation output in JSON:
   ```bash
   text2file validate ./test_files --json
   ```

#### Clean Up Invalid Files

```bash
text2file cleanup PATH [OPTIONS]
```

**Options:**
- `-r, --recursive`: Recursively clean up files in subdirectories
- `--dry-run`: Show what would be deleted without actually deleting
- `-v, --verbose`: Show detailed information
- `--help`: Show help message and exit

**Examples:**

1. Clean up invalid files in a directory:
   ```bash
   text2file cleanup ./test_files
   ```

2. Preview what would be deleted (dry run):
   ```bash
   text2file cleanup ./test_files --dry-run -v
   ```

## File Format Examples

### Text Files (`.txt`, `.md`)
```bash
text2file generate "# Markdown Title\n\nThis is a **markdown** file with *formatting*.\n\n- Item 1\n- Item 2\n- Item 3" md
```

### Code Files (`.py`, `.js`, `.html`)
```bash
text2file generate "def hello_world():\n    print('Hello, World!')" py
```

### Images (`.jpg`, `.png`)
```bash
text2file generate "Sample text to be converted to image" jpg png
```

### Documents (`.pdf`, `.docx`)
```bash
text2file generate "Formal Document\n\nThis is a sample document with multiple paragraphs. The text will be automatically wrapped to fit the output format. Great for creating test data!" pdf docx
```

## Development

### Setup

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Run tests:
   ```bash
   poetry run pytest
   ```

3. Run linter:
   ```bash
   poetry run ruff check .
   ```

4. Run formatter:
   ```bash
   poetry run black .
   ```

### Adding New File Formats

1. Create a new generator function in `src/text2file/generators/`
2. Add validation logic in `src/text2file/validators.py` if needed
3. Register the generator in `src/text2file/__init__.py`
4. Add tests in `tests/`
5. Update documentation

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.
