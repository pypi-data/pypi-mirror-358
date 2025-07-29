"""
File validation utilities for checking the integrity of generated files.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type


@dataclass
class ValidationResult:
    """Container for validation results."""

    is_valid: bool
    message: str = ""
    details: Optional[Dict[str, Any]] = None


class FileValidator:
    """Base class for file validators."""

    @classmethod
    def validate_file(cls, file_path: str) -> ValidationResult:
        """
        Validate if the file at the given path is valid.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult containing the validation status and details
        """
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False, message=f"File does not exist: {file_path}"
            )

        if not os.path.isfile(file_path):
            return ValidationResult(
                is_valid=False, message=f"Path is not a file: {file_path}"
            )

        return cls._validate(file_path)

    @classmethod
    def _validate(cls, file_path: str) -> ValidationResult:
        """
        Implementation-specific validation logic.
        Should be overridden by subclasses.
        """
        try:
            with open(file_path, "rb") as f:
                # Basic validation: check if file can be opened and is not empty
                first_byte = f.read(1)
                if not first_byte:
                    return ValidationResult(is_valid=False, message="File is empty")
            return ValidationResult(is_valid=True, message="File is valid")
        except Exception as e:
            return ValidationResult(
                is_valid=False, message=f"Error validating file: {str(e)}"
            )


class TextFileValidator(FileValidator):
    """Validator for text files."""

    @classmethod
    def _validate(cls, file_path: str) -> ValidationResult:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Try to read the file as text with UTF-8 encoding
                content = f.read()
                # Basic validation: check if the file contains any non-printable characters
                if not all(ord(c) >= 32 or c in "\n\r\t" for c in content):
                    return ValidationResult(
                        is_valid=False, message="File contains non-printable characters"
                    )
            return ValidationResult(is_valid=True, message="Text file is valid")
        except UnicodeDecodeError:
            return ValidationResult(
                is_valid=False, message="File is not valid UTF-8 text"
            )


class ImageFileValidator(FileValidator):
    """Validator for image files."""

    @classmethod
    def _validate(cls, file_path: str) -> ValidationResult:
        try:
            import imghdr

            from PIL import Image

            # Check if file is a valid image using imghdr
            image_type = imghdr.what(file_path)
            if not image_type:
                return ValidationResult(
                    is_valid=False, message="File is not a recognized image format"
                )

            # Try to open the image with PIL to verify it's not corrupted
            try:
                with Image.open(file_path) as img:
                    img.verify()  # Verify if the file is a valid image
                return ValidationResult(
                    is_valid=True, message=f"Valid {image_type.upper()} image"
                )
            except Exception as e:
                return ValidationResult(
                    is_valid=False, message=f"Invalid image file: {str(e)}"
                )

        except ImportError:
            # Fallback to basic validation if PIL is not available
            return super()._validate(file_path)


class PDFFileValidator(FileValidator):
    """Validator for PDF files."""

    @classmethod
    def _validate(cls, file_path: str) -> ValidationResult:
        try:
            from PyPDF2 import PdfReader

            with open(file_path, "rb") as f:
                try:
                    pdf = PdfReader(f)
                    # Check if PDF is not encrypted and has at least one page
                    if pdf.is_encrypted:
                        return ValidationResult(
                            is_valid=False, message="PDF is encrypted"
                        )
                    if len(pdf.pages) == 0:
                        return ValidationResult(
                            is_valid=False, message="PDF has no pages"
                        )
                    return ValidationResult(
                        is_valid=True, message=f"Valid PDF with {len(pdf.pages)} pages"
                    )
                except Exception as e:
                    return ValidationResult(
                        is_valid=False, message=f"Invalid PDF file: {str(e)}"
                    )

        except ImportError:
            # Fallback to basic validation if PyPDF2 is not available
            return super()._validate(file_path)


# Map of file extensions to their corresponding validator classes
VALIDATORS = {
    ".txt": TextFileValidator,
    ".csv": TextFileValidator,
    ".json": TextFileValidator,
    ".xml": TextFileValidator,
    ".jpg": ImageFileValidator,
    ".jpeg": ImageFileValidator,
    ".png": ImageFileValidator,
    ".gif": ImageFileValidator,
    ".bmp": ImageFileValidator,
    ".pdf": PDFFileValidator,
}


def get_validator(file_path: str) -> Type["FileValidator"]:
    """
    Get the appropriate validator for the given file based on its extension.

    Args:
        file_path: Path to the file to validate

    Returns:
        A validator class that can validate the file
    """
    ext = os.path.splitext(file_path)[1].lower()
    return VALIDATORS.get(ext, FileValidator)


def validate_file(file_path: str) -> ValidationResult:
    """
    Validate a file using the appropriate validator.

    Args:
        file_path: Path to the file to validate

    Returns:
        ValidationResult containing the validation status and details
    """
    validator = get_validator(file_path)
    return validator.validate_file(file_path)


def cleanup_invalid_files(
    directory: str, recursive: bool = False
) -> Dict[str, ValidationResult]:
    """
    Clean up invalid files in the specified directory.

    Args:
        directory: Directory to search for files
        recursive: If True, search recursively in subdirectories

    Returns:
        Dictionary mapping file paths to their validation results
    """
    results = {}
    path = Path(directory)

    # Determine search pattern based on recursive flag
    pattern = "**/*" if recursive else "*"

    for file_path in path.glob(pattern):
        if file_path.is_file():
            result = validate_file(str(file_path))
            results[str(file_path)] = result

            # If file is invalid, delete it
            if not result.is_valid:
                try:
                    file_path.unlink()
                    result.message = f"{result.message} (deleted)"
                except Exception as e:
                    result.message = f"{result.message} (failed to delete: {str(e)})"

    return results
