"""File generators and validators for different file formats."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .registration import GeneratorFunc
from .registration import get_generator as _get_generator
from .registration import get_supported_extensions, register_generator
from .validators import (
    FileValidator,
    ImageFileValidator,
    PDFFileValidator,
    TextFileValidator,
    ValidationResult,
    cleanup_invalid_files,
)
from .validators import get_validator as _get_validator
from .validators import validate_file

# Re-export registration functions
register_generator = register_generator
get_generator = _get_generator

# Make SUPPORTED_EXTENSIONS a function call to get the latest set of extensions
def SUPPORTED_EXTENSIONS():
    return get_supported_extensions()


# Re-export get_validator from validators module
get_validator = _get_validator

# Export validation functions and types
__all__ = [
    "FileValidator",
    "TextFileValidator",
    "ImageFileValidator",
    "PDFFileValidator",
    "ValidationResult",
    "cleanup_invalid_files",
    "generate_file",
    "get_generator",
    "get_validator",
    "register_generator",
    "validate_file",
    "GeneratorFunc",
    "SUPPORTED_EXTENSIONS",
]  # ImageSetGenerator will be added after import


# Module-level constant for default output directory
_DEFAULT_OUTPUT_DIR = Path.cwd()


def generate_file(
    content: str,
    extension: str,
    output_dir: Optional[Path] = None,
    prefix: str = "generated",
) -> Path:
    """Generate a file with the given content and extension.

    Args:
        content: Text content to include in the file
        extension: File extension (with or without leading dot)
        output_dir: Directory to save the file in
        prefix: Prefix for the generated filename

    Returns:
        Path to the generated file

    Raises:
        ValueError: If no generator is found for the extension
        IOError: If there's an error writing the file
    """
    # Get the generator function for the extension
    generator = get_generator(extension)
    if generator is None:
        raise ValueError(f"No generator found for extension: {extension}")

    # Use default output directory if none provided
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    else:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension.lstrip('.')}"
    output_path = output_dir / filename

    try:
        # Call the generator function
        generated_path = generator(content, output_path)
        return generated_path
    except Exception as e:
        # Clean up partially created files
        if output_path.exists():
            output_path.unlink()
        raise IOError(f"Error generating {extension} file: {str(e)}") from e


# Import and register all generators
try:
    # Force reload of supported extensions after all generators are registered
    def get_supported_extensions_with_reload():
        return get_supported_extensions()

    # Import text generator first
    from .text import generate_text_file

    register_generator(["txt", "md", "html", "css", "js", "py", "json", "csv"])(
        generate_text_file
    )

    # Import and register archive generators
    from .archives import generate_zip_file, generate_tar_file

    # Register each archive type with its specific generator
    register_generator(["zip"])(generate_zip_file)
    register_generator(["tar"])(generate_tar_file)
    register_generator(["tar.gz", "tgz"])(generate_tar_file)

    # Import and register SVG generator
    from .image.svg_generator import generate_svg

    register_generator(["svg"])(generate_svg)

    # Import and register PDF generator
    from .pdf import generate_pdf_file

    register_generator(["pdf"])(generate_pdf_file)
    
    # Import and register config generator
    from .config import ConfigGenerator
    
    # Note: ConfigGenerator is registered directly in the config.py module: F401, F403
    from .image import *  # noqa: F401, F403

    # Lazy import of PDF generator to avoid circular imports
    from .image_set import ImageSetGenerator  # noqa: F401
    from .office import *  # noqa: F401, F403
    from .video import *  # noqa: F401, F403
    
    # Import and register Excel generator
    try:
        from .excel import register as register_excel_generator
        register_excel_generator()
    except ImportError as e:
        print(f"Warning: Excel generation not available: {e}", file=sys.stderr)  # noqa: T201

    # Add ImageSetGenerator to __all__
    __all__.append("ImageSetGenerator")

except ImportError as e:
    print(f"Error importing generators: {e}", file=sys.stderr)  # noqa: T201
    raise
