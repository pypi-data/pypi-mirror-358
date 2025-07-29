"""Validators for office document formats."""

import zipfile
from pathlib import Path
from typing import Dict, List, TypeVar, Union

from .base import BaseValidator, ValidationResult

T = TypeVar("T", bound="OfficeValidator")


class OfficeValidator(BaseValidator):
    """Base validator for office document formats."""

    # Common office document MIME types
    MIME_TYPES: Dict[str, List[str]] = {
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document": [".docx"],
        "application/vnd.openxmlformats-officedocument"
        ".spreadsheetml.sheet": [".xlsx"],
        "application/vnd.openxmlformats-officedocument"
        ".presentationml.presentation": [".pptx"],
        "application/vnd.oasis.opendocument.text": [".odt"],
        "application/vnd.oasis.opendocument.spreadsheet": [".ods"],
        "application/vnd.oasis.opendocument.presentation": [".odp"],
        "application/msword": [".doc"],
        "application/vnd.ms-excel": [".xls"],
        "application/vnd.ms-powerpoint": [".ppt"],
    }

    # File extensions this validator can handle
    EXTENSIONS: List[str] = [
        ".docx",
        ".xlsx",
        ".pptx",  # Office Open XML formats
        ".odt",
        ".ods",
        ".odp",  # OpenDocument formats
        ".doc",
        ".xls",
        ".ppt",  # Legacy MS Office formats
    ]

    def __init__(self) -> None:
        """Initialize the office document validator."""
        super().__init__(self.MIME_TYPES, self.EXTENSIONS)

    def validate(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate an office document file.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        file_path = Path(file_path)

        # First, check if the file exists and is readable
        if not file_path.exists() or not file_path.is_file():
            return ValidationResult(
                valid=False,
                messages=[f"File does not exist or is not a file: {file_path}"],
            )

        # Check file extension
        ext = file_path.suffix.lower()
        if ext not in self.EXTENSIONS:
            return ValidationResult(
                valid=False, messages=[f"Unsupported office document extension: {ext}"]
            )

        # For Office Open XML formats (docx, xlsx, pptx) and ODF formats
        # (odt, ods, odp), we can validate by checking if it's a valid ZIP
        # archive with the expected structure
        if ext in (".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"):
            return self._validate_office_open_xml(file_path)

        # For legacy formats, we can only do basic validation
        return self._validate_legacy_office(file_path)

    def _validate_office_open_xml(self, file_path: Path) -> ValidationResult:
        """
        Validate Office Open XML (OOXML) or OpenDocument Format (ODF) files.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        try:
            # Check if the file is a valid ZIP archive
            if not zipfile.is_zipfile(file_path):
                return ValidationResult(
                    valid=False,
                    messages=[f"Not a ZIP archive: {file_path}"],
                )

            # Basic structure validation by checking for required files
            with zipfile.ZipFile(file_path, "r") as zf:
                file_list = zf.namelist()

                # Required files for OOXML/ODF
                required_files = {
                    ".docx": [
                        "[Content_Types].xml",
                        "word/document.xml",
                    ],
                    ".xlsx": [
                        "[Content_Types].xml",
                        "xl/workbook.xml",
                    ],
                    ".pptx": [
                        "[Content_Types].xml",
                        "ppt/presentation.xml",
                    ],
                    ".odt": [
                        "mimetype",
                        "content.xml",
                    ],
                    ".ods": [
                        "mimetype",
                        "content.xml",
                    ],
                    ".odp": [
                        "mimetype",
                        "content.xml",
                    ],
                }

                ext = file_path.suffix.lower()
                if ext in required_files:
                    for req_file in required_files[ext]:
                        if req_file not in file_list:
                            # Check for case-insensitive match (some ODF files might have different case)
                            if not any(
                                f.lower() == req_file.lower() for f in file_list
                            ):
                                msg = (
                                    f"Missing required file in {ext} "
                                    f"archive: {req_file}"
                                )
                                return ValidationResult(
                                    valid=False,
                                    messages=[msg]
                                )

            return ValidationResult(valid=True)

        except Exception as e:
            error_msg = (
                f"Error validating office document {file_path}: {str(e)}"
            )
            return ValidationResult(valid=False, messages=[error_msg])

    def _validate_legacy_office(self, file_path: Path) -> ValidationResult:
        """
        Perform basic validation for legacy MS Office formats.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        # For legacy formats, we can only check if the file is not empty
        # and has the correct extension
        try:
            if file_path.stat().st_size == 0:
                return ValidationResult(
                    valid=False, messages=[f"File is empty: {file_path}"]
                )

            # Check if the file starts with the expected signature
            # This is a very basic check and not foolproof
            with open(file_path, "rb") as f:
                header = f.read(8)

                # Check for OLE Compound File format (used by legacy Office formats)
                if header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
                    return ValidationResult(valid=True)

                # Check for OOXML/ODF files with wrong extension
                if header.startswith(b"PK\x03\x04"):
                    return ValidationResult(
                        valid=False,
                        messages=[
                            f"File appears to be an OOXML/ODF file with wrong extension: {file_path}"
                        ],
                    )

                return ValidationResult(
                    valid=False,
                    messages=[f"Invalid office document: {file_path}"]
                )

        except Exception as e:
            return ValidationResult(
                valid=False,
                messages=[
                    f"Error validating legacy office document {file_path}: {str(e)}"
                ],
            )

    def _check_legacy_office(
        self, file_path: Path
    ) -> ValidationResult:
        """Check if the file is a valid legacy office document."""
        try:
            # Legacy office files have a specific header
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                    return ValidationResult(
                        is_valid=True,
                        message=(
                            f"Valid legacy office document: "
                            f"{file_path.suffix}"
                        )
                    )
                return ValidationResult(
                    is_valid=False,
                    message="Not a valid legacy office document"
                )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=(
                    f"Error validating legacy office document {file_path}: {str(e)}"
                )
            )


