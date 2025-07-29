"""Validator for PDF files."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base import BaseValidator, ValidationResult

# Try to import PyPDF2 for more thorough PDF validation
HAS_PYPDF2 = False
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    pass


class PdfValidator(BaseValidator):
    """Validator for PDF files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a PDF file.

        Args:
            file_path: Path to the PDF file to validate

        Returns:
            ValidationResult indicating whether the PDF is valid
        """
        try:
            # First check if the file exists and is readable
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    message=(
                        f"File not found: {file_path}"
                    )
                )

            if not path.is_file():
                return ValidationResult(
                    is_valid=False, message=f"Not a file: {file_path}"
                )

            # Check file extension
            if path.suffix.lower() != ".pdf":
                return ValidationResult(
                    is_valid=False, message=f"Not a PDF file: {file_path}"
                )

            # Basic PDF validation - check file header
            with open(file_path, "rb") as f:
                header = f.read(1024)

                # Check for PDF header
                if not header.startswith(b"%PDF-"):
                    return ValidationResult(
                        is_valid=False,
                        message=(
                            "File does not appear to be a valid PDF "
                            "(missing PDF header)"
                        ),
                    )

                # Check for EOF marker
                f.seek(-1024, 2)  # Go to the end of the file
                footer = f.read()
                if b"%%EOF" not in footer:
                    return ValidationResult(
                        is_valid=False,
                        message="PDF is missing EOF marker (may be corrupted)",
                    )

            # If PyPDF2 is available, do more thorough validation
            if PyPDF2:
                return cls._validate_with_pypdf2(file_path)

            # Otherwise, just do basic validation
            return ValidationResult(
                is_valid=True,
                message="File appears to be a valid PDF (basic validation only)",
                details={"size": path.stat().st_size, "validated_with": "basic"},
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating PDF file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _validate_with_pypdf2(cls, file_path: str) -> ValidationResult:
        """Validate a PDF file using PyPDF2.

        Args:
            file_path: Path to the PDF file to validate

        Returns:
            ValidationResult indicating whether the PDF is valid
        """
        try:
            with open(file_path, "rb") as f:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfReader(f)

                # Get document info
                info = {}
                if hasattr(pdf_reader, "metadata") and pdf_reader.metadata:
                    info = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "producer": pdf_reader.metadata.get("/Producer", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "keywords": pdf_reader.metadata.get("/Keywords", ""),
                        "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        "modification_date": pdf_reader.metadata.get("/ModDate", ""),
                    }

                # Get page count
                num_pages = len(pdf_reader.pages)

                # Check for encryption
                is_encrypted = pdf_reader.is_encrypted

                # Get document outline (bookmarks)
                outline = []
                if hasattr(pdf_reader, "outline") and pdf_reader.outline:
                    outline = cls._extract_outline(pdf_reader.outline)

                dimensions = ""
                if hasattr(pdf_reader.pages[0], "mediaBox"):
                    media_box = pdf_reader.pages[0].mediaBox
                    dimensions = (
                        f"{media_box.width:.1f}x{media_box.height:.1f} points"
                    )

                metadata = {
                    "size": Path(file_path).stat().st_size,
                    "page_count": num_pages,
                    "is_encrypted": is_encrypted,
                    "info": {k: v for k, v in info.items() if v},
                    "outline_count": len(outline),
                    "validated_with": "pypdf2",
                }

                return ValidationResult(
                    is_valid=True,
                    message=(
                        f"Valid PDF with {num_pages} pages "
                        f"({dimensions})"
                    ),
                    details=metadata,
                )

        except PyPDF2.PdfReadError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid PDF file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _extract_outline(
        cls,
        outline_items: List[Any],
        level: int = 0,
    ) -> List[Dict[str, Any]]:
        """Extract outline items recursively."""
        result = []
        for item in outline_items:
            if isinstance(item, list):
                # This is a nested list of outline items
                result.extend(cls._extract_outline(item, level + 1))
            elif hasattr(item, "title"):
                # This is an outline item
                outline_item = {"title": item.title, "level": level}

                # Add page number if available
                if hasattr(item, "page") and item.page is not None:
                    outline_item["page"] = item.page.number + 1  # 1-based page number

                result.append(outline_item)

                # Process any children
                if hasattr(item, "children") and item.children:
                    result.extend(cls._extract_outline(item.children, level + 1))

        return result

    @classmethod
    def get_page_count(
        cls, file_path: str
    ) -> Tuple[bool, int, str]:
        """Get the number of pages in a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Tuple of (success, page_count, message)
        """
        if not HAS_PYPDF2:
            return False, 0, "PyPDF2 is required for page count"

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                return (
                    True,
                    len(pdf_reader.pages),
                    f"PDF has {len(pdf_reader.pages)} pages",
                )
        except Exception as e:
            return False, 0, f"Error getting page count: {str(e)}"

    @classmethod
    def is_encrypted(
        cls, file_path: str
    ) -> Tuple[bool, bool, str]:
        """Check if a PDF file is encrypted.

        Args:
            file_path: Path to the PDF file

        Returns:
            Tuple of (success, is_encrypted, message)
        """
        if not HAS_PYPDF2:
            return False, False, "PyPDF2 is required for encryption check"

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                return (
                    True,
                    pdf_reader.is_encrypted,
                    "PDF is encrypted"
                    if pdf_reader.is_encrypted
                    else "PDF is not encrypted",
                )
        except Exception as e:
            return False, False, f"Error checking encryption: {str(e)}"
