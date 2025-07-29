"""Base validator class for file validation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T", bound="ValidationResult")


@dataclass
class ValidationResult:
    """Result of a file validation operation."""

    is_valid: bool
    message: str
    details: Optional[Dict[str, Any]] = None

    def __bool__(self) -> bool:
        return self.is_valid


class BaseValidator(ABC):
    """Abstract base class for all file validators."""

    @classmethod
    @abstractmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate the given file.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid and any details
        """
        raise NotImplementedError("Subclasses must implement validate()")

    @classmethod
    def is_valid(cls, file_path: str) -> bool:
        """Check if the given file is valid.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if the file is valid, False otherwise
        """
        return bool(cls.validate(file_path))


def get_validator(file_path: str) -> Type[BaseValidator]:
    """Get the appropriate validator for the given file based on its extension.

    Args:
        file_path: Path to the file to validate

    Returns:
        A validator class that can validate the file
    """
    from ..generators import get_generator
    from . import (  # Import validators here to avoid circular imports
        archive_validator,
        image_validator,
        office_validator,
        pdf_validator,
        text_validator,
        video_validator,
    )

    # Map file extensions to their validators
    validators = {
        # Text files
        "txt": text_validator.TextFileValidator,
        "md": text_validator.TextFileValidator,
        "html": text_validator.HtmlFileValidator,
        "css": text_validator.CssFileValidator,
        "js": text_validator.JavaScriptFileValidator,
        "py": text_validator.PythonFileValidator,
        "json": text_validator.JsonFileValidator,
        "csv": text_validator.CsvFileValidator,
        "xml": text_validator.XmlFileValidator,
        "yaml": text_validator.YamlFileValidator,
        "yml": text_validator.YamlFileValidator,
        # Images
        "jpg": image_validator.JpegValidator,
        "jpeg": image_validator.JpegValidator,
        "png": image_validator.PngValidator,
        "gif": image_validator.GifValidator,
        "bmp": image_validator.BmpValidator,
        "webp": image_validator.WebPValidator,
        "svg": image_validator.SvgValidator,
        # Archives
        "zip": archive_validator.ZipValidator,
        "tar": archive_validator.TarValidator,
        "tar.gz": archive_validator.TarGzValidator,
        "tgz": archive_validator.TarGzValidator,
        "tar.bz2": archive_validator.TarBz2Validator,
        "tbz2": archive_validator.TarBz2Validator,
        # Office
        "pdf": pdf_validator.PdfValidator,
        "docx": office_validator.DocxValidator,
        "xlsx": office_validator.XlsxValidator,
        "pptx": office_validator.PptxValidator,
        "odt": office_validator.OdtValidator,
        "ods": office_validator.OdsValidator,
        "odp": office_validator.OdpValidator,
        # Video
        "mp4": video_validator.Mp4Validator,
        "avi": video_validator.AviValidator,
        "mov": video_validator.MovValidator,
        "mkv": video_validator.MkvValidator,
        "webm": video_validator.WebmValidator,
    }

    # Get the file extension
    ext = Path(file_path).suffix.lstrip(".").lower()

    # Handle double extensions like .tar.gz
    if ext in ["gz", "bz2"] and len(parts := Path(file_path).suffixes) > 1:
        ext = f"{parts[-2].lstrip('.')}{parts[-1]}"

    # Return the appropriate validator or the base validator if not found
    return validators.get(ext, BaseValidator)