class DocxValidator(OfficeValidator):
    """Validator for DOCX files."""
    
    MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
            ".docx"
        ],
    }
    EXTENSIONS = [".docx"]


class XlsxValidator(OfficeValidator):
    """Validator for XLSX files."""
    
    MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
            ".xlsx"
        ],
    }
    EXTENSIONS = [".xlsx"]


class PptxValidator(OfficeValidator):
    """Validator for PPTX files."""
    
    MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument"
        ".presentationml.presentation": [".pptx"],
    }
    EXTENSIONS = [".pptx"]


class OdtValidator(OfficeValidator):
    """Validator for ODT files."""

    MIME_TYPES = {
        "application/vnd.oasis.opendocument.text": [".odt"],
    }
    EXTENSIONS = [".odt"]


class OdsValidator(OfficeValidator):
    """Validator for ODS files."""

    MIME_TYPES = {
        "application/vnd.oasis.opendocument.spreadsheet": [".ods"],
    }
    EXTENSIONS = [".ods"]


class OdpValidator(OfficeValidator):
    """Validator for ODP files."""

    MIME_TYPES = {
        "application/vnd.oasis.opendocument.presentation": [".odp"],
    }
    EXTENSIONS = [".odp"]


# Legacy MS Office validators
class DocValidator(OfficeValidator):
    """Validator for legacy DOC files."""

    MIME_TYPES = {
        "application/msword": [".doc"],
    }
    EXTENSIONS = [".doc"]


class XlsValidator(OfficeValidator):
    """Validator for legacy XLS files."""

    MIME_TYPES = {
        "application/vnd.ms-excel": [".xls"],
    }
    EXTENSIONS = [".xls"]


class PptValidator(OfficeValidator):
    """Validator for legacy PPT files."""

    MIME_TYPES = {
        "application/vnd.ms-powerpoint": [".ppt"],
    }
    EXTENSIONS = [".ppt"]
